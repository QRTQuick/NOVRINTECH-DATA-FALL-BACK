from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.core.database import get_async_db
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
    db: AsyncSession = Depends(get_async_db)
):
    """Get system statistics (admin only)"""
    verify_admin_key(admin_key)
    
    # Count statistics
    total_apps_result = await db.execute(select(func.count(App.id)))
    total_apps = total_apps_result.scalar()
    
    total_data_result = await db.execute(select(func.count(DataStore.id)))
    total_data_records = total_data_result.scalar()
    
    total_files_result = await db.execute(select(func.count(FileStore.id)))
    total_files = total_files_result.scalar()
    
    total_requests_result = await db.execute(select(func.count(RequestLog.id)))
    total_requests = total_requests_result.scalar()
    
    # Active apps
    active_apps_result = await db.execute(
        select(func.count(App.id)).where(App.status == "active")
    )
    active_apps = active_apps_result.scalar()
    
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
    db: AsyncSession = Depends(get_async_db)
):
    """List all apps (admin only)"""
    verify_admin_key(admin_key)
    
    result = await db.execute(select(App))
    apps = result.scalars().all()
    
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
    db: AsyncSession = Depends(get_async_db)
):
    """Revoke an app's API key (admin only)"""
    verify_admin_key(admin_key)
    
    result = await db.execute(select(App).where(App.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    app.status = "revoked"
    await db.commit()
    
    return {
        "success": True,
        "message": f"App '{app.app_name}' has been revoked"
    }