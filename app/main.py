from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.routes import data_routes, file_routes, health, admin_routes
from app.middleware.api_key_auth import APIKeyMiddleware
from app.services.keep_alive import keep_alive_service

app = FastAPI(
    title="Novrintech Data Fall Back API",
    description="Universal backend API for data storage and retrieval",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Authentication Middleware (temporarily disabled for testing)
# app.add_middleware(APIKeyMiddleware)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        print("🚀 Starting Novrintech Data Fall Back API...")
        print(f"📊 Database URL: {settings.DATABASE_URL[:50]}...")
        
        # Test database connection first
        from app.core.database import test_db_connection
        if not await test_db_connection():
            print("⚠️ Database connection failed, but continuing startup...")
        
        # Initialize database tables
        await init_db()
        print("✅ Database initialized successfully")
        
        # Create default app for testing if it doesn't exist
        await create_default_app_if_missing()
        
        # Start keep-alive service
        keep_alive_service.start()
        print(f"🔄 Keep-alive service started (pings every 4 seconds)")
        
        print("🔥 Novrintech Data Fall Back API started successfully!")
        print(f"📡 API running on {settings.API_HOST}:{settings.API_PORT}")
        print(f"🌐 External URL: https://novrintech-data-fall-back.onrender.com")
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()
        # Don't raise - let the app start anyway
        print("⚠️ Starting with limited functionality...")

async def create_default_app_if_missing():
    """Create default app for testing if it doesn't exist"""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.app_model import App, AppStatus
        from sqlalchemy import select
        import uuid
        
        async with AsyncSessionLocal() as db:
            # Check if default app exists
            default_app_id = "00000000-0000-0000-0000-000000000000"
            result = await db.execute(
                select(App).where(App.id == uuid.UUID(default_app_id))
            )
            existing_app = result.scalar_one_or_none()
            
            if not existing_app:
                # Create default app
                default_app = App(
                    id=uuid.UUID(default_app_id),
                    app_name="Default Test App",
                    api_key="novrintech_api_key_2024_secure",
                    status=AppStatus.active
                )
                db.add(default_app)
                await db.commit()
                print("✅ Created default app for testing")
            else:
                print("✅ Default app already exists")
                
    except Exception as e:
        print(f"⚠️ Could not create default app: {e}")
        # Don't fail startup for this

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    try:
        keep_alive_service.stop()
        print("🔄 Novrintech Data Fall Back API shutting down...")
    except Exception as e:
        print(f"❌ Shutdown error: {e}")

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(data_routes.router, prefix="/data", tags=["Data"])
app.include_router(file_routes.router, prefix="/file", tags=["Files"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {
        "service": "Novrintech Data Fall Back API",
        "status": "active",
        "version": "1.0.0",
        "message": "🔥 API is running successfully!",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "data": "/data/*",
            "files": "/file/*"
        }
    }
