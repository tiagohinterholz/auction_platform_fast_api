import uuid

from fastapi import APIRouter, status

from app.core.auth.dependencies import OwnUser, RequireAdmin
from app.modules.users.application.schemas.update_user_schema import UpdateUserSchema
from app.modules.users.application.schemas.user_response_schema import UserResponse
from app.modules.users.routers.dependencies import (
    DeleteUserUseCaseDep,
    GetAllUsersUseCaseDep,
    GetUserByIdUseCaseDep,
    UpdateUserUseCaseDep,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(
    usecase: GetAllUsersUseCaseDep,
    _: RequireAdmin,
):
    return await usecase.execute()


@router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    id: uuid.UUID,
    usecase: GetUserByIdUseCaseDep,
    _: OwnUser,
):
    return await usecase.execute(str(id))


@router.patch("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_user(
    id: uuid.UUID,
    data: UpdateUserSchema,
    usecase: UpdateUserUseCaseDep,
    _: OwnUser,
):
    user = await usecase.execute(str(id), data)
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: uuid.UUID,
    usecase: DeleteUserUseCaseDep,
    _: RequireAdmin,
):
    await usecase.execute(str(id))
