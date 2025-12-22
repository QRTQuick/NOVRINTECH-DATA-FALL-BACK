from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings
from urllib.parse import urlparse, urlunparse

# Async engine only (asyncpg) - works perfectly with Python 3.13
def convert_to_asyncpg_url(database_url: str) -> str:
    """Convert PostgreSQL URL to asyncpg compatible format"""
    # Parse the URL
    parsed = urlparse(database_url)
    
    # Replace scheme
    new_scheme = "postgresql+asyncpg"
    
    # Remove query parameters that asyncpg doesn't support
    new_parsed = parsed._replace(scheme=new_scheme, query="")
    
    return urlunparse(new_parsed)

async_database_url = convert_to_asyncpg_url(settings.DATABASE_URL)
print(f"🔗 Converted URL: {async_database_url}")

async_engine = create_async_engine(
    async_database_url, 
    echo=False,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    connect_args={"ssl": "require"}  # Use asyncpg SSL format
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
