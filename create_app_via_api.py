#!/usr/bin/env python3
"""
Create the missing default app record via API call
This is a workaround until the backend fix is deployed
"""
import requests
import json

API_URL = "https://novrintech-data-fall-back.onrender.com"
ADMIN_KEY = "admin_super_secret_key_change_this"

def create_default_app_via_api():
    print("🔧 Creating default app via API...")
    
    # Try to use admin endpoint to create app
    try:
        # First check if admin endpoint exists
        response = requests.get(f"{API_URL}/admin/stats?admin_key={ADMIN_KEY}", timeout=10)
        
        if response.status_code != 200:
            print("❌ Admin endpoint not accessible")
            return False
        
        # Try to create app via admin endpoint (if it exists)
        app_data = {
            "app_name": "Default Test App",
            "api_key": "novrintech_api_key_2024_secure"
        }
        
        # This might not exist, but worth trying
        create_response = requests.post(
            f"{API_URL}/admin/create-app?admin_key={ADMIN_KEY}",
            json=app_data,
            timeout=15
        )
        
        print(f"Create app response: {create_response.status_code}")
        if create_response.status_code == 200:
            print("✅ Default app created successfully!")
            return True
        else:
            print(f"❌ Create app failed: {create_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_after_fix():
    """Test upload after creating the app"""
    print("\n🧪 Testing upload after fix...")
    
    try:
        headers = {"X-API-KEY": "novrintech_api_key_2024_secure"}
        files = {'file': ('test_after_fix.txt', 'Test after creating default app', 'text/plain')}
        
        response = requests.post(f"{API_URL}/file/upload", headers=headers, files=files, timeout=20)
        print(f"Upload test status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🎉 SUCCESS! Upload now works!")
            print(f"File ID: {result.get('file_id')}")
            return True
        else:
            print(f"❌ Still failing: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Attempting to fix database issue...")
    
    if create_default_app_via_api():
        test_after_fix()
    else:
        print("\n💡 Manual fix didn't work. You need to:")
        print("   1. Deploy the backend changes on Render")
        print("   2. Wait for deployment to complete")
        print("   3. Test upload again")
        print("\n🔗 Render Dashboard: https://dashboard.render.com")