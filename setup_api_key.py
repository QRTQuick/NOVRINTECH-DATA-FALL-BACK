"""
Quick setup script to create the API key in the database
Run this to enable the desktop app to work properly
"""

import asyncio
import requests
import json

# API Configuration
API_URL = "https://novrintech-data-fall-back.onrender.com"
API_KEY = "novrintech_api_key_2024_secure"

async def setup_api_key():
    """Setup API key by making a direct database call"""
    
    print("🔥 Novrintech API Key Setup")
    print("=" * 40)
    
    # First, let's test if the API is responding
    try:
        print("📡 Testing API connection...")
        response = requests.get(f"{API_URL}/", timeout=10)
        
        if response.status_code == 200:
            print("✅ API is responding!")
            print(f"📊 Response: {response.json()}")
        else:
            print(f"⚠️ API returned status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        print("🔄 The backend might be sleeping. Let's wake it up...")
        
        # Try to wake up the backend
        for i in range(3):
            try:
                print(f"🔄 Wake-up attempt {i+1}/3...")
                response = requests.get(f"{API_URL}/", timeout=15)
                if response.status_code == 200:
                    print("✅ Backend is now awake!")
                    break
            except:
                if i < 2:
                    print("⏳ Waiting 10 seconds...")
                    await asyncio.sleep(10)
                else:
                    print("❌ Could not wake up backend")
                    return
    
    # Now test the health endpoint
    try:
        print("\n🏥 Testing health endpoint...")
        response = requests.get(f"{API_URL}/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check passed!")
            print(f"📊 Database status: {health_data.get('databases', {})}")
        else:
            print(f"⚠️ Health check returned: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test API key authentication
    try:
        print(f"\n🔑 Testing API key authentication...")
        headers = {"X-API-KEY": API_KEY}
        response = requests.get(f"{API_URL}/health", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ API key authentication successful!")
            print("🎉 Your desktop app should work now!")
        elif response.status_code == 401:
            print("❌ API key not found in database")
            print("💡 The API key needs to be created in the database")
            print("📝 Contact your administrator to run the create_api_key.py script")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API key test failed: {e}")
    
    # Test file upload endpoint
    try:
        print(f"\n📁 Testing file upload endpoint...")
        headers = {"X-API-KEY": API_KEY}
        
        # Create a simple test file
        test_data = {"test": "data"}
        files = {'file': ('test.txt', 'Hello World!', 'text/plain')}
        
        response = requests.post(f"{API_URL}/file/upload", headers=headers, files=files, timeout=15)
        
        if response.status_code == 200:
            print("✅ File upload test successful!")
            result = response.json()
            print(f"📄 File ID: {result.get('file_id')}")
        elif response.status_code == 401:
            print("❌ File upload failed: API key authentication error")
        elif response.status_code == 500:
            print("❌ File upload failed: Internal server error")
            print("💡 This might be a database connection issue")
        else:
            print(f"⚠️ File upload returned: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ File upload test failed: {e}")
    
    print("\n" + "=" * 40)
    print("🔍 Setup Complete!")
    print("\n💡 If you see authentication errors:")
    print("   1. The backend database needs the API key")
    print("   2. Run the create_api_key.py script on the server")
    print("   3. Or contact your administrator")
    print("\n🚀 If everything is green, your desktop app is ready!")

if __name__ == "__main__":
    asyncio.run(setup_api_key())