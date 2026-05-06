from typing import List, Callable
from abc import ABC, abstractmethod


class EventBusInterface(ABC):

    @abstractmethod
    async def publish(self, events: List) -> None:
        pass

    @abstractmethod
    async def subscribe(self, event_name: str, handler: Callable) -> None:
        pass
