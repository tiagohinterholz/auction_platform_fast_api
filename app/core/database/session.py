from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Engine ASSÍNCRONO!
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)

# SessionMaker ASSÍNCRONO!
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Dependência do FastAPI (yield assíncrono)
async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
