from abc import ABC, abstractmethod
from app.modules.auth.infrastructure.persistence.refresh_token_model import RefreshTokenModel


class IRefreshRespository(ABC):
    @abstractmethod
    async def save(self, token: RefreshTokenModel) -> None:
        pass
    @abstractmethod
    async def find_by_jti(self, jti: str) -> RefreshTokenModel | None:
        pass
    @abstractmethod
    async def revoke(self, jti: str) -> None:
        pass