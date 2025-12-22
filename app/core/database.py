from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

# Async engine only (asyncpg) - works perfectly with Python 3.13
async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(
    async_database_url, 
    echo=False,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_async_db():
    """Dependency for async database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database tables (async)"""
    from app.models import app_model, data_model, file_model
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
