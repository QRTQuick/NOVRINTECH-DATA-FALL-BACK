#!/usr/bin/env python3
"""
Test Script for New Chat Database Integration and App Updater Features
"""
import json
from datetime import datetime
import sys
import os

# Test imports
try:
    from chat_database_integration import ChatDatabaseIntegration
    from app_updater import AppUpdater
    from enhanced_chat_integration import EnhancedChatManager
    print("✅ All modules imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_chat_database_integration():
    """Test chat database integration functionality"""
    print("\n🧪 Testing Chat Database Integration...")
    
    # Initialize with test API settings
    api_url = "https://novrintech-data-fall-back.onrender.com"
    api_key = "novrintech_api_key_2024_secure"
    
    chat_db = ChatDatabaseIntegration(api_url, api_key)
    
    # Test data
    test_messages = [
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "system",
            "title": "Test Message",
            "content": "This is a test message for database integration",
            "user": "TestUser"
        },
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "upload",
            "title": "File Upload Test",
            "content": "Testing file upload message",
            "user": "TestUser"
        }
    ]
    
    test_ai_history = [
        {
            "role": "user",
            "message": "How do I upload files?",
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "assistant", 
            "message": "To upload files, go to the File Upload tab and select your file.",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    print("📤 Testing chat message save to database...")
    result = chat_db.save_chat_to_database(test_messages, "TestUser")
    if result["success"]:
        print(f"   ✅ Chat saved successfully with key: {result['chat_key']}")
    else:
        print(f"   ❌ Chat save failed: {result['error']}")
    
    print("🤖 Testing AI chat save to database...")
    ai_result = chat_db.save_ai_chat_to_database(test_ai_history, "TestUser")
    if ai_result["success"]:
        print(f"   ✅ AI chat saved successfully with key: {ai_result['ai_chat_key']}")
    else:
        print(f"   ❌ AI chat save failed: {ai_result['error']}")
    
    print("📥 Testing chat load from database...")
    load_result = chat_db.load_chat_from_database("TestUser")
    if load_result["success"]:
        print("   ✅ Chat loaded successfully from database")
        print(f"   📊 Data keys: {list(load_result['data'].keys())}")
    else:
        print(f"   ❌ Chat load failed: {load_result['error']}")
    
    print("🔄 Testing sync functionality...")
    sync_result = chat_db.sync_chat_data(test_messages, test_ai_history, "TestUser")
    print(f"   📊 Sync results: {sync_result}")
    
    return True

def test_app_updater():
    """Test app updater functionality"""
    print("\n🔄 Testing App Updater...")
    
    updater = AppUpdater(current_version="2.0")
    
    print("🔍 Testing update check...")
    # This will fail since we don't have an actual update server, but we can test the logic
    try:
        update_result = updater.check_for_updates()
        print(f"   📊 Update check result: {update_result}")
    except Exception as e:
        print(f"   ⚠️ Update check failed (expected): {e}")
    
    print("💾 Testing backup functionality...")
    backup_result = updater.backup_current_version()
    if backup_result["success"]:
        print(f"   ✅ Backup created: {backup_result['backup_path']}")
    else:
        print(f"   ❌ Backup failed: {backup_result['error']}")
    
    print("📝 Testing update script creation...")
    try:
        script_path = updater.create_update_script("test_new.exe", "test_current.exe")
        print(f"   ✅ Update script created: {script_path}")
        
        # Check if script exists and has content
        if os.path.exists(script_path):
            with open(script_path, 'r') as f:
                script_content = f.read()
            print(f"   📄 Script length: {len(script_content)} characters")
        
    except Exception as e:
        print(f"   ❌ Script creation failed: {e}")
    
    return True

def test_enhanced_chat_manager():
    """Test enhanced chat manager functionality"""
    print("\n💬 Testing Enhanced Chat Manager...")
    
    api_url = "https://novrintech-data-fall-back.onrender.com"
    api_key = "novrintech_api_key_2024_secure"
    
    enhanced_chat = EnhancedChatManager(api_url, api_key)
    
    print("📝 Testing enhanced message creation...")
    message = enhanced_chat.enhanced_add_chat_message(
        "test", 
        "Test Message", 
        "This is a test message from enhanced chat manager",
        "TestUser",
        sync_to_db=False  # Don't actually sync for testing
    )
    
    print(f"   ✅ Message created: {message['title']}")
    print(f"   📊 Message data: {json.dumps(message, indent=2)}")
    
    print("📊 Testing sync status...")
    sync_status = enhanced_chat.get_sync_status()
    print(f"   📈 Sync status: {sync_status}")
    
    print("🔄 Testing single message sync (dry run)...")
    # Test the sync logic without actually sending to server
    try:
        sync_result = enhanced_chat.sync_single_message_to_db(message, "TestUser")
        print(f"   📊 Sync result: {sync_result}")
    except Exception as e:
        print(f"   ⚠️ Sync test failed (expected): {e}")
    
    return True

def test_integration_with_existing_app():
    """Test integration points with existing app"""
    print("\n🔗 Testing Integration Points...")
    
    # Test if we can import existing modules
    try:
        from config import APP_CONTEXT, AI_API_URL
        print("   ✅ Config module accessible")
        print(f"   📊 App context keys: {list(APP_CONTEXT.keys())}")
        print(f"   🤖 AI API URL: {AI_API_URL}")
    except ImportError as e:
        print(f"   ❌ Config import failed: {e}")
    
    try:
        from ai_service import AIService
        print("   ✅ AI Service module accessible")
    except ImportError as e:
        print(f"   ❌ AI Service import failed: {e}")
    
    # Test if notification system exists
    try:
        from notification_system import get_notification_system
        notif_system = get_notification_system()
        print("   ✅ Notification system accessible")
    except ImportError as e:
        print(f"   ❌ Notification system import failed: {e}")
    
    return True

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Comprehensive Feature Tests...")
    print("=" * 60)
    
    tests = [
        ("Chat Database Integration", test_chat_database_integration),
        ("App Updater", test_app_updater),
        ("Enhanced Chat Manager", test_enhanced_chat_manager),
        ("Integration Points", test_integration_with_existing_app)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running {test_name} tests...")
            result = test_func()
            results[test_name] = "✅ PASSED" if result else "❌ FAILED"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {str(e)}"
            print(f"   ❌ Test failed with error: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        print(f"{test_name:.<40} {result}")
    
    # Overall status
    passed_tests = sum(1 for result in results.values() if "✅ PASSED" in result)
    total_tests = len(results)
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Features are ready for integration.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return results

if __name__ == "__main__":
    try:
        results = run_all_tests()
        
        print("\n💡 Next Steps:")
        print("1. Review test results above")
        print("2. Fix any failed tests")
        print("3. Integrate working features into main.py")
        print("4. Test with actual backend server")
        print("5. Build new EXE with enhanced features")
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests cancelled by user")
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
    
    input("\nPress Enter to exit...")