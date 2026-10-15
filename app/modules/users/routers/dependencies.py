from typing import Annotated

from fastapi import Depends

from app.core.database.session import SessionDep
from app.core.events.dependencies import EventBusDep
from app.modules.users.application.usecases.delete_user_usecase import DeleteUserUseCase
from app.modules.users.application.usecases.get_all_users_usecase import (
    GetAllUsersUseCase,
)
from app.modules.users.application.usecases.get_user_by_id_usecase import (
    GetUserByIdUseCase,
)
from app.modules.users.application.usecases.update_user_usecase import UpdateUserUseCase
from app.modules.users.infrastructure.repository.users_repository import UserRepository


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_delete_user_use_case(
    repo: UserRepositoryDep,
    event_bus: EventBusDep,
) -> DeleteUserUseCase:
    return DeleteUserUseCase(repo, event_bus)


def get_user_by_id_use_case(repo: UserRepositoryDep) -> GetUserByIdUseCase:
    return GetUserByIdUseCase(repo)


def get_all_users_use_case(repo: UserRepositoryDep) -> GetAllUsersUseCase:
    return GetAllUsersUseCase(repo)


def get_update_user_use_case(
    repo: UserRepositoryDep,
    event_bus: EventBusDep,
) -> UpdateUserUseCase:
    return UpdateUserUseCase(repo, event_bus)


DeleteUserUseCaseDep = Annotated[DeleteUserUseCase, Depends(get_delete_user_use_case)]
GetUserByIdUseCaseDep = Annotated[GetUserByIdUseCase, Depends(get_user_by_id_use_case)]
GetAllUsersUseCaseDep = Annotated[GetAllUsersUseCase, Depends(get_all_users_use_case)]
UpdateUserUseCaseDep = Annotated[UpdateUserUseCase, Depends(get_update_user_use_case)]
