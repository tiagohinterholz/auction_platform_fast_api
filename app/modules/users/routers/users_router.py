import uuid

from fastapi import APIRouter, Depends, status

from app.core.auth.dependencies import get_current_user, require_admin, require_own_user
from app.modules.users.application.schemas.update_user_schema import UpdateUserSchema
from app.modules.users.application.schemas.user_response_schema import UserResponse
from app.modules.users.application.usecases.delete_user_usecase import DeleteUserUseCase
from app.modules.users.application.usecases.get_all_users_usecase import GetAllUsersUseCase
from app.modules.users.application.usecases.get_user_by_id_usecase import GetUserByIdUseCase
from app.modules.users.application.usecases.update_user_usecase import UpdateUserUseCase
from app.modules.users.domain.users_aggregate import User
from app.modules.users.routers.dependencies import (
    get_all_users_use_case,
    get_delete_user_use_case,
    get_update_user_use_case,
    get_user_by_id_use_case,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(
    usecase: GetAllUsersUseCase = Depends(get_all_users_use_case),
    _: User = Depends(require_admin),
):
    return await usecase.execute()


@router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    id: uuid.UUID,
    usecase: GetUserByIdUseCase = Depends(get_user_by_id_use_case),
    _: User = Depends(get_current_user),
):
    return await usecase.execute(str(id))


@router.patch("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_user(
    id: uuid.UUID,
    data: UpdateUserSchema,
    usecase: UpdateUserUseCase = Depends(get_update_user_use_case),
    _: User = Depends(require_own_user),
):
    user = await usecase.execute(str(id), data)
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: uuid.UUID,
    usecase: DeleteUserUseCase = Depends(get_delete_user_use_case),
    _: User = Depends(require_admin),
):
    await usecase.execute(str(id))
