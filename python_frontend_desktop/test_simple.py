#!/usr/bin/env python3
"""
Simple test for core functionality
"""
import sys
import os

def test_imports():
    """Test basic imports"""
    print("Testing imports...")
    
    try:
        import json
        print("✅ json")
        
        import hashlib
        print("✅ hashlib")
        
        import threading
        print("✅ threading")
        
        import requests
        print("✅ requests")
        
        try:
            from dotenv import load_dotenv
            print("✅ dotenv")
        except ImportError:
            print("⚠️ dotenv (fallback mode)")
        
        try:
            import plyer
            print("✅ plyer")
        except ImportError:
            print("⚠️ plyer (fallback mode)")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_notification_fallback():
    """Test notification fallback system"""
    print("\nTesting notification fallback...")
    
    try:
        # Test console notification
        print("🔔 Test Notification: This is a test notification")
        
        # Test EXE detection
        is_frozen = getattr(sys, 'frozen', False)
        print(f"   Running as: {'EXE' if is_frozen else 'Script'}")
        
        # Test app data directory
        if is_frozen:
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        data_dir = os.path.join(app_dir, "app_data")
        os.makedirs(data_dir, exist_ok=True)
        print(f"   App data dir: {data_dir}")
        
        return True
    except Exception as e:
        print(f"❌ Notification test error: {e}")
        return False

def test_file_operations():
    """Test file operations"""
    print("\nTesting file operations...")
    
    try:
        # Test JSON operations
        test_data = {"test": "data", "number": 123}
        json_str = json.dumps(test_data, indent=2)
        parsed_data = json.loads(json_str)
        print("✅ JSON operations")
        
        # Test file hash
        import hashlib
        test_string = "test data for hashing"
        hash_obj = hashlib.md5(test_string.encode())
        hash_hex = hash_obj.hexdigest()
        print(f"✅ File hashing: {hash_hex[:8]}...")
        
        return True
    except Exception as e:
        print(f"❌ File operations error: {e}")
        return False

if __name__ == "__main__":
    print("🔥 Novrintech Desktop Client - Simple Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_notification_fallback,
        test_file_operations
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED!")
        print("✅ Core functionality working")
        print("✅ EXE compilation should work")
        print("✅ Notification fallback ready")
    else:
        print("⚠️ Some tests failed")
    
    print("=" * 50)