from app.modules.auction.domain.ports.event_bus_interface import EventBusInterface
from typing import List, Callable


class DummyEventBus(EventBusInterface):
    async def publish(self, events: List) -> None:
        for event in events:
            print(f"Publicando evento: {event}")

    async def subscribe(self, event_name: str, handler: Callable) -> None:
        pass
