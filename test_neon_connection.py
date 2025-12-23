#!/usr/bin/env python3
"""
Test Neon database connection and setup
"""
import os
import asyncio
import re
from sqlalchemy import text
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

async def test_neon_database():
    """Test connection to Neon database"""
    print("🔍 Testing Neon Database Connection")
    print("=" * 50)
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    print(f"📊 Database: {database_url[:50]}...")
    
    # Convert to asyncpg format
    async_url = re.sub(r'^postgresql:', 'postgresql+asyncpg:', database_url)
    
    try:
        # Create engine
        engine = create_async_engine(
            async_url, 
            echo=True,
            pool_size=2,
            max_overflow=5,
            pool_pre_ping=True
        )
        
        # Test basic connection
        print("\n1️⃣ Testing basic connection...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 'Hello Neon!' as message"))
            row = result.fetchone()
            print(f"✅ Connection successful: {row[0]}")
        
        # Test table creation
        print("\n2️⃣ Testing table operations...")
        async with engine.begin() as conn:
            # Create a test table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Insert test data
            await conn.execute(text("""
                INSERT INTO test_connection (message) 
                VALUES ('Neon database test successful!')
            """))
            
            # Read test data
            result = await conn.execute(text("""
                SELECT message, created_at FROM test_connection 
                ORDER BY created_at DESC LIMIT 1
            """))
            row = result.fetchone()
            print(f"✅ Table operations successful: {row[0]}")
            
            # Clean up
            await conn.execute(text("DROP TABLE test_connection"))
        
        # Test app-related tables
        print("\n3️⃣ Testing app tables...")
        async with engine.begin() as conn:
            # Check if apps table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'apps'
                )
            """))
            apps_table_exists = result.scalar()
            print(f"Apps table exists: {apps_table_exists}")
            
            if not apps_table_exists:
                print("⚠️ Apps table doesn't exist - need to run database initialization")
            else:
                # Count apps
                result = await conn.execute(text("SELECT COUNT(*) FROM apps"))
                app_count = result.scalar()
                print(f"Total apps in database: {app_count}")
        
        await engine.dispose()
        print("\n✅ All Neon database tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def initialize_database_tables():
    """Initialize the database tables"""
    print("\n🔧 Initializing database tables...")
    
    try:
        # Import after setting up the path
        import sys
        sys.path.append('.')
        
        from app.core.database import init_db, async_engine
        from app.models.app_model import App, AppStatus
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import select
        import uuid
        
        # Initialize tables
        await init_db()
        print("✅ Tables initialized")
        
        # Create default app
        async with AsyncSessionLocal() as db:
            default_app_id = "00000000-0000-0000-0000-000000000000"
            result = await db.execute(
                select(App).where(App.id == uuid.UUID(default_app_id))
            )
            existing_app = result.scalar_one_or_none()
            
            if not existing_app:
                default_app = App(
                    id=uuid.UUID(default_app_id),
                    app_name="Default Test App",
                    api_key="novrintech_api_key_2024_secure",
                    status=AppStatus.active
                )
                db.add(default_app)
                await db.commit()
                print("✅ Created default app")
            else:
                print("✅ Default app already exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Neon Database Test & Setup")
    
    async def main():
        # Test connection first
        if await test_neon_database():
            # Try to initialize if needed
            await initialize_database_tables()
        else:
            print("❌ Database connection failed - check your DATABASE_URL")
    
    asyncio.run(main())