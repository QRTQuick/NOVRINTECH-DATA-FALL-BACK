#!/usr/bin/env python3
"""
Fix the database issue using Neon's REST API
This will create the missing default app record directly
"""
import requests
import json
import uuid
from datetime import datetime

# Neon REST API endpoint
NEON_REST_URL = "https://ep-weathered-math-afeq5max.apirest.c-2.us-west-2.aws.neon.tech/neondb/rest/v1"

def create_default_app_via_neon_rest():
    """Create the default app record using Neon REST API"""
    print("🔧 Creating default app via Neon REST API...")
    
    try:
        # Default app data
        default_app_id = "00000000-0000-0000-0000-000000000000"
        app_data = {
            "id": default_app_id,
            "app_name": "Default Test App",
            "api_key": "novrintech_api_key_2024_secure",
            "status": "active",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # First, check if the apps table exists
        print("1️⃣ Checking if apps table exists...")
        check_table_query = {
            "query": """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'apps'
                )
            """
        }
        
        response = requests.post(f"{NEON_REST_URL}/sql", json=check_table_query)
        print(f"Table check status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            table_exists = result.get("rows", [[False]])[0][0]
            print(f"Apps table exists: {table_exists}")
            
            if not table_exists:
                print("❌ Apps table doesn't exist. Need to create schema first.")
                return create_database_schema()
        else:
            print(f"❌ Table check failed: {response.text}")
            return False
        
        # Check if default app already exists
        print("2️⃣ Checking if default app exists...")
        check_app_query = {
            "query": f"SELECT COUNT(*) FROM apps WHERE id = '{default_app_id}'"
        }
        
        response = requests.post(f"{NEON_REST_URL}/sql", json=check_app_query)
        if response.status_code == 200:
            result = response.json()
            app_count = result.get("rows", [[0]])[0][0]
            print(f"Default app count: {app_count}")
            
            if app_count > 0:
                print("✅ Default app already exists!")
                return True
        else:
            print(f"⚠️ Could not check existing app: {response.text}")
        
        # Create the default app
        print("3️⃣ Creating default app...")
        insert_query = {
            "query": f"""
                INSERT INTO apps (id, app_name, api_key, status, created_at)
                VALUES (
                    '{app_data["id"]}',
                    '{app_data["app_name"]}',
                    '{app_data["api_key"]}',
                    '{app_data["status"]}',
                    '{app_data["created_at"]}'
                )
            """
        }
        
        response = requests.post(f"{NEON_REST_URL}/sql", json=insert_query)
        print(f"Insert status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Default app created successfully!")
            
            # Verify creation
            verify_query = {
                "query": "SELECT app_name, api_key, status FROM apps WHERE id = '00000000-0000-0000-0000-000000000000'"
            }
            
            verify_response = requests.post(f"{NEON_REST_URL}/sql", json=verify_query)
            if verify_response.status_code == 200:
                result = verify_response.json()
                if result.get("rows"):
                    row = result["rows"][0]
                    print(f"✅ Verified: {row[0]} | {row[1]} | {row[2]}")
                    return True
            
            return True
        else:
            print(f"❌ Insert failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_database_schema():
    """Create the database schema if it doesn't exist"""
    print("🏗️ Creating database schema...")
    
    try:
        # Create apps table
        create_apps_table = {
            "query": """
                CREATE TABLE IF NOT EXISTS apps (
                    id UUID PRIMARY KEY,
                    app_name VARCHAR NOT NULL,
                    api_key VARCHAR UNIQUE NOT NULL,
                    status VARCHAR NOT NULL DEFAULT 'active',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """
        }
        
        response = requests.post(f"{NEON_REST_URL}/sql", json=create_apps_table)
        print(f"Create apps table: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to create apps table: {response.text}")
            return False
        
        # Create data_store table
        create_data_table = {
            "query": """
                CREATE TABLE IF NOT EXISTS data_store (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    app_id UUID NOT NULL REFERENCES apps(id),
                    data_key VARCHAR NOT NULL,
                    data_value JSONB NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """
        }
        
        response = requests.post(f"{NEON_REST_URL}/sql", json=create_data_table)
        print(f"Create data_store table: {response.status_code}")
        
        # Create file_store table
        create_file_table = {
            "query": """
                CREATE TABLE IF NOT EXISTS file_store (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    app_id UUID NOT NULL REFERENCES apps(id),
                    file_name VARCHAR NOT NULL,
                    file_path VARCHAR NOT NULL,
                    file_type VARCHAR,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """
        }
        
        response = requests.post(f"{NEON_REST_URL}/sql", json=create_file_table)
        print(f"Create file_store table: {response.status_code}")
        
        print("✅ Database schema created!")
        
        # Now create the default app
        return create_default_app_via_neon_rest()
        
    except Exception as e:
        print(f"❌ Schema creation error: {e}")
        return False

def test_upload_after_fix():
    """Test upload after creating the default app"""
    print("\n🧪 Testing upload after database fix...")
    
    try:
        api_url = "https://novrintech-data-fall-back.onrender.com"
        headers = {"X-API-KEY": "novrintech_api_key_2024_secure"}
        files = {'file': ('test_after_neon_fix.txt', 'Test after Neon database fix', 'text/plain')}
        
        response = requests.post(f"{api_url}/file/upload", headers=headers, files=files, timeout=30)
        print(f"Upload test status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🎉 SUCCESS! Upload now works!")
            print(f"File ID: {result.get('file_id')}")
            print(f"File Name: {result.get('file_name')}")
            return True
        else:
            print(f"❌ Still failing: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Fixing Neon Database via REST API")
    print("=" * 50)
    
    if create_default_app_via_neon_rest():
        print("\n✅ Database fix completed!")
        test_upload_after_fix()
    else:
        print("\n❌ Database fix failed")
        print("💡 You may need to:")
        print("   1. Check Neon REST API permissions")
        print("   2. Deploy the backend changes on Render")
        print("   3. Wait for deployment to complete")