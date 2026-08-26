from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

# WORKER_COUNT comes from settings.API_WORKER_COUNT (.env) - the same value
# docker-compose.yml's api service passes to uvicorn's --workers. One
# number, one place to change it, instead of two that only work together
# by remembering to keep them in sync.
WORKER_COUNT = settings.API_WORKER_COUNT
TARGET_TOTAL_CONNECTIONS = 90
_PER_WORKER = TARGET_TOTAL_CONNECTIONS // WORKER_COUNT  # 45 at WORKER_COUNT=2
POOL_SIZE = (_PER_WORKER * 2) // 3  # 30 - warm connections, always open
MAX_OVERFLOW = _PER_WORKER - POOL_SIZE  # 15 - extra, opened only under burst

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

celery_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
CelerySessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=celery_engine, class_=AsyncSession
)


async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise
