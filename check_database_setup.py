#!/usr/bin/env python3
"""
Check if the database is properly set up for the upload functionality
"""
import requests
import json

API_URL = "https://novrintech-data-fall-back.onrender.com"
API_KEY = "novrintech_api_key_2024_secure"

def check_database_setup():
    print("🔍 Database Setup Diagnostic")
    print("=" * 50)
    
    # Check if we can access admin endpoints to see database status
    print("\n1️⃣ Checking admin stats...")
    try:
        # Try the admin endpoint (if available)
        response = requests.get(f"{API_URL}/admin/stats?admin_key=admin_super_secret_key_change_this", timeout=10)
        print(f"Admin endpoint status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"📊 Database stats: {json.dumps(stats, indent=2)}")
        else:
            print(f"Admin endpoint response: {response.text}")
    except Exception as e:
        print(f"❌ Admin endpoint error: {e}")
    
    # Check if we can create a simple data record (this should work)
    print("\n2️⃣ Testing simple data creation...")
    try:
        headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
        test_data = {
            "data_key": "diagnostic_test",
            "data_value": {"test": True, "timestamp": "2024-12-22"}
        }
        
        response = requests.post(f"{API_URL}/data/save", headers=headers, json=test_data, timeout=15)
        print(f"Data save status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Data operations work - database connection is good")
            
            # Try to read it back
            read_response = requests.get(f"{API_URL}/data/read/diagnostic_test", headers=headers, timeout=10)
            print(f"Data read status: {read_response.status_code}")
            if read_response.status_code == 200:
                print("✅ Data read works too")
            else:
                print(f"❌ Data read failed: {read_response.text}")
        else:
            print(f"❌ Data save failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Data operation error: {e}")
    
    # Test file upload with detailed error
    print("\n3️⃣ Testing file upload with error details...")
    try:
        headers = {"X-API-KEY": API_KEY}
        files = {'file': ('diagnostic.txt', 'Database diagnostic test file', 'text/plain')}
        
        response = requests.post(f"{API_URL}/file/upload", headers=headers, files=files, timeout=20)
        print(f"File upload status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File upload works! File ID: {result.get('file_id')}")
        else:
            print(f"❌ File upload failed")
            print(f"Response text: {response.text}")
            
            # Try to get more details
            try:
                error_json = response.json()
                print(f"Error JSON: {json.dumps(error_json, indent=2)}")
            except:
                print("Could not parse error as JSON")
                
    except Exception as e:
        print(f"❌ File upload error: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Diagnostic Complete!")
    
    print("\n💡 Likely Issues:")
    print("   • Missing 'apps' table or default app record")
    print("   • Foreign key constraint preventing file_store inserts")
    print("   • Database schema not fully initialized")
    print("   • Backend code changes not deployed yet")
    
    print("\n🛠️ Solutions:")
    print("   1. Deploy the backend changes (creates default app automatically)")
    print("   2. Run database initialization script")
    print("   3. Manually create the default app record")

if __name__ == "__main__":
    check_database_setup()