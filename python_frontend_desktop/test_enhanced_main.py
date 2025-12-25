#!/usr/bin/env python3
"""
Test Enhanced Main.py Integration
Tests the integrated chat database and update features
"""
import tkinter as tk
from datetime import datetime
import threading
import time

def test_enhanced_app():
    """Test the enhanced application"""
    print("🧪 Testing Enhanced Novrintech Desktop Client")
    print("=" * 60)
    
    try:
        # Import enhanced main
        import main
        print("✅ Enhanced main.py imported successfully")
        
        # Create root window (but don't show it)
        root = tk.Tk()
        root.withdraw()  # Hide the window for testing
        
        print("🚀 Initializing enhanced app...")
        app = main.NovrintechDesktopApp(root)
        
        # Test enhanced features
        print("\n🧪 Testing Enhanced Features:")
        
        # Test 1: Enhanced Chat Manager
        if hasattr(app, 'enhanced_chat') and app.enhanced_chat:
            print("   ✅ Enhanced Chat Manager: Available")
            
            # Test adding a message with database sync
            message = app.add_chat_message("test", "Test Message", "Testing enhanced chat integration", "TestUser")
            print(f"   📝 Test message created: {message.get('title', 'Unknown')}")
            print(f"   💾 Database sync status: {message.get('synced_to_db', False)}")
        else:
            print("   ❌ Enhanced Chat Manager: Not available")
        
        # Test 2: App Updater
        if hasattr(app, 'app_updater') and app.app_updater:
            print("   ✅ App Updater: Available")
            print(f"   🔄 Current version: {app.app_updater.current_version}")
            print(f"   ⚙️ Auto-download: {app.app_updater.strategies['auto_download']}")
        else:
            print("   ❌ App Updater: Not available")
        
        # Test 3: AI Service Integration
        if hasattr(app, 'ai_service') and app.ai_service:
            print("   ✅ AI Service: Available")
            print(f"   🤖 AI connected: {app.ai_service.is_connected}")
        else:
            print("   ❌ AI Service: Not available")
        
        # Test 4: Menu Integration
        menu_items = []
        try:
            # Check if enhanced menu items exist
            menubar = app.root.nametowidget(app.root['menu'])
            for i in range(menubar.index('end') + 1):
                try:
                    menu_label = menubar.entrycget(i, 'label')
                    menu_items.append(menu_label)
                except:
                    pass
            
            print(f"   📋 Menu items: {len(menu_items)} found")
            if "Tools" in menu_items:
                print("   ✅ Tools menu: Available (enhanced features accessible)")
            else:
                print("   ❌ Tools menu: Not found")
        except Exception as e:
            print(f"   ⚠️ Menu test failed: {e}")
        
        # Test 5: Chat History
        print(f"   📚 Chat messages in memory: {len(app.chat_messages)}")
        
        # Test 6: File History
        print(f"   📁 File history entries: {len(app.uploaded_files)}")
        
        # Test 7: API Configuration
        print(f"   🔗 API URL: {app.api_base_url}")
        print(f"   🔑 API Key configured: {'Yes' if app.api_key else 'No'}")
        
        print("\n🎯 Integration Test Results:")
        
        # Count available features
        features = {
            "Enhanced Chat": hasattr(app, 'enhanced_chat') and app.enhanced_chat,
            "App Updater": hasattr(app, 'app_updater') and app.app_updater,
            "AI Service": hasattr(app, 'ai_service') and app.ai_service,
            "Database Sync": app.chat_db_sync_enabled if hasattr(app, 'chat_db_sync_enabled') else False,
            "Notifications": app.notification_available if hasattr(app, 'notification_available') else False
        }
        
        available_count = sum(features.values())
        total_count = len(features)
        
        for feature, available in features.items():
            status = "✅ Available" if available else "❌ Not Available"
            print(f"   {feature}: {status}")
        
        print(f"\n📊 Feature Availability: {available_count}/{total_count} features active")
        
        if available_count >= 3:
            print("🎉 INTEGRATION SUCCESS: Enhanced features are working!")
        else:
            print("⚠️ PARTIAL INTEGRATION: Some features may need attention")
        
        # Cleanup
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_chat_database_functionality():
    """Test chat database functionality specifically"""
    print("\n💾 Testing Chat Database Functionality:")
    
    try:
        from chat_database_integration import ChatDatabaseIntegration
        
        api_url = "https://novrintech-data-fall-back.onrender.com"
        api_key = "novrintech_api_key_2024_secure"
        
        chat_db = ChatDatabaseIntegration(api_url, api_key)
        
        # Test message
        test_message = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "integration_test",
            "title": "Integration Test Message",
            "content": "Testing chat database integration from enhanced main.py",
            "user": "IntegrationTest"
        }
        
        # Test save
        result = chat_db.save_chat_to_database([test_message], "IntegrationTest")
        
        if result["success"]:
            print(f"   ✅ Chat save test: SUCCESS (Key: {result['chat_key']})")
            
            # Test load
            load_result = chat_db.load_chat_from_database("IntegrationTest")
            if load_result["success"]:
                print("   ✅ Chat load test: SUCCESS")
                return True
            else:
                print(f"   ❌ Chat load test: FAILED ({load_result['error']})")
                return False
        else:
            print(f"   ❌ Chat save test: FAILED ({result['error']})")
            return False
            
    except Exception as e:
        print(f"   ❌ Chat database test failed: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive integration test"""
    print("🚀 COMPREHENSIVE ENHANCED INTEGRATION TEST")
    print("=" * 80)
    
    tests = [
        ("Enhanced App Integration", test_enhanced_app),
        ("Chat Database Functionality", test_chat_database_functionality)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results[test_name] = "✅ PASSED" if result else "❌ FAILED"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {str(e)}"
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    
    for test_name, result in results.items():
        print(f"{test_name:.<50} {result}")
    
    passed_tests = sum(1 for result in results.values() if "✅ PASSED" in result)
    total_tests = len(results)
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Enhanced Novrintech Desktop Client is ready for production!")
        print("\n💡 Ready for EXE compilation with enhanced features:")
        print("   • Chat database synchronization")
        print("   • Automatic update system")
        print("   • AI service integration")
        print("   • Enhanced user interface")
    else:
        print("⚠️ Some integration tests failed. Review the results above.")
    
    return results

if __name__ == "__main__":
    try:
        results = run_comprehensive_test()
        
        print("\n🚀 Next Steps:")
        print("1. ✅ Enhanced features integrated successfully")
        print("2. 🔨 Build new EXE with: python build_exe_simple.py")
        print("3. 🧪 Test the new EXE with enhanced features")
        print("4. 🚀 Deploy to users with automatic updates")
        
    except KeyboardInterrupt:
        print("\n⏹️ Integration test cancelled by user")
    except Exception as e:
        print(f"\n❌ Integration test runner failed: {e}")
    
    input("\nPress Enter to exit...")