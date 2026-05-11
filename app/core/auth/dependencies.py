from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID

from app.core.security.jwt_service import JWTService
from app.modules.users.infrastructure.repository.users_repository import UserRepository
from app.modules.users.routers.dependencies import get_user_repository
from app.modules.users.domain.users_aggregate import User
from app.modules.users.domain.enums.user_role import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_jwt_service = JWTService()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    try:
        payload = _jwt_service.decode_access_token(token)
        user_id: UUID = UUID(payload["sub"])
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repo.get_by_id(str(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def require_own_user(
    id: UUID,
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role == UserRole.ADMIN:
        return current_user
    if current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own data",
        )
    return current_user
