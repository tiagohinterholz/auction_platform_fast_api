from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.modules.auth.application.schemas.login_schema import LoginSchema
from app.modules.auth.application.schemas.register_schema import RegisterSchema
from app.modules.auth.application.schemas.token_schema import TokenSchema
from app.modules.auth.application.usecases.login_use_case import LoginUseCase
from app.modules.auth.application.usecases.logout_use_case import LogoutUseCase
from app.modules.auth.application.usecases.refresh_use_case import RefreshTokenUseCase
from app.modules.auth.application.usecases.register_use_case import RegisterUseCase
from app.modules.auth.routers.dependencies import (
    get_current_jti,
    get_login_use_case,
    get_logout_use_case,
    get_refresh_use_case,
    get_register_use_case,
)


class RefreshRequest(BaseModel):
    refresh_token: str


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenSchema)
async def register(
    data: RegisterSchema,
    use_case: RegisterUseCase = Depends(get_register_use_case),
) -> TokenSchema:
    result = await use_case.execute(
        name=data.name,
        email=data.email,
        password=data.password,
        cpf=data.cpf,
    )
    return TokenSchema(**result)


@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenSchema)
async def login(
    data: LoginSchema,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> TokenSchema:
    result = await use_case.execute(email=data.email, password=data.password)
    return TokenSchema(**result)


@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=TokenSchema)
async def refresh_token(
    data: RefreshRequest,
    use_case: RefreshTokenUseCase = Depends(get_refresh_use_case),
) -> TokenSchema:
    result = await use_case.execute(refresh_token=data.refresh_token)
    return TokenSchema(**result)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    jti: str = Depends(get_current_jti),
    use_case: LogoutUseCase = Depends(get_logout_use_case),
) -> None:
    await use_case.execute(jti=jti)
