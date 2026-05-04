from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database.session import get_db

from app.modules.users.infrastructure.repository.users_repository import UserRepository
from app.modules.users.application.usecases.create_user_usecase import CreateUserUseCase
from app.modules.users.application.usecases.delete_user_usecase import DeleteUserUseCase
from app.modules.users.application.usecases.get_user_by_id_usecase import (
    GetUserByIdUseCase,
)
from app.modules.users.application.usecases.get_all_users_usecase import (
    GetAllUsersUseCase,
)
from app.modules.users.application.usecases.update_user_usecase import UpdateUserUseCase
from app.modules.users.application.schemas.create_user_schema import CreateUserSchema
from app.modules.users.application.schemas.update_user_schema import UpdateUserSchema

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    return UserRepository(session)


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(
    id: uuid.UUID,
    repository: UserRepository = Depends(get_user_repository),
):
    usecase = GetUserByIdUseCase(repository)
    user = await usecase.execute(str(id))
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_users(
    repository: UserRepository = Depends(get_user_repository),
):
    usecase = GetAllUsersUseCase(repository)
    users = await usecase.execute()
    return [
        {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
        for user in users
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    data: CreateUserSchema,
    repository: UserRepository = Depends(get_user_repository),
):
    usecase = CreateUserUseCase(repository)
    user = await usecase.execute(data)

    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@router.patch("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_user(
    id: uuid.UUID,
    data: UpdateUserSchema,
    repository: UserRepository = Depends(get_user_repository),
):
    usecase = UpdateUserUseCase(repository)
    user = await usecase.execute(str(id), data)
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: uuid.UUID,
    repository: UserRepository = Depends(get_user_repository),
):
    usecase = DeleteUserUseCase(repository)
    await usecase.execute(str(id))
