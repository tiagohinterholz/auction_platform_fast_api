from fastapi import Depends
from redis.asyncio import Redis
from app.core.locks.redis_lock import RedisLockService
from app.core.locks.lock_interface import ILockService
from app.core.redis.client import get_redis_client


def get_lock_service(
    redis: Redis = Depends(get_redis_client),
) -> ILockService:
    return RedisLockService(redis)