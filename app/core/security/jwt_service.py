from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from jose import JWTError, jwt

from app.core.config import settings
from app.modules.auth.domain.ports.jwt_service_interface import IJWTService


class JWTService(IJWTService):

    def create_access_token(
        self,
        subject: UUID,
        expires_delta: timedelta | None = None,
        name: str | None = None,
        email: str | None = None,
        role: list[str] | None = None,
    ) -> str:
        expire = datetime.now(UTC) + (
            expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        payload = {
            'sub': str(subject),
            'jti': str(uuid4()),
            'exp': expire,
            'name': name,
            'email': email,
            'role': role,
        }
        return jwt.encode(payload, settings.JWT_ACCESS_SECRET, algorithm=settings.ALGORITHM)


    def create_refresh_token(
        self,
        subject: UUID,
        expires_delta: timedelta | None = None,
        name: str | None = None,
        email: str | None = None,
        role: str | None = None,
    ) -> tuple[str, str]:
        jti = str(uuid4())
        expire = datetime.now(UTC) + (
            expires_delta if expires_delta else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        payload = {
            'sub': str(subject),
            'jti': jti,
            'exp': expire,
            'name': name,
            'email': email,
            'role': role,
        }
        token = jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm=settings.ALGORITHM)
        return token, jti


    def decode_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.JWT_ACCESS_SECRET, algorithms=[settings.ALGORITHM])
            if payload.get('sub') is None:
                raise ValueError('Token inválido')
            return payload
        except JWTError:
            raise ValueError('Token inválido ou expirado')


    def decode_refresh_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.JWT_REFRESH_SECRET, algorithms=[settings.ALGORITHM])
            if payload.get('sub') is None or payload.get('jti') is None:
                raise ValueError('Token inválido')
            return payload
        except JWTError:
            raise ValueError('Token inválido ou expirado')