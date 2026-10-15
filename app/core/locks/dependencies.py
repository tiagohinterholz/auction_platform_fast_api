from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.core.locks.lock_interface import ILockService
from app.core.locks.redis_lock import RedisLockService
from app.core.redis.client import get_redis_client


def get_lock_service(
    redis: Annotated[Redis, Depends(get_redis_client)],
) -> ILockService:
    return RedisLockService(redis)


LockServiceDep = Annotated[ILockService, Depends(get_lock_service)]
