import asyncio
import json
import logging
from collections.abc import Callable
from types import SimpleNamespace

import aio_pika
from opentelemetry import propagate, trace
from opentelemetry.trace import SpanKind

from app.core.config import settings
from app.core.events.event_bus_interface import EventBusInterface

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

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
            event_name = type(event).__name__

            # RabbitMQ has no built-in way to carry an OTel trace context the
            # way HTTP headers or Celery's own task headers do — aio-pika
            # gives us a plain dict of AMQP message headers, so that's where
            # we manually stash it. `propagate.inject` reads whatever span is
            # currently active (e.g. the HTTP request span that triggered
            # this publish) and writes the W3C `traceparent` string into the
            # dict we hand it.
            headers: dict = {}
            with tracer.start_as_current_span(
                f"{event_name} publish",
                kind=SpanKind.PRODUCER,
                attributes={"messaging.system": "rabbitmq", "messaging.destination": event_name},
            ):
                propagate.inject(headers)

                message = aio_pika.Message(
                    body=event.model_dump_json().encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # survives a broker restart too
                    headers=headers,
                )
                await exchange.publish(message, routing_key=event_name)

    async def subscribe(
        self, event_name: str, handler: Callable, broadcast: bool = False
    ) -> None:
        exchange = await self._get_exchange()
        channel = self._channel
        assert channel is not None

        # AMQP queue names only allow [a-zA-Z0-9-_.:@#,/+ ] — a closure's
        # __qualname__ (e.g. "wire_event_handlers.<locals>.on_auction_created")
        # has <> in it, which RabbitMQ rejects outright. Also used below to
        # name this handler's span, regardless of which queue type it gets.
        safe_qualname = handler.__qualname__.replace("<locals>", "locals")

        if broadcast:
            # No name, exclusive, auto_delete: RabbitMQ generates a unique
            # queue for THIS connection alone, and deletes it the moment
            # this connection closes. With uvicorn --workers N, each worker
            # process holds its own RabbitMQEventBus/connection, so each one
            # ends up with its own private queue bound to the same routing
            # key - every worker gets its own copy of every matching event,
            # instead of the message going to a single, arbitrarily-picked
            # worker. Needed by handlers whose effect depends on per-process
            # state (WebSocket connections held only in this process's
            # ConnectionManager) - see EventBusInterface.subscribe's
            # docstring for the full "why".
            queue = await channel.declare_queue(exclusive=True, auto_delete=True)
        else:
            # Durable, fixed name shared by every subscriber process: this
            # is RabbitMQ's normal competing-consumers behavior, where each
            # matching event goes to exactly ONE of the bound queues/workers
            # - correct for handlers that write to the DB, where two workers
            # both processing the same event would double the write.
            queue_name = f"{EXCHANGE_NAME}.{event_name}.{safe_qualname}"
            queue = await channel.declare_queue(queue_name, durable=True)

        await queue.bind(exchange, routing_key=event_name)

        async def _on_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
            async with message.process():
                # Mirror of publish()'s inject: `extract` reads the
                # `traceparent` string back out of the AMQP headers and
                # rebuilds a SpanContext from it. Passing that as `context=`
                # to start_as_current_span is what makes this new span a
                # CHILD of the original publisher's span instead of the
                # start of a brand new, disconnected trace — this is the
                # actual link between the API process and the worker process.
                ctx = propagate.extract(message.headers or {})
                data = json.loads(message.body)
                event = SimpleNamespace(name=data.get("name"), payload=data["payload"])

                with tracer.start_as_current_span(
                    f"{event_name} handle ({safe_qualname})",
                    context=ctx,
                    kind=SpanKind.CONSUMER,
                    attributes={
                        "messaging.system": "rabbitmq",
                        "messaging.destination": event_name,
                    },
                ):
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
