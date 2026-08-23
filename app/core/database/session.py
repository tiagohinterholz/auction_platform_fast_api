from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Used by Celery tasks (app/modules/auction/application/tasks/auction_tasks.py):
# each task runs its own asyncio.run(), a brand-new event loop every time, but
# asyncpg connections are bound to the loop that created them. AsyncSessionLocal's
# pool would hand out a connection opened on a previous (now-closed) loop and
# blow up with "attached to a different loop". NullPool never reuses a
# connection — every checkout opens fresh and every checkin closes it — so
# there's nothing to carry across event loop boundaries. Never use this for
# the API itself: it runs on one single long-lived loop, where pooling is
# correct and the whole point.
celery_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
CelerySessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=celery_engine, class_=AsyncSession
)


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
