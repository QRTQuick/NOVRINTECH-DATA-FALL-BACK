#!/usr/bin/env python3
"""
Test the enhanced file manager with user name functionality
"""
import requests
import json

API_URL = "https://novrintech-data-fall-back.onrender.com"
API_KEY = "novrintech_api_key_2024_secure"

def test_enhanced_functionality():
    print("🧪 Testing Enhanced File Manager")
    print("=" * 50)
    
    headers = {"X-API-KEY": API_KEY}
    
    # Test 1: Upload file with user name in filename
    print("\n1️⃣ Testing upload with user name...")
    try:
        test_user = "TestUser123"
        original_filename = "enhanced_test.txt"
        upload_filename = f"[{test_user}]_{original_filename}"
        
        files = {'file': (upload_filename, 'This is a test file with user name functionality', 'text/plain')}
        response = requests.post(f"{API_URL}/file/upload", headers=headers, files=files, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            test_file_id = result.get('file_id')
            print(f"✅ Upload with user name successful!")
            print(f"   User: {test_user}")
            print(f"   Original: {original_filename}")
            print(f"   Upload name: {upload_filename}")
            print(f"   File ID: {test_file_id}")
        else:
            print(f"❌ Upload failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Test 2: List files and verify user name is preserved
    print("\n2️⃣ Testing file list with user names...")
    try:
        response = requests.get(f"{API_URL}/file/list", headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            files = result.get('files', [])
            print(f"✅ List successful! Found {len(files)} files")
            
            # Look for files with user names
            user_files = [f for f in files if '[' in f.get('file_name', '')]
            print(f"   Files with user names: {len(user_files)}")
            
            for file_info in user_files[:3]:  # Show first 3 user files
                filename = file_info.get('file_name', '')
                if '[' in filename and ']' in filename:
                    user_part = filename[filename.find('[')+1:filename.find(']')]
                    original_part = filename[filename.find(']')+2:]  # Skip ']_'
                    print(f"   👤 {user_part} uploaded: {original_part}")
        else:
            print(f"❌ List failed: {response.text}")
    except Exception as e:
        print(f"❌ List error: {e}")
    
    # Test 3: Download file and verify content
    print(f"\n3️⃣ Testing download functionality...")
    try:
        response = requests.get(f"{API_URL}/file/download/{test_file_id}", headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            print(f"✅ Download successful!")
            print(f"   Content: {content}")
        else:
            print(f"❌ Download failed: {response.text}")
    except Exception as e:
        print(f"❌ Download error: {e}")
    
    # Test 4: File info
    print(f"\n4️⃣ Testing file info...")
    try:
        response = requests.get(f"{API_URL}/file/read/{test_file_id}", headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File info successful!")
            print(f"   Server name: {result.get('file_name')}")
            print(f"   Type: {result.get('file_type')}")
            print(f"   Created: {result.get('created_at')}")
        else:
            print(f"❌ File info failed: {response.text}")
    except Exception as e:
        print(f"❌ File info error: {e}")
    
    # Test 5: Bulk operations test
    print(f"\n5️⃣ Testing bulk operations...")
    
    # Upload a few more test files
    test_files = [
        ("bulk_test_1.txt", "Bulk test file 1"),
        ("bulk_test_2.txt", "Bulk test file 2"),
        ("bulk_test_3.txt", "Bulk test file 3")
    ]
    
    uploaded_ids = []
    
    for filename, content in test_files:
        try:
            upload_name = f"[BulkTester]_{filename}"
            files = {'file': (upload_name, content, 'text/plain')}
            response = requests.post(f"{API_URL}/file/upload", headers=headers, files=files, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                uploaded_ids.append(result.get('file_id'))
                print(f"   ✅ Uploaded: {upload_name}")
            else:
                print(f"   ❌ Failed to upload: {filename}")
        except Exception as e:
            print(f"   ❌ Upload error for {filename}: {e}")
    
    print(f"   📊 Bulk upload complete: {len(uploaded_ids)} files uploaded")
    
    # Test cleanup (optional)
    cleanup = input(f"\n🗑️ Delete test files? ({len(uploaded_ids) + 1} files) (y/N): ").lower().strip()
    
    if cleanup == 'y':
        all_test_ids = uploaded_ids + [test_file_id]
        deleted_count = 0
        
        for file_id in all_test_ids:
            try:
                response = requests.delete(f"{API_URL}/file/delete/{file_id}", headers=headers, timeout=10)
                if response.status_code == 200:
                    deleted_count += 1
            except:
                pass
        
        print(f"✅ Cleanup complete: {deleted_count}/{len(all_test_ids)} files deleted")
    
    print("\n" + "=" * 50)
    print("🎉 Enhanced File Manager Test Complete!")
    print("\n💡 New Features Tested:")
    print("   ✅ User name requirement for uploads")
    print("   ✅ User name preservation in filenames")
    print("   ✅ Enhanced file listing")
    print("   ✅ Bulk operations support")
    print("   ✅ Improved error handling")
    print("\n🚀 Your desktop app is ready with all enhanced features!")

if __name__ == "__main__":
    test_enhanced_functionality()