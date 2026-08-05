from redis.asyncio import Redis
from redis.asyncio.lock import Lock
from redis.exceptions import LockNotOwnedError

from app.core.locks.lock_interface import ILockService


class RedisLockService(ILockService):
    """Distributed lock backed by redis-py's own Lock primitive.

    redis-py's Lock stores a random ownership token per acquire() call and
    releases via an atomic Lua script that only deletes the key if the token
    still matches — unlike a bare SET/DELETE, one holder can never release a
    lock that a different holder has since acquired (e.g. because the first
    holder's TTL expired mid-processing).

    thread_local=False because a single asyncio event loop thread runs many
    concurrent requests: redis-py's default thread-local token storage would
    let two unrelated coroutines on the same thread clobber each other's
    token. Instead, each acquired Lock object is kept in `_locks`, scoped to
    this RedisLockService instance — which FastAPI already creates fresh per
    request via `get_lock_service`, matching the one-acquire-per-release
    usage in PlaceBidUseCase.
    """

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self._locks: dict[str, Lock] = {}

    async def acquire(self, key: str, ttl_ms: int) -> bool:
        lock_key = f"lock:{key}"
        lock = self.redis_client.lock(
            lock_key, timeout=ttl_ms / 1000, blocking=False, thread_local=False
        )
        acquired = await lock.acquire()
        if acquired:
            self._locks[lock_key] = lock
        return acquired

    async def release(self, key: str) -> None:
        lock_key = f"lock:{key}"
        lock = self._locks.pop(lock_key, None)
        if lock is None:
            return
        try:
            await lock.release()
        except LockNotOwnedError:
            # TTL already expired before we got here — someone else may own
            # the key now. Nothing to clean up; the caller's work is done.
            pass
