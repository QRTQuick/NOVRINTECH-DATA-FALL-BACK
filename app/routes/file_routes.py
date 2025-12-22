from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from app.services.async_postgres_service import AsyncPostgresService
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db)
):
    """Upload file and save metadata"""
    app_id = request.state.app_id
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Save metadata to database
    postgres_service = AsyncPostgresService(db)
    file_record = await postgres_service.save_file_metadata(
        app_id=app_id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type
    )
    
    return {
        "success": True,
        "message": "File uploaded successfully",
        "file_id": str(file_record.id),
        "file_name": file.filename,
        "file_type": file.content_type
    }

@router.get("/read/{file_id}")
async def read_file(
    request: Request,
    file_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get file metadata"""
    app_id = request.state.app_id
    
    postgres_service = AsyncPostgresService(db)
    file_record = await postgres_service.get_file_metadata(app_id, file_id)
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID '{file_id}' not found"
        )
    
    return {
        "success": True,
        "file_id": str(file_record.id),
        "file_name": file_record.file_name,
        "file_path": file_record.file_path,
        "file_type": file_record.file_type,
        "created_at": file_record.created_at.isoformat()
    }
