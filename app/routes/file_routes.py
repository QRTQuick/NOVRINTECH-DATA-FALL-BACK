from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from app.services.async_postgres_service import AsyncPostgresService
from app.models.app_model import App, AppStatus
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
    try:
        # Handle app_id - use default if middleware is disabled
        try:
            app_id = request.state.app_id
        except AttributeError:
            # Default app_id for testing when middleware is disabled
            app_id = "00000000-0000-0000-0000-000000000000"
            
            # Ensure default app exists
            from sqlalchemy import select
            result = await db.execute(
                select(App).where(App.id == uuid.UUID(app_id))
            )
            default_app = result.scalar_one_or_none()
            
            if not default_app:
                # Create default app for testing
                default_app = App(
                    id=uuid.UUID(app_id),
                    app_name="Default Test App",
                    api_key="novrintech_api_key_2024_secure",
                    status=AppStatus.active
                )
                db.add(default_app)
                await db.commit()
        
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
    
    except Exception as e:
        # Log the error for debugging
        print(f"❌ Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return detailed error for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.get("/read/{file_id}")
async def read_file(
    request: Request,
    file_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get file metadata"""
    # Handle app_id - use default if middleware is disabled
    try:
        app_id = request.state.app_id
    except AttributeError:
        # Default app_id for testing when middleware is disabled
        app_id = "00000000-0000-0000-0000-000000000000"
    
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

@router.get("/list")
async def list_files(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    limit: int = 100,
    offset: int = 0
):
    """List all files for the app"""
    # Handle app_id - use default if middleware is disabled
    try:
        app_id = request.state.app_id
    except AttributeError:
        # Default app_id for testing when middleware is disabled
        app_id = "00000000-0000-0000-0000-000000000000"
    
    postgres_service = AsyncPostgresService(db)
    files = await postgres_service.list_files(app_id, limit, offset)
    
    return {
        "success": True,
        "files": [
            {
                "file_id": str(file.id),
                "file_name": file.file_name,
                "file_type": file.file_type,
                "file_size": os.path.getsize(file.file_path) if os.path.exists(file.file_path) else 0,
                "created_at": file.created_at.isoformat()
            }
            for file in files
        ],
        "total": len(files)
    }

@router.get("/download/{file_id}")
async def download_file(
    request: Request,
    file_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Download file by ID"""
    from fastapi.responses import FileResponse
    
    # Handle app_id - use default if middleware is disabled
    try:
        app_id = request.state.app_id
    except AttributeError:
        # Default app_id for testing when middleware is disabled
        app_id = "00000000-0000-0000-0000-000000000000"
    
    postgres_service = AsyncPostgresService(db)
    file_record = await postgres_service.get_file_metadata(app_id, file_id)
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID '{file_id}' not found"
        )
    
    if not os.path.exists(file_record.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    return FileResponse(
        path=file_record.file_path,
        filename=file_record.file_name,
        media_type=file_record.file_type or 'application/octet-stream'
    )

@router.delete("/delete/{file_id}")
async def delete_file(
    request: Request,
    file_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete file by ID"""
    # Handle app_id - use default if middleware is disabled
    try:
        app_id = request.state.app_id
    except AttributeError:
        # Default app_id for testing when middleware is disabled
        app_id = "00000000-0000-0000-0000-000000000000"
    
    postgres_service = AsyncPostgresService(db)
    file_record = await postgres_service.get_file_metadata(app_id, file_id)
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID '{file_id}' not found"
        )
    
    # Delete file from disk
    if os.path.exists(file_record.file_path):
        os.remove(file_record.file_path)
    
    # Delete from database
    success = await postgres_service.delete_file_metadata(app_id, file_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file from database"
        )
    
    return {
        "success": True,
        "message": f"File '{file_record.file_name}' deleted successfully",
        "file_id": file_id
    }
