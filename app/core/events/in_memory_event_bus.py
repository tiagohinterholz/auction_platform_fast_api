from asyncio.log import logger
from collections.abc import Callable

from app.core.events.event_bus_interface import EventBusInterface


class InMemoryEventBus(EventBusInterface):
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}

    async def subscribe(
        self, event_name: str, handler: Callable, broadcast: bool = False
    ) -> None:
        # `broadcast` only matters when there's more than one OS process
        # subscribing to the same queue (RabbitMQEventBus, across uvicorn
        # workers). InMemoryEventBus only ever exists within a single
        # process/test, so every handler already gets called directly -
        # there's nothing "broadcast" would change here.
        handlers = self._handlers.get(event_name, [])
        handlers.append(handler)
        self._handlers[event_name] = handlers

    async def publish(self, events: list) -> None:
        for event in events:
            event_name = type(event).__name__
            handlers = self._handlers.get(event_name, [])
            for handler in handlers:
                try:
                    await handler(event)
                except Exception:
                    logger.exception(f"Handler {handler} failed for event {event_name}")