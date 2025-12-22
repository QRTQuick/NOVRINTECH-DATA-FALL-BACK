import firebase_admin
from firebase_admin import credentials, db
from app.core.config import settings
from typing import Dict, Any, Optional
import os

class FirebaseService:
    def __init__(self):
        self.is_initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Firebase Admin SDK"""
        try:
            if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://novrintech-data-fall-back-default-rtdb.firebaseio.com/'
                })
                self.is_initialized = True
            else:
                print(f"Warning: Firebase credentials not found at {settings.FIREBASE_CREDENTIALS_PATH}")
        except Exception as e:
            print(f"Firebase initialization error: {e}")
    
    def save_data(self, app_id: str, data_key: str, data_value: Dict[str, Any]):
        """Save data to Firebase Realtime Database"""
        if not self.is_initialized:
            return
        
        try:
            ref = db.reference(f'apps/{app_id}/data/{data_key}')
            ref.set(data_value)
        except Exception as e:
            print(f"Firebase save error: {e}")
    
    def get_data(self, app_id: str, data_key: str) -> Optional[Dict[str, Any]]:
        """Get data from Firebase Realtime Database"""
        if not self.is_initialized:
            return None
        
        try:
            ref = db.reference(f'apps/{app_id}/data/{data_key}')
            return ref.get()
        except Exception as e:
            print(f"Firebase get error: {e}")
            return None
    
    def delete_data(self, app_id: str, data_key: str):
        """Delete data from Firebase Realtime Database"""
        if not self.is_initialized:
            return
        
        try:
            ref = db.reference(f'apps/{app_id}/data/{data_key}')
            ref.delete()
        except Exception as e:
            print(f"Firebase delete error: {e}")

# Singleton instance
firebase_service = FirebaseService()
