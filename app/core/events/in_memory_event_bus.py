from asyncio.log import logger
from collections.abc import Callable

from app.core.events.event_bus_interface import EventBusInterface


class InMemoryEventBus(EventBusInterface):
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}

    def subscribe(self, event_name: str, handler: Callable) -> None:
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