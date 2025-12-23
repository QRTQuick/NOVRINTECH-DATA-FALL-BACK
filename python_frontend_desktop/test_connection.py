"""
Simple test script to debug the upload issue
Run this to see what's happening with the API
"""

import requests
import json

# API Configuration
API_URL = "https://novrintech-data-fall-back.onrender.com"
API_KEY = "novrintech_api_key_2024_secure"

def test_api():
    print("🔥 Novrintech Desktop App - Connection Test")
    print("=" * 50)
    
    # Test 1: Basic API connection
    print("\n1️⃣ Testing basic API connection...")
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Health check without API key
    print("\n2️⃣ Testing health endpoint (no auth)...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print(f"📄 Response: {response.json()}")
        else:
            print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Health check with API key
    print("\n3️⃣ Testing health endpoint (with API key)...")
    try:
        headers = {"X-API-KEY": API_KEY}
        response = requests.get(f"{API_URL}/health", headers=headers, timeout=10)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print(f"📄 Response: {response.json()}")
        else:
            print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: File upload test
    print("\n4️⃣ Testing file upload...")
    try:
        headers = {"X-API-KEY": API_KEY}
        files = {'file': ('test.txt', 'Hello World Test!', 'text/plain')}
        
        response = requests.post(f"{API_URL}/file/upload", headers=headers, files=files, timeout=15)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🎉 Upload successful!")
            print(f"📄 File ID: {result.get('file_id')}")
            print(f"📄 File Name: {result.get('file_name')}")
        else:
            print(f"❌ Upload failed!")
            print(f"📄 Response: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"🔍 Error details: {error_data}")
            except:
                pass
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Data operations test
    print("\n5️⃣ Testing data save...")
    try:
        headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
        data = {
            "data_key": "test_key",
            "data_value": {"message": "Hello from test!", "timestamp": "2024-12-22"}
        }
        
        response = requests.post(f"{API_URL}/data/save", headers=headers, json=data, timeout=15)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🎉 Data save successful!")
            print(f"📄 Response: {result}")
        else:
            print(f"❌ Data save failed!")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Test Complete!")
    print("\n💡 Common Issues:")
    print("   • 401 Unauthorized: API key not in database")
    print("   • 500 Internal Error: Database connection issue")
    print("   • Timeout: Backend is sleeping (wait and retry)")
    print("\n🚀 If all tests pass, the desktop app should work!")

if __name__ == "__main__":
    test_api()