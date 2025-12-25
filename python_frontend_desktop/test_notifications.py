#!/usr/bin/env python3
"""
Test script for EXE-safe notification system
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_notification_system():
    """Test the notification system"""
    print("🧪 Testing EXE-safe notification system...")
    
    try:
        from notification_system import get_notification_system, show_notification
        
        print("✅ Notification system imported successfully")
        
        # Get notification system
        notif_system = get_notification_system()
        print(f"✅ Notification system initialized: {type(notif_system).__name__}")
        
        # Test basic notification
        print("📤 Testing basic notification...")
        result1 = notif_system.show_notification("Test Title", "This is a test message")
        print(f"   Result: {'✅ Success' if result1 else '❌ Failed'}")
        
        # Test global function
        print("📤 Testing global notification function...")
        result2 = show_notification("Global Test", "This is a global function test")
        print(f"   Result: {'✅ Success' if result2 else '❌ Failed'}")
        
        # Test with different parameters
        print("📤 Testing notification with timeout...")
        result3 = notif_system.show_notification("Timeout Test", "This notification has a 5 second timeout", 5)
        print(f"   Result: {'✅ Success' if result3 else '❌ Failed'}")
        
        print("\n🎉 All notification tests completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_main_app_imports():
    """Test main app imports"""
    print("\n🧪 Testing main app imports...")
    
    try:
        import tkinter as tk
        print("✅ tkinter imported")
        
        from tkinter import ttk, filedialog, messagebox, scrolledtext
        print("✅ tkinter components imported")
        
        import requests
        print("✅ requests imported")
        
        import json
        print("✅ json imported")
        
        try:
            from dotenv import load_dotenv
            print("✅ dotenv imported")
        except ImportError:
            print("⚠️ dotenv not available (will use fallback)")
        
        try:
            import plyer
            print("✅ plyer imported")
        except ImportError:
            print("⚠️ plyer not available (will use fallback)")
        
        print("✅ All main app imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_exe_compatibility():
    """Test EXE compatibility features"""
    print("\n🧪 Testing EXE compatibility features...")
    
    try:
        # Test frozen detection
        is_frozen = getattr(sys, 'frozen', False)
        print(f"   Frozen state: {'EXE mode' if is_frozen else 'Script mode'}")
        
        # Test app data directory creation
        if is_frozen:
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        data_dir = os.path.join(app_dir, "app_data")
        os.makedirs(data_dir, exist_ok=True)
        print(f"   App data directory: {data_dir}")
        print("✅ EXE compatibility features working")
        
        return True
        
    except Exception as e:
        print(f"❌ EXE compatibility error: {e}")
        return False

if __name__ == "__main__":
    print("🔥 Novrintech Desktop Client - Notification & EXE Test")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Main App Imports", test_main_app_imports),
        ("Notification System", test_notification_system),
        ("EXE Compatibility", test_exe_compatibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Application ready for EXE compilation!")
    else:
        print("⚠️ Some tests failed - check the errors above")
    
    print("=" * 60)
    input("\nPress Enter to exit...")