from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.data_model import DataStore
from app.models.file_model import FileStore
from typing import Dict, Any, Optional
import uuid

class AsyncPostgresService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def save_data(self, app_id: str, data_key: str, data_value: Dict[str, Any]) -> DataStore:
        """Save data to PostgreSQL (async)"""
        data_record = DataStore(
            app_id=uuid.UUID(app_id),
            data_key=data_key,
            data_value=data_value
        )
        self.db.add(data_record)
        await self.db.commit()
        await self.db.refresh(data_record)
        return data_record
    
    async def get_data(self, app_id: str, data_key: str) -> Optional[DataStore]:
        """Get data from PostgreSQL (async)"""
        stmt = select(DataStore).where(
            DataStore.app_id == uuid.UUID(app_id),
            DataStore.data_key == data_key
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_data(self, app_id: str, data_key: str, data_value: Dict[str, Any]) -> Optional[DataStore]:
        """Update data in PostgreSQL (async)"""
        data_record = await self.get_data(app_id, data_key)
        if data_record:
            data_record.data_value = data_value
            await self.db.commit()
            await self.db.refresh(data_record)
        return data_record
    
    async def delete_data(self, app_id: str, data_key: str) -> bool:
        """Delete data from PostgreSQL (async)"""
        stmt = delete(DataStore).where(
            DataStore.app_id == uuid.UUID(app_id),
            DataStore.data_key == data_key
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def save_file_metadata(self, app_id: str, file_name: str, file_path: str, file_type: str) -> FileStore:
        """Save file metadata to PostgreSQL (async)"""
        file_record = FileStore(
            app_id=uuid.UUID(app_id),
            file_name=file_name,
            file_path=file_path,
            file_type=file_type
        )
        self.db.add(file_record)
        await self.db.commit()
        await self.db.refresh(file_record)
        return file_record
    
    async def get_file_metadata(self, app_id: str, file_id: str) -> Optional[FileStore]:
        """Get file metadata from PostgreSQL (async)"""
        stmt = select(FileStore).where(
            FileStore.app_id == uuid.UUID(app_id),
            FileStore.id == uuid.UUID(file_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_files(self, app_id: str, limit: int = 100, offset: int = 0) -> list[FileStore]:
        """List files for an app from PostgreSQL (async)"""
        stmt = select(FileStore).where(
            FileStore.app_id == uuid.UUID(app_id)
        ).order_by(FileStore.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def delete_file_metadata(self, app_id: str, file_id: str) -> bool:
        """Delete file metadata from PostgreSQL (async)"""
        stmt = delete(FileStore).where(
            FileStore.app_id == uuid.UUID(app_id),
            FileStore.id == uuid.UUID(file_id)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0