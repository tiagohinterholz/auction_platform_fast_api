from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

# This pool is created once PER WORKER PROCESS (uvicorn --workers N forks N
# separate OS processes, each importing this module fresh and building its
# own engine/pool - nothing here is shared across workers). So the real
# ceiling on connections coming from the API is pool_size+max_overflow
# TIMES the worker count, not just this number by itself.
#
# pool_size=16, max_overflow=8 -> 24 per worker. At the 4 workers this repo
# currently runs (docker-compose.yml's api service), that's 4x24=96 total,
# under our target of 98 out of Postgres's own max_connections (100 by
# default) - leaving just 2 headroom for the Celery worker (NullPool,
# opens/closes per task) and any manual/admin connection. That's a
# deliberately tight margin, not a cautious one - push it further only
# alongside also raising Postgres's max_connections.
#
# The SQLAlchemy default (5 + 10 = 15, i.e. 60 total at 4 workers) was
# already found live via a Locust load test to queue up and time out at 30s
# under a few hundred concurrent requests, well before Postgres itself (0%
# CPU during the same run) was under any real pressure. If WORKER_COUNT
# here ever drifts from the actual --workers flag in docker-compose.yml,
# these two numbers need to be revisited together.
WORKER_COUNT = 4
TARGET_TOTAL_CONNECTIONS = 98
_PER_WORKER = TARGET_TOTAL_CONNECTIONS // WORKER_COUNT  # 18
POOL_SIZE = (_PER_WORKER * 2) // 3  # 12 - warm connections, always open
MAX_OVERFLOW = _PER_WORKER - POOL_SIZE  # 6 - extra, opened only under burst

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

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
    """Every request gets its transaction explicitly closed the moment the
    endpoint returns or raises - never left for `async with`'s implicit
    close()-triggers-rollback to clean up later.

    Found live via a Locust load test: read-only repository methods (e.g.
    AuctionRepository.get_by_id) run a SELECT and never call commit() or
    rollback() themselves. On the happy path a later write's commit() (e.g.
    BiddingRepository.save()) closes that transaction as a side effect, but
    on any error path that raises before reaching a write - a bid rejected
    as too low, an auction not found, the lock already held - nothing ever
    closes it. The connection sits "idle in transaction" in Postgres until
    this generator's own cleanup eventually runs, which under heavy
    concurrent load gets progressively delayed: each stuck connection is
    one less available in the pool, which slows everything else down,
    which delays that cleanup further. That's a feedback loop, not a fixed
    cost - it explains a failure rate that keeps climbing under *constant*
    load instead of settling at one contention level.
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise
