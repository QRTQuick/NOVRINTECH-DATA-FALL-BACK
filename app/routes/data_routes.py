from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any, Dict
from app.core.database import get_db
from app.services.postgres_service import PostgresService
from app.services.sync_service import SyncService

router = APIRouter()

class DataSaveRequest(BaseModel):
    data_key: str
    data_value: Dict[str, Any]

class DataUpdateRequest(BaseModel):
    data_value: Dict[str, Any]

@router.post("/save")
async def save_data(
    request: Request,
    data: DataSaveRequest,
    db: Session = Depends(get_db)
):
    """Save data to PostgreSQL and sync to Firebase"""
    app_id = request.state.app_id
    
    postgres_service = PostgresService(db)
    sync_service = SyncService(db)
    
    # Save to PostgreSQL
    result = postgres_service.save_data(app_id, data.data_key, data.data_value)
    
    # Sync to Firebase
    sync_service.sync_to_firebase(app_id, data.data_key, data.data_value)
    
    return {
        "success": True,
        "message": "Data saved successfully",
        "data_id": str(result.id),
        "data_key": data.data_key
    }

@router.get("/read/{data_key}")
async def read_data(
    request: Request,
    data_key: str,
    db: Session = Depends(get_db)
):
    """Read data from PostgreSQL with Firebase fallback"""
    app_id = request.state.app_id
    
    postgres_service = PostgresService(db)
    sync_service = SyncService(db)
    
    # Try PostgreSQL first
    try:
        result = postgres_service.get_data(app_id, data_key)
        if result:
            return {
                "success": True,
                "source": "postgresql",
                "data_key": data_key,
                "data_value": result.data_value,
                "updated_at": result.updated_at.isoformat()
            }
    except Exception as e:
        # Fallback to Firebase
        firebase_data = sync_service.get_from_firebase(app_id, data_key)
        if firebase_data:
            return {
                "success": True,
                "source": "firebase_fallback",
                "data_key": data_key,
                "data_value": firebase_data
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Data with key '{data_key}' not found"
    )

@router.put("/update/{data_key}")
async def update_data(
    request: Request,
    data_key: str,
    data: DataUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update data in PostgreSQL and sync to Firebase"""
    app_id = request.state.app_id
    
    postgres_service = PostgresService(db)
    sync_service = SyncService(db)
    
    # Update PostgreSQL
    result = postgres_service.update_data(app_id, data_key, data.data_value)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data with key '{data_key}' not found"
        )
    
    # Sync to Firebase
    sync_service.sync_to_firebase(app_id, data_key, data.data_value)
    
    return {
        "success": True,
        "message": "Data updated successfully",
        "data_key": data_key,
        "updated_at": result.updated_at.isoformat()
    }

@router.delete("/delete/{data_key}")
async def delete_data(
    request: Request,
    data_key: str,
    db: Session = Depends(get_db)
):
    """Delete data from PostgreSQL and Firebase"""
    app_id = request.state.app_id
    
    postgres_service = PostgresService(db)
    sync_service = SyncService(db)
    
    # Delete from PostgreSQL
    success = postgres_service.delete_data(app_id, data_key)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data with key '{data_key}' not found"
        )
    
    # Delete from Firebase
    sync_service.delete_from_firebase(app_id, data_key)
    
    return {
        "success": True,
        "message": "Data deleted successfully",
        "data_key": data_key
    }
