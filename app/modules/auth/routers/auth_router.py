from fastapi import APIRouter, status
from pydantic import BaseModel

from app.core.auth.dependencies import CurrentUser
from app.modules.auth.application.schemas.login_schema import LoginSchema
from app.modules.auth.application.schemas.register_schema import RegisterSchema
from app.modules.auth.application.schemas.token_schema import TokenSchema
from app.modules.auth.routers.dependencies import (
    LoginUseCaseDep,
    LogoutUseCaseDep,
    RefreshTokenUseCaseDep,
    RegisterUseCaseDep,
)


class RefreshRequest(BaseModel):
    refresh_token: str


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenSchema)
async def register(
    data: RegisterSchema,
    use_case: RegisterUseCaseDep,
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
    use_case: LoginUseCaseDep,
) -> TokenSchema:
    result = await use_case.execute(email=data.email, password=data.password)
    return TokenSchema(**result)


@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=TokenSchema)
async def refresh_token(
    data: RefreshRequest,
    use_case: RefreshTokenUseCaseDep,
) -> TokenSchema:
    result = await use_case.execute(refresh_token=data.refresh_token)
    return TokenSchema(**result)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: RefreshRequest,
    use_case: LogoutUseCaseDep,
    _: CurrentUser,
) -> None:
    await use_case.execute(refresh_token=data.refresh_token)
