#!/usr/bin/env python3
"""
Test the new file manager endpoints
"""
import requests
import json

API_URL = "https://novrintech-data-fall-back.onrender.com"
API_KEY = "novrintech_api_key_2024_secure"

def test_file_manager():
    print("🧪 Testing File Manager Endpoints")
    print("=" * 50)
    
    headers = {"X-API-KEY": API_KEY}
    
    # Test 1: Upload a test file first
    print("\n1️⃣ Uploading test file...")
    try:
        files = {'file': ('file_manager_test.txt', 'This is a test file for file manager', 'text/plain')}
        response = requests.post(f"{API_URL}/file/upload", headers=headers, files=files, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            test_file_id = result.get('file_id')
            print(f"✅ Upload successful! File ID: {test_file_id}")
        else:
            print(f"❌ Upload failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Test 2: List files
    print("\n2️⃣ Testing file list...")
    try:
        response = requests.get(f"{API_URL}/file/list", headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            files = result.get('files', [])
            print(f"✅ List successful! Found {len(files)} files")
            
            for file_info in files[:3]:  # Show first 3 files
                print(f"   📄 {file_info.get('file_name')} ({file_info.get('file_size', 0)} bytes)")
        else:
            print(f"❌ List failed: {response.text}")
    except Exception as e:
        print(f"❌ List error: {e}")
    
    # Test 3: Get file info
    print(f"\n3️⃣ Testing file info for {test_file_id}...")
    try:
        response = requests.get(f"{API_URL}/file/read/{test_file_id}", headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File info successful!")
            print(f"   Name: {result.get('file_name')}")
            print(f"   Type: {result.get('file_type')}")
            print(f"   Created: {result.get('created_at')}")
        else:
            print(f"❌ File info failed: {response.text}")
    except Exception as e:
        print(f"❌ File info error: {e}")
    
    # Test 4: Download file
    print(f"\n4️⃣ Testing file download for {test_file_id}...")
    try:
        response = requests.get(f"{API_URL}/file/download/{test_file_id}", headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            print(f"✅ Download successful!")
            print(f"   Content: {content[:50]}...")
        else:
            print(f"❌ Download failed: {response.text}")
    except Exception as e:
        print(f"❌ Download error: {e}")
    
    # Test 5: Delete file (optional - uncomment to test)
    print(f"\n5️⃣ Testing file delete for {test_file_id}...")
    delete_test = input("Delete the test file? (y/N): ").lower().strip()
    
    if delete_test == 'y':
        try:
            response = requests.delete(f"{API_URL}/file/delete/{test_file_id}", headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Delete successful! {result.get('message')}")
            else:
                print(f"❌ Delete failed: {response.text}")
        except Exception as e:
            print(f"❌ Delete error: {e}")
    else:
        print("⏭️ Skipping delete test")
    
    print("\n" + "=" * 50)
    print("🎉 File Manager Test Complete!")
    print("\n💡 If all tests pass, your desktop app file manager should work perfectly!")

if __name__ == "__main__":
    test_file_manager()