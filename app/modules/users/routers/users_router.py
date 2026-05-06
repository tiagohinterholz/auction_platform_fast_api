from fastapi import APIRouter, Depends, status

from typing import List
import uuid

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
from app.modules.users.application.schemas.user_response_schema import UserResponse

from app.modules.users.routers.dependencies import (
    get_create_user_use_case,
    get_all_users_use_case,
    get_user_by_id_use_case,
    get_delete_user_use_case,
    get_update_user_use_case,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    id: uuid.UUID,
    usecase: GetUserByIdUseCase = Depends(get_user_by_id_use_case),
):
    user = await usecase.execute(str(id))
    return user


@router.get("", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(
    usecase: GetAllUsersUseCase = Depends(get_all_users_use_case),
):
    users = await usecase.execute()
    return users


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    data: CreateUserSchema,
    usecase: CreateUserUseCase = Depends(get_create_user_use_case),
):
    user = await usecase.execute(data)

    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@router.patch("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_user(
    id: uuid.UUID,
    data: UpdateUserSchema,
    usecase: UpdateUserUseCase = Depends(get_update_user_use_case),
):
    user = await usecase.execute(str(id), data)
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: uuid.UUID,
    usecase: DeleteUserUseCase = Depends(get_delete_user_use_case),
):
    await usecase.execute(str(id))
