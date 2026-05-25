import uuid
import hashlib
from datetime import datetime, timedelta, timezone

from app.modules.auth.domain.exceptions.auth_exceptions import InvalidCredentialsException
from app.modules.auth.domain.ports.jwt_service_interface import IJWTService
from app.modules.auth.domain.ports.password_service_interface import IPasswordService
from app.modules.auth.domain.ports.refresh_token_repository_interface import IRefreshTokenRepository
from app.modules.auth.domain.entities.refresh_tokel_entity import RefreshTokenEntity
from app.modules.users.domain.ports.users_repository_interface import IUsersRepository
from app.core.config import settings


class LoginUseCase:
    def __init__(
        self,
        user_repository: IUsersRepository,
        password_service: IPasswordService,
        jwt_service: IJWTService,
        refresh_token_repository: IRefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.jwt_service = jwt_service
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, email: str, password: str) -> dict:
        user = await self.user_repository.get_by_email(email)

        if not user:
            raise InvalidCredentialsException()

        if not self.password_service.verify_password(password, user.password_hash):
            raise InvalidCredentialsException()

        access_token = self.jwt_service.create_access_token(
            subject=user.id, name=user.name, email=user.email, role=user.role
        )
        refresh_token, jti = self.jwt_service.create_refresh_token(
            subject=user.id, name=user.name, email=user.email, role=user.role
        )

        token_model = RefreshTokenEntity(
            id=uuid.uuid4(),
            jti=jti,
            user_id=user.id,
            token_hash=hashlib.sha256(refresh_token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self.refresh_token_repository.save(token_model)

        return {"access_token": access_token, "refresh_token": refresh_token}
