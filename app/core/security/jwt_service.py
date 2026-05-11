from jose import JWTError, jwt
from app.core.config import settings
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4


def create_access_token(
    subject: UUID,
    expires_delta: Optional[timedelta] = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        'sub': str(subject),
        'jti': str(uuid4()),
        'exp': expire,
    }
    return jwt.encode(payload, settings.JWT_ACCESS_SECRET, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: UUID,
    expires_delta: Optional[timedelta] = None,
) -> tuple[str, str]:
    jti = str(uuid4())
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    payload = {
        'sub': str(subject),
        'jti': jti,
        'exp': expire,
    }
    token = jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm=settings.ALGORITHM)
    return token, jti


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_ACCESS_SECRET, algorithms=[settings.ALGORITHM])
        if payload.get('sub') is None:
            raise ValueError('Token inválido')
        return payload
    except JWTError:
        raise ValueError('Token inválido ou expirado')


def decode_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_REFRESH_SECRET, algorithms=[settings.ALGORITHM])
        if payload.get('sub') is None or payload.get('jti') is None:
            raise ValueError('Token inválido')
        return payload
    except JWTError:
        raise ValueError('Token inválido ou expirado')
