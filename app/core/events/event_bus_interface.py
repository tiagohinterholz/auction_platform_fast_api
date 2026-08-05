from abc import ABC, abstractmethod
from collections.abc import Callable


class EventBusInterface(ABC):

    @abstractmethod
    async def publish(self, events: list) -> None:
        pass

    @abstractmethod
    def subscribe(self, event_name: str, handler: Callable) -> None:
        pass
