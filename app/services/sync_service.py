from sqlalchemy.orm import Session
from app.services.firebase_service import firebase_service
from typing import Dict, Any, Optional

class SyncService:
    def __init__(self, db: Session):
        self.db = db
    
    def sync_to_firebase(self, app_id: str, data_key: str, data_value: Dict[str, Any]):
        """Sync data from PostgreSQL to Firebase"""
        firebase_service.save_data(app_id, data_key, data_value)
    
    def get_from_firebase(self, app_id: str, data_key: str) -> Optional[Dict[str, Any]]:
        """Get data from Firebase (fallback)"""
        return firebase_service.get_data(app_id, data_key)
    
    def delete_from_firebase(self, app_id: str, data_key: str):
        """Delete data from Firebase"""
        firebase_service.delete_data(app_id, data_key)
