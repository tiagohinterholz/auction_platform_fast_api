from typing import List, Callable


class EventBusInterface:
    async def publish(self, events: List) -> None:
        pass

    async def subscribe(self, event_name: str, handler: Callable) -> None:
        pass
