#!/usr/bin/env python3
"""
Test API Connections for Chat Database Integration
"""
import requests
import json
from datetime import datetime

def test_backend_api():
    """Test the main backend API"""
    print("🔗 Testing Backend API Connection...")
    
    api_url = "https://novrintech-data-fall-back.onrender.com"
    api_key = "novrintech_api_key_2024_secure"
    
    # Test health endpoint
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Backend API is online")
            print(f"   📊 Response: {response.json()}")
        else:
            print(f"   ❌ Backend API returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend API connection failed: {e}")
    
    # Test data save endpoint (for chat storage)
    try:
        headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        test_data = {
            "data_key": f"test_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "data_value": {
                "test": "This is a test chat message",
                "timestamp": datetime.now().isoformat(),
                "user": "TestUser"
            }
        }
        
        response = requests.post(f"{api_url}/data/save", headers=headers, json=test_data, timeout=10)
        if response.status_code == 200:
            print("   ✅ Data save endpoint working (chat storage ready)")
            print(f"   📊 Saved test data with key: {test_data['data_key']}")
        else:
            print(f"   ❌ Data save failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Data save test failed: {e}")

def test_ai_backend():
    """Test the AI backend API"""
    print("\n🤖 Testing AI Backend API Connection...")
    
    ai_url = "https://novrintech-ai.onrender.com"
    
    # Test AI health endpoint
    try:
        response = requests.get(f"{ai_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ AI Backend is online")
            print(f"   📊 Response: {response.json()}")
        else:
            print(f"   ❌ AI Backend returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ AI Backend connection failed: {e}")
    
    # Test AI chat endpoint
    try:
        test_message = {
            "message": "Hello, this is a test message. Please respond briefly."
        }
        
        response = requests.post(f"{ai_url}/api/chat", json=test_message, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("   ✅ AI Chat endpoint working")
                print(f"   🤖 AI Response: {data.get('reply', 'No reply')[:100]}...")
            else:
                print(f"   ❌ AI Chat failed: {data.get('error')}")
        else:
            print(f"   ❌ AI Chat returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ AI Chat test failed: {e}")

def test_chat_database_integration_live():
    """Test live chat database integration"""
    print("\n💾 Testing Live Chat Database Integration...")
    
    from chat_database_integration import ChatDatabaseIntegration
    
    api_url = "https://novrintech-data-fall-back.onrender.com"
    api_key = "novrintech_api_key_2024_secure"
    
    chat_db = ChatDatabaseIntegration(api_url, api_key)
    
    # Test saving actual chat data
    test_messages = [
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "system",
            "title": "Live Test Message",
            "content": "This is a live test of chat database integration",
            "user": "LiveTestUser"
        }
    ]
    
    print("   📤 Saving test chat to database...")
    result = chat_db.save_chat_to_database(test_messages, "LiveTestUser")
    
    if result["success"]:
        print(f"   ✅ Chat saved successfully! Key: {result['chat_key']}")
        
        # Try to load it back
        print("   📥 Loading chat back from database...")
        load_result = chat_db.load_chat_from_database("LiveTestUser")
        
        if load_result["success"]:
            print("   ✅ Chat loaded successfully from database!")
            saved_data = load_result["data"]["data_value"]
            print(f"   📊 Retrieved {len(saved_data.get('messages', []))} messages")
        else:
            print(f"   ❌ Chat load failed: {load_result['error']}")
    else:
        print(f"   ❌ Chat save failed: {result['error']}")

if __name__ == "__main__":
    print("🧪 Live API Connection Tests")
    print("=" * 50)
    
    test_backend_api()
    test_ai_backend()
    test_chat_database_integration_live()
    
    print("\n" + "=" * 50)
    print("✅ Live API tests completed!")
    print("\n💡 If all tests passed, your chat database integration is ready!")
    
    input("\nPress Enter to exit...")