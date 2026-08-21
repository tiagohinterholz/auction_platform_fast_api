from abc import ABC, abstractmethod


class IEmailService(ABC):
    @abstractmethod
    async def send(self, to: str, subject: str, body: str) -> None:
        pass
