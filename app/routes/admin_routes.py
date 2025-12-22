from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.app_model import App
from app.models.data_model import DataStore
from app.models.file_model import FileStore, RequestLog
from typing import Dict, Any

router = APIRouter()

# Simple admin authentication (replace with proper auth in production)
ADMIN_API_KEY = "admin_super_secret_key_change_this"

def verify_admin_key(admin_key: str = None):
    if admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key"
        )

@router.get("/stats")
async def get_system_stats(
    admin_key: str,
    db: Session = Depends(get_db)
):
    """Get system statistics (admin only)"""
    verify_admin_key(admin_key)
    
    # Count statistics
    total_apps = db.query(func.count(App.id)).scalar()
    total_data_records = db.query(func.count(DataStore.id)).scalar()
    total_files = db.query(func.count(FileStore.id)).scalar()
    total_requests = db.query(func.count(RequestLog.id)).scalar()
    
    # Active apps
    active_apps = db.query(func.count(App.id)).filter(App.status == "active").scalar()
    
    return {
        "system_stats": {
            "total_apps": total_apps,
            "active_apps": active_apps,
            "total_data_records": total_data_records,
            "total_files": total_files,
            "total_requests": total_requests
        }
    }

@router.get("/apps")
async def list_apps(
    admin_key: str,
    db: Session = Depends(get_db)
):
    """List all apps (admin only)"""
    verify_admin_key(admin_key)
    
    apps = db.query(App).all()
    
    return {
        "apps": [
            {
                "id": str(app.id),
                "app_name": app.app_name,
                "status": app.status,
                "created_at": app.created_at.isoformat(),
                "api_key": app.api_key[:8] + "..." # Show only first 8 chars
            }
            for app in apps
        ]
    }

@router.post("/apps/{app_id}/revoke")
async def revoke_app(
    app_id: str,
    admin_key: str,
    db: Session = Depends(get_db)
):
    """Revoke an app's API key (admin only)"""
    verify_admin_key(admin_key)
    
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    app.status = "revoked"
    db.commit()
    
    return {
        "success": True,
        "message": f"App '{app.app_name}' has been revoked"
    }