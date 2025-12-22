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
                print("✅ Firebase initialized successfully")
            else:
                print(f"⚠️ Firebase credentials not found at {settings.FIREBASE_CREDENTIALS_PATH}")
                print("🔄 Firebase features will be disabled, PostgreSQL will work normally")
                self.is_initialized = False
        except Exception as e:
            print(f"⚠️ Firebase initialization error: {e}")
            print("🔄 Firebase features will be disabled, PostgreSQL will work normally")
            self.is_initialized = False
    
    def save_data(self, app_id: str, data_key: str, data_value: Dict[str, Any]):
        """Save data to Firebase Realtime Database"""
        if not self.is_initialized:
            print("⚠️ Firebase not initialized, skipping Firebase sync")
            return
        
        try:
            ref = db.reference(f'apps/{app_id}/data/{data_key}')
            ref.set(data_value)
            print(f"✅ Data synced to Firebase: {data_key}")
        except Exception as e:
            print(f"⚠️ Firebase save error: {e}")
    
    def get_data(self, app_id: str, data_key: str) -> Optional[Dict[str, Any]]:
        """Get data from Firebase Realtime Database"""
        if not self.is_initialized:
            print("⚠️ Firebase not initialized, cannot fallback to Firebase")
            return None
        
        try:
            ref = db.reference(f'apps/{app_id}/data/{data_key}')
            data = ref.get()
            if data:
                print(f"✅ Data retrieved from Firebase: {data_key}")
            return data
        except Exception as e:
            print(f"⚠️ Firebase get error: {e}")
            return None
    
    def delete_data(self, app_id: str, data_key: str):
        """Delete data from Firebase Realtime Database"""
        if not self.is_initialized:
            print("⚠️ Firebase not initialized, skipping Firebase delete")
            return
        
        try:
            ref = db.reference(f'apps/{app_id}/data/{data_key}')
            ref.delete()
            print(f"✅ Data deleted from Firebase: {data_key}")
        except Exception as e:
            print(f"⚠️ Firebase delete error: {e}")

# Singleton instance
firebase_service = FirebaseService()
