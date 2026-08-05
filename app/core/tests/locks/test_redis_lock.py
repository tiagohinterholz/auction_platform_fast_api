import asyncio
import uuid

import pytest
from redis.asyncio import Redis

from app.core.config import settings
from app.core.locks.redis_lock import RedisLockService


@pytest.fixture
async def redis_client():
    client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield client
    await client.aclose()


@pytest.fixture
def lock_key():
    return f"test:{uuid.uuid4()}"


class TestRedisLockService:

    async def test_acquire_succeeds_when_free(self, redis_client, lock_key):
        service = RedisLockService(redis_client)

        acquired = await service.acquire(lock_key, ttl_ms=5000)

        assert acquired is True

    async def test_acquire_fails_when_already_held(self, redis_client, lock_key):
        holder = RedisLockService(redis_client)
        contender = RedisLockService(redis_client)
        await holder.acquire(lock_key, ttl_ms=5000)

        acquired = await contender.acquire(lock_key, ttl_ms=5000)

        assert acquired is False

    async def test_release_frees_the_lock_for_others(self, redis_client, lock_key):
        holder = RedisLockService(redis_client)
        contender = RedisLockService(redis_client)
        await holder.acquire(lock_key, ttl_ms=5000)

        await holder.release(lock_key)
        acquired = await contender.acquire(lock_key, ttl_ms=5000)

        assert acquired is True

    async def test_release_does_not_steal_a_lock_acquired_by_someone_else(
        self, redis_client, lock_key
    ):
        """Regression test for the C5 bug: releasing a lock whose TTL already
        expired must not delete a *different* holder's now-current lock."""
        expired_holder = RedisLockService(redis_client)
        await expired_holder.acquire(lock_key, ttl_ms=50)

        # simulate the TTL expiring mid-processing, then a second request
        # picking up the now-free key
        await asyncio.sleep(0.1)
        new_holder = RedisLockService(redis_client)
        assert await new_holder.acquire(lock_key, ttl_ms=5000) is True

        # the original holder finishes late and releases what it thinks is
        # still its lock
        await expired_holder.release(lock_key)

        # the new holder's lock must still be intact
        still_held = await redis_client.get(f"lock:{lock_key}")
        assert still_held is not None

        another_contender = RedisLockService(redis_client)
        assert await another_contender.acquire(lock_key, ttl_ms=5000) is False
