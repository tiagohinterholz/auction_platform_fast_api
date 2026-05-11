from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database.session import get_db
from app.core.security.jwt_service import JWTService
from app.core.security.password_service import PasswordService
from app.modules.auth.infrastructure.repository.refresh_token_repository import RefreshTokenRepository
from app.modules.users.infrastructure.repository.users_repository import UserRepository
from app.modules.users.routers.dependencies import get_user_repository
from app.modules.auth.application.usecases.register_use_case import RegisterUseCase
from app.modules.auth.application.usecases.login_use_case import LoginUseCase
from app.modules.auth.application.usecases.refresh_use_case import RefreshTokenUseCase
from app.modules.auth.application.usecases.logout_use_case import LogoutUseCase
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_jwt_service = JWTService()
_password_service = PasswordService()


def get_jwt_service() -> JWTService:
    return _jwt_service


def get_password_service() -> PasswordService:
    return _password_service


def get_refresh_token_repository(
    session: AsyncSession = Depends(get_db),
) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


def get_register_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    refresh_token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> RegisterUseCase:
    return RegisterUseCase(user_repo, _password_service, _jwt_service, refresh_token_repo)


def get_login_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    refresh_token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> LoginUseCase:
    return LoginUseCase(user_repo, _password_service, _jwt_service, refresh_token_repo)


def get_refresh_use_case(
    refresh_token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(refresh_token_repo, _jwt_service, _password_service)


def get_logout_use_case(
    refresh_token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> LogoutUseCase:
    return LogoutUseCase(refresh_token_repo)


def get_current_jti(
    token: str = Depends(oauth2_scheme),
) -> str:
    try:
        payload = _jwt_service.decode_access_token(token)
        return payload["jti"]
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
