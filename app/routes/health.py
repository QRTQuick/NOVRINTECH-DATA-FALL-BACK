from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.firebase_service import firebase_service

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Check API and database health"""
    
    # Check PostgreSQL
    postgres_status = "connected"
    try:
        db.execute("SELECT 1")
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
