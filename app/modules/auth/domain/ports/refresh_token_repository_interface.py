from abc import ABC, abstractmethod

from app.modules.auth.domain.entities.refresh_tokel_entity import RefreshTokenEntity


class IRefreshTokenRepository(ABC):
    @abstractmethod
    async def save(self, token: RefreshTokenEntity) -> None:
        pass
    @abstractmethod
    async def find_by_jti(self, jti: str) -> RefreshTokenEntity | None:
        pass
    @abstractmethod
    async def revoke(self, jti: str) -> None:
        pass