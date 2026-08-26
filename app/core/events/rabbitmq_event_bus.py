import asyncio
import json
import logging
from collections.abc import Callable
from types import SimpleNamespace

import aio_pika

from app.core.config import settings
from app.core.events.event_bus_interface import EventBusInterface

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "domain_events"
CONNECT_MAX_ATTEMPTS = 10
CONNECT_RETRY_DELAY_SECONDS = 3


class RabbitMQEventBus(EventBusInterface):
    def __init__(self, url: str = settings.RABBITMQ_URL):
        self._url = url
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def _connect(self) -> aio_pika.abc.AbstractRobustConnection:
        last_error: Exception | None = None
        for attempt in range(1, CONNECT_MAX_ATTEMPTS + 1):
            try:
                return await aio_pika.connect_robust(self._url)
            except Exception as exc:
                last_error = exc
                if attempt == CONNECT_MAX_ATTEMPTS:
                    break
                logger.warning(
                    f"RabbitMQ connect attempt {attempt}/{CONNECT_MAX_ATTEMPTS} failed "
                    f"({exc}); retrying in {CONNECT_RETRY_DELAY_SECONDS}s"
                )
                await asyncio.sleep(CONNECT_RETRY_DELAY_SECONDS)
        assert last_error is not None
        raise last_error

    async def _get_exchange(self) -> aio_pika.abc.AbstractExchange:
        if (
            self._exchange is not None
            and self._connection is not None
            and not self._connection.is_closed
        ):
            return self._exchange

        self._connection = await self._connect()
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
