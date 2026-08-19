from abc import ABC, abstractmethod


class ILockService(ABC):
    @abstractmethod
    async def acquire(self, key: str, ttl_ms: int) -> bool: ...
    @abstractmethod
    async def release(self, key: str) -> None: ...
