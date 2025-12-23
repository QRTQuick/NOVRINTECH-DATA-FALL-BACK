#!/usr/bin/env python3
"""
Create a default app record for testing when middleware is disabled
"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.app_model import App, AppStatus

async def create_default_app():
    """Create the default app record for testing"""
    default_app_id = "00000000-0000-0000-0000-000000000000"
    default_api_key = "novrintech_api_key_2024_secure"
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if default app already exists
            from sqlalchemy import select
            result = await db.execute(
                select(App).where(App.id == uuid.UUID(default_app_id))
            )
            existing_app = result.scalar_one_or_none()
            
            if existing_app:
                print(f"✅ Default app already exists: {existing_app.app_name}")
                return existing_app
            
            # Create default app
            default_app = App(
                id=uuid.UUID(default_app_id),
                app_name="Default Test App",
                api_key=default_api_key,
                status=AppStatus.active
            )
            
            db.add(default_app)
            await db.commit()
            await db.refresh(default_app)
            
            print(f"✅ Created default app: {default_app.app_name}")
            print(f"   App ID: {default_app.id}")
            print(f"   API Key: {default_app.api_key}")
            
            return default_app
            
        except Exception as e:
            print(f"❌ Error creating default app: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    print("🚀 Creating default app for testing...")
    asyncio.run(create_default_app())
    print("✅ Done!")