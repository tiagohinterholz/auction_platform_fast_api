import json
from collections.abc import Callable
from types import SimpleNamespace

import aio_pika

from app.core.config import settings
from app.core.events.event_bus_interface import EventBusInterface

EXCHANGE_NAME = "domain_events"


class RabbitMQEventBus(EventBusInterface):
    def __init__(self, url: str = settings.RABBITMQ_URL):
        self._url = url
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def _get_exchange(self) -> aio_pika.abc.AbstractExchange:
        # A cached connection/channel is only safe to reuse within the same
        # event loop that created it. Celery tasks each run their own
        # asyncio.run() — a brand-new loop every call — so a connection
        # opened by an earlier task is already closed by the time a later
        # task (same process, same RabbitMQEventBus instance) reaches here.
        # Detect that and reconnect instead of handing back a dead exchange.
        if (
            self._exchange is not None
            and self._connection is not None
            and not self._connection.is_closed
        ):
            return self._exchange

        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
        )
        return self._exchange

    async def publish(self, events: list) -> None:
        exchange = await self._get_exchange()

        for event in events:
            message = aio_pika.Message(
                body=event.model_dump_json().encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # survives a broker restart too
            )
            await exchange.publish(message, routing_key=type(event).__name__)

    async def subscribe(self, event_name: str, handler: Callable) -> None:
        exchange = await self._get_exchange()
        channel = self._channel
        assert channel is not None

        # AMQP queue names only allow [a-zA-Z0-9-_.:@#,/+ ] — a closure's
        # __qualname__ (e.g. "wire_event_handlers.<locals>.on_auction_created")
        # has <> in it, which RabbitMQ rejects outright.
        safe_qualname = handler.__qualname__.replace("<locals>", "locals")
        queue_name = f"{EXCHANGE_NAME}.{event_name}.{safe_qualname}"
        queue = await channel.declare_queue(queue_name, durable=True)
        await queue.bind(exchange, routing_key=event_name)

        async def _on_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
            async with message.process():
                data = json.loads(message.body)
                event = SimpleNamespace(name=data.get("name"), payload=data["payload"])
                await handler(event)

        await queue.consume(_on_message)

    async def close(self) -> None:
        """Only needed by short-lived callers that create their own
        RabbitMQEventBus instance for a single publish and must not leak the
        connection afterwards (e.g. a Celery task — see auction_tasks.py).
        Long-lived callers like main.py's module-level event_bus never call
        this; the connection stays open for the process's lifetime.
        """
        if self._connection is not None:
            await self._connection.close()
