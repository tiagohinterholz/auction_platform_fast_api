from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db
from app.modules.users.application.usecases.delete_user_usecase import DeleteUserUseCase
from app.modules.users.application.usecases.get_all_users_usecase import (
    GetAllUsersUseCase,
)
from app.modules.users.application.usecases.get_user_by_id_usecase import (
    GetUserByIdUseCase,
)
from app.modules.users.application.usecases.update_user_usecase import UpdateUserUseCase
from app.modules.users.infrastructure.repository.users_repository import UserRepository


def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    return UserRepository(session)


def get_delete_user_use_case(
    repo: UserRepository = Depends(get_user_repository),
) -> DeleteUserUseCase:
    return DeleteUserUseCase(repo)


def get_user_by_id_use_case(
    repo: UserRepository = Depends(get_user_repository),
) -> GetUserByIdUseCase:
    return GetUserByIdUseCase(repo)


def get_all_users_use_case(
    repo: UserRepository = Depends(get_user_repository),
) -> GetAllUsersUseCase:
    return GetAllUsersUseCase(repo)


def get_update_user_use_case(
    repo: UserRepository = Depends(get_user_repository),
) -> UpdateUserUseCase:
    return UpdateUserUseCase(repo)
