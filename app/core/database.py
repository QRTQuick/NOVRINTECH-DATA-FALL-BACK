from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings
from urllib.parse import urlparse, urlunparse

# Async engine only (asyncpg) - works perfectly with Python 3.13 and Neon
def convert_to_asyncpg_url(database_url: str) -> str:
    """Convert PostgreSQL URL to asyncpg compatible format"""
    # Parse the URL
    parsed = urlparse(database_url)
    
    # Replace scheme
    new_scheme = "postgresql+asyncpg"
    
    # Remove Neon-specific query parameters that asyncpg doesn't support
    # Keep only the essential ones
    query_params = []
    if parsed.query:
        for param in parsed.query.split('&'):
            if param.startswith('sslmode='):
                # Convert sslmode to asyncpg format
                continue  # asyncpg handles SSL automatically for Neon
            elif param.startswith('channel_binding='):
                # Remove channel_binding as asyncpg doesn't support it
                continue
            else:
                query_params.append(param)
    
    new_query = '&'.join(query_params) if query_params else ""
    new_parsed = parsed._replace(scheme=new_scheme, query=new_query)
    
    return urlunparse(new_parsed)

async_database_url = convert_to_asyncpg_url(settings.DATABASE_URL)
print(f"🔗 Neon Database URL: {async_database_url}")

# Configure engine for Neon database
async_engine = create_async_engine(
    async_database_url, 
    echo=False,  # Set to True for debugging SQL queries
    pool_size=5,  # Smaller pool for Neon
    max_overflow=10,  # Smaller overflow for Neon
    pool_pre_ping=True,  # Important for Neon - checks connections
    pool_recycle=3600,  # Recycle connections every hour
    # SSL is handled automatically by asyncpg for Neon
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
    try:
        print("🗄️ Initializing database tables...")
        from app.models import app_model, data_model, file_model
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        raise

async def test_db_connection():
    """Test database connection"""
    try:
        async with async_engine.connect() as conn:
            from sqlalchemy import text
            result = await conn.execute(text("SELECT 1"))
            print("✅ Database connection test successful")
            return True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False
