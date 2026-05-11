from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone

from app.modules.auth.domain.ports.refresh_token_repository_interface import IRefreshTokenRepository
from app.modules.auth.domain.entities.refresh_tokel_entity import RefreshTokenEntity
from app.modules.auth.infrastructure.persistence.refresh_token_model import RefreshTokenModel


class RefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_model(self, entity: RefreshTokenEntity) -> RefreshTokenModel:
        return RefreshTokenModel(
            id=entity.id,
            jti=entity.jti,
            user_id=entity.user_id,
            token_hash=entity.token_hash,
            expires_at=entity.expires_at,
            revoked_at=entity.revoked_at,
        )

    def _to_entity(self, model: RefreshTokenModel) -> RefreshTokenEntity:
        return RefreshTokenEntity(
            id=model.id,
            jti=model.jti,
            user_id=model.user_id,
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
        )

    async def save(self, token: RefreshTokenEntity) -> None:
        self.session.add(self._to_model(token))
        await self.session.commit()

    async def find_by_jti(self, jti: str) -> RefreshTokenEntity | None:
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.jti == jti)
        )
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def revoke(self, jti: str) -> None:
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.jti == jti)
        )
        model = result.scalars().first()
        if model:
            model.revoked_at = datetime.now(timezone.utc)
            await self.session.commit()
