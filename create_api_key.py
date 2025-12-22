"""
Script to create API key for Novrintech Desktop Client
Run this once to add the API key to your database
"""

import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.app_model import App, AppStatus
from app.core.security import generate_api_key

def create_company_api_key():
    """Create API key for company use"""
    
    # Company API key (you can change this)
    company_api_key = "novrintech_api_key_2024_secure"
    
    db: Session = SessionLocal()
    
    try:
        # Check if API key already exists
        existing_app = db.query(App).filter(App.api_key == company_api_key).first()
        
        if existing_app:
            print(f"✅ API key already exists for app: {existing_app.app_name}")
            print(f"📋 API Key: {company_api_key}")
            print(f"🔑 App ID: {existing_app.id}")
            print(f"📅 Created: {existing_app.created_at}")
            return
        
        # Create new app with API key
        new_app = App(
            app_name="Novrintech Desktop Client",
            api_key=company_api_key,
            status=AppStatus.active
        )
        
        db.add(new_app)
        db.commit()
        db.refresh(new_app)
        
        print("🔥 SUCCESS! API key created successfully!")
        print(f"📱 App Name: {new_app.app_name}")
        print(f"📋 API Key: {company_api_key}")
        print(f"🔑 App ID: {new_app.id}")
        print(f"📅 Created: {new_app.created_at}")
        print(f"✅ Status: {new_app.status}")
        
        print("\n🚀 Your desktop app is ready to use!")
        print("💡 Use this API key in your desktop application")
        
    except Exception as e:
        print(f"❌ Error creating API key: {e}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🔥 Novrintech API Key Generator")
    print("=" * 40)
    create_company_api_key()