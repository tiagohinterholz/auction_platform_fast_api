import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from app.core.config import settings
from app.modules.auth.domain.entities.refresh_token_entity import RefreshTokenEntity
from app.modules.auth.domain.exceptions.auth_exceptions import EmailAlreadyRegisteredException
from app.modules.auth.domain.ports.jwt_service_interface import IJWTService
from app.modules.auth.domain.ports.password_service_interface import IPasswordService
from app.modules.auth.domain.ports.refresh_token_repository_interface import IRefreshTokenRepository
from app.modules.users.domain.enums.user_role import UserRole
from app.modules.users.domain.ports.users_repository_interface import IUsersRepository
from app.modules.users.domain.users_aggregate import User


class RegisterUseCase:
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

    async def execute(self, name: str, email: str, password: str, cpf: str) -> dict:
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise EmailAlreadyRegisteredException()

        hashed_password = self.password_service.hash_password(password)

        user = User.create(
            name=name,
            email=email,
            password_hash=hashed_password,
            cpf=cpf,
            role=UserRole.USER,
        )

        await self.user_repository.save(user)

        access_token = self.jwt_service.create_access_token(
            subject=user.id, name=user.name, email=user.email, role=user.role.value
        )
        refresh_token, jti = self.jwt_service.create_refresh_token(
            subject=user.id, name=user.name, email=user.email, role=user.role.value
        )

        token_model = RefreshTokenEntity(
            id=uuid.uuid4(),
            jti=jti,
            user_id=user.id,
            token_hash=hashlib.sha256(refresh_token.encode()).hexdigest(),
            expires_at=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self.refresh_token_repository.save(token_model)

        return {"access_token": access_token, "refresh_token": refresh_token}
