from redis.asyncio import Redis
from app.core.locks.lock_interface import ILockService


class RedisLockService(ILockService):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def acquire(self, key: str, ttl_ms: int) -> bool:
        lock_key = f"lock:{key}"
        result  = await self.redis_client.set(lock_key, "locked", nx=True, px=ttl_ms)
        return result is not None

    async def release(self, key: str) -> None:
        lock_key = f"lock:{key}"
        await self.redis_client.delete(lock_key)