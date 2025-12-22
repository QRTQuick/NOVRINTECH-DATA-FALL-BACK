"""
Utility script to generate API keys for apps
Run this to create new API keys for client applications
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.models.app_model import App
from app.core.security import generate_api_key

def create_app_with_api_key(app_name: str) -> tuple[str, str]:
    """Create a new app with API key"""
    init_db()
    db: Session = SessionLocal()
    
    try:
        api_key = generate_api_key()
        
        new_app = App(
            app_name=app_name,
            api_key=api_key
        )
        
        db.add(new_app)
        db.commit()
        db.refresh(new_app)
        
        return str(new_app.id), api_key
    
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python api_key_generator.py <app_name>")
        sys.exit(1)
    
    app_name = sys.argv[1]
    app_id, api_key = create_app_with_api_key(app_name)
    
    print(f"✅ App Created Successfully!")
    print(f"App ID: {app_id}")
    print(f"App Name: {app_name}")
    print(f"API Key: {api_key}")
    print(f"\n🔑 Use this API key in your client applications:")
    print(f"X-API-KEY: {api_key}")