from typing import Annotated

from fastapi import Depends

from app.core.database.session import SessionDep
from app.core.events.dependencies import EventBusDep
from app.core.security.jwt_service import JWTService
from app.core.security.password_service import PasswordService
from app.modules.auth.application.usecases.login_use_case import LoginUseCase
from app.modules.auth.application.usecases.logout_use_case import LogoutUseCase
from app.modules.auth.application.usecases.refresh_use_case import RefreshTokenUseCase
from app.modules.auth.application.usecases.register_use_case import RegisterUseCase
from app.modules.auth.infrastructure.repository.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.modules.users.routers.dependencies import UserRepositoryDep

_jwt_service = JWTService()
_password_service = PasswordService()


def get_jwt_service() -> JWTService:
    return _jwt_service


def get_password_service() -> PasswordService:
    return _password_service


def get_refresh_token_repository(session: SessionDep) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


RefreshTokenRepositoryDep = Annotated[
    RefreshTokenRepository, Depends(get_refresh_token_repository)
]


def get_register_use_case(
    user_repo: UserRepositoryDep,
    refresh_token_repo: RefreshTokenRepositoryDep,
    event_bus: EventBusDep,
) -> RegisterUseCase:
    return RegisterUseCase(
        user_repo, _password_service, _jwt_service, refresh_token_repo, event_bus
    )


def get_login_use_case(
    user_repo: UserRepositoryDep,
    refresh_token_repo: RefreshTokenRepositoryDep,
) -> LoginUseCase:
    return LoginUseCase(user_repo, _password_service, _jwt_service, refresh_token_repo)


def get_refresh_use_case(
    refresh_token_repo: RefreshTokenRepositoryDep,
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(refresh_token_repo, _jwt_service)


def get_logout_use_case(
    refresh_token_repo: RefreshTokenRepositoryDep,
) -> LogoutUseCase:
    return LogoutUseCase(refresh_token_repo, _jwt_service)


RegisterUseCaseDep = Annotated[RegisterUseCase, Depends(get_register_use_case)]
LoginUseCaseDep = Annotated[LoginUseCase, Depends(get_login_use_case)]
RefreshTokenUseCaseDep = Annotated[RefreshTokenUseCase, Depends(get_refresh_use_case)]
LogoutUseCaseDep = Annotated[LogoutUseCase, Depends(get_logout_use_case)]
