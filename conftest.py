import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.modules.auction.infrastructure.persistence.auction_model
import app.modules.auction.infrastructure.persistence.auction_read_model
import app.modules.auth.infrastructure.persistence.refresh_token_model
import app.modules.bidding.infrastructure.persistence.bid_read_model
import app.modules.bidding.infrastructure.persistence.bidding_model
import app.modules.users.infrastructure.persistence.users_model  # noqa: F401
from app.core.config import settings
from app.core.database.base import Base

TEST_DATABASE_URL = settings.DATABASE_URL.replace("/auction_db", "/auction_test_db")

test_engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def rollback_session():
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession):
    from app.core.database.session import get_db
    from app.core.events.in_memory_event_bus import InMemoryEventBus
    from app.core.locks.dependencies import get_lock_service
    from app.core.locks.lock_interface import ILockService
    from main import app

    class FakeLockService(ILockService):
        async def acquire(self, key: str, ttl_ms: int) -> bool:
            return True

        async def release(self, key: str) -> None:
            pass

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_lock_service] = lambda: FakeLockService()
    app.state.event_bus = InMemoryEventBus()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
