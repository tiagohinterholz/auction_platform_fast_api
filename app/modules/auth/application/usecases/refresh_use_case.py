import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.modules.auth.domain.ports.jwt_service_interface import IJWTService
from app.modules.auth.domain.ports.refresh_token_repository_interface import IRefreshTokenRepository
from app.modules.auth.domain.entities.refresh_tokel_entity import RefreshTokenEntity
from app.modules.auth.domain.exceptions.auth_exceptions import TokenRevokedException
from app.core.config import settings


class RefreshTokenUseCase:
    def __init__(
        self,
        refresh_token_repository: IRefreshTokenRepository,
        jwt_service: IJWTService,
    ):
        self.refresh_token_repository = refresh_token_repository
        self.jwt_service = jwt_service

    async def execute(self, refresh_token: str) -> dict:
        payload = self.jwt_service.decode_refresh_token(refresh_token)
        jti: str = payload["jti"]
        user_id: UUID = UUID(payload["sub"])

        stored_token = await self.refresh_token_repository.find_by_jti(jti)

        if not stored_token or stored_token.revoked_at is not None:
            raise TokenRevokedException()

        await self.refresh_token_repository.revoke(jti)

        name = payload.get("name")
        email = payload.get("email")
        role = payload.get("role")

        new_access_token = self.jwt_service.create_access_token(
            subject=user_id, name=name, email=email, role=role
        )
        new_refresh_token, new_jti = self.jwt_service.create_refresh_token(
            subject=user_id, name=name, email=email, role=role
        )

        token_model = RefreshTokenEntity(
            id=uuid.uuid4(),
            jti=new_jti,
            user_id=user_id,
            token_hash=hashlib.sha256(new_refresh_token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self.refresh_token_repository.save(token_model)

        return {"access_token": new_access_token, "refresh_token": new_refresh_token}
