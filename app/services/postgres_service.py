from sqlalchemy.orm import Session
from app.models.data_model import DataStore
from app.models.file_model import FileStore
from typing import Dict, Any, Optional
import uuid

class PostgresService:
    def __init__(self, db: Session):
        self.db = db
    
    def save_data(self, app_id: str, data_key: str, data_value: Dict[str, Any]) -> DataStore:
        """Save data to PostgreSQL"""
        data_record = DataStore(
            app_id=uuid.UUID(app_id),
            data_key=data_key,
            data_value=data_value
        )
        self.db.add(data_record)
        self.db.commit()
        self.db.refresh(data_record)
        return data_record
    
    def get_data(self, app_id: str, data_key: str) -> Optional[DataStore]:
        """Get data from PostgreSQL"""
        return self.db.query(DataStore).filter(
            DataStore.app_id == uuid.UUID(app_id),
            DataStore.data_key == data_key
        ).first()
    
    def update_data(self, app_id: str, data_key: str, data_value: Dict[str, Any]) -> Optional[DataStore]:
        """Update data in PostgreSQL"""
        data_record = self.get_data(app_id, data_key)
        if data_record:
            data_record.data_value = data_value
            self.db.commit()
            self.db.refresh(data_record)
        return data_record
    
    def delete_data(self, app_id: str, data_key: str) -> bool:
        """Delete data from PostgreSQL"""
        data_record = self.get_data(app_id, data_key)
        if data_record:
            self.db.delete(data_record)
            self.db.commit()
            return True
        return False
    
    def save_file_metadata(self, app_id: str, file_name: str, file_path: str, file_type: str) -> FileStore:
        """Save file metadata to PostgreSQL"""
        file_record = FileStore(
            app_id=uuid.UUID(app_id),
            file_name=file_name,
            file_path=file_path,
            file_type=file_type
        )
        self.db.add(file_record)
        self.db.commit()
        self.db.refresh(file_record)
        return file_record
    
    def get_file_metadata(self, app_id: str, file_id: str) -> Optional[FileStore]:
        """Get file metadata from PostgreSQL"""
        return self.db.query(FileStore).filter(
            FileStore.app_id == uuid.UUID(app_id),
            FileStore.id == uuid.UUID(file_id)
        ).first()
