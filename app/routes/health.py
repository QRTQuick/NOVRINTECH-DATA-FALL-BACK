from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from app.services.firebase_service import firebase_service

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_async_db)):
    """Check API and database health"""
    
    # Check PostgreSQL
    postgres_status = "connected"
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        print("✅ PostgreSQL health check passed")
    except Exception as e:
        postgres_status = f"error: {str(e)}"
        print(f"❌ PostgreSQL health check failed: {e}")
    
    # Check Firebase
    firebase_status = "connected" if firebase_service.is_initialized else "not initialized"
    
    return {
        "status": "healthy",
        "service": "Novrintech Data Fall Back API",
        "databases": {
            "postgresql": postgres_status,
            "firebase": firebase_status
        },
        "timestamp": "2024-12-22T00:00:00Z"
    }
