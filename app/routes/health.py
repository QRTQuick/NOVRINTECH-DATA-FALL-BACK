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
        await db.execute("SELECT 1")
    except Exception as e:
        postgres_status = f"error: {str(e)}"
    
    # Check Firebase
    firebase_status = "connected" if firebase_service.is_initialized else "not initialized"
    
    return {
        "status": "healthy",
        "databases": {
            "postgresql": postgres_status,
            "firebase": firebase_status
        }
    }
