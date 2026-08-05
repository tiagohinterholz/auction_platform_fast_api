from abc import ABC, abstractmethod
from datetime import timedelta
from uuid import UUID


class IJWTService(ABC):
    @abstractmethod
    def create_access_token(
        self, 
        subject: UUID,
        expires_delta: timedelta | None = None,  
        name: str | None = None,
        email: str | None = None,
        role: str | None = None
    ) -> str:
        pass

    @abstractmethod
    def create_refresh_token(
        self,
        subject: UUID,
        expires_delta: timedelta | None = None,
        name: str | None = None,
        email: str | None = None,
        role: str | None = None
    ) -> tuple[str, str]:
        pass

    @abstractmethod
    def decode_access_token(self, token: str) -> dict:
        pass

    @abstractmethod
    def decode_refresh_token(self, token: str) -> dict:
        pass