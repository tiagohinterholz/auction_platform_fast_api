from jose import JWTError, jwt
from app.core.config import settings
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4
from app.modules.auth.domain.ports.jwt_service_interface import IJWTService


class JWTService(IJWTService):

    def create_access_token(
        self,
        subject: UUID,
        expires_delta: Optional[timedelta] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[list[str]] = None,
    ) -> str:
        expire = datetime.now(timezone.utc) + (
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
        expires_delta: Optional[timedelta] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
    ) -> tuple[str, str]:
        jti = str(uuid4())
        expire = datetime.now(timezone.utc) + (
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