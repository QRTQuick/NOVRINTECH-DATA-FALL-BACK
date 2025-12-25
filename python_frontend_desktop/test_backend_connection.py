#!/usr/bin/env python3
"""
Test backend connection and file operations
"""
import requests
import json

def test_backend():
    """Test backend connection and file operations"""
    api_base_url = "https://novrintech-data-fall-back.onrender.com"
    api_key = "novrintech_api_key_2024_secure"
    
    print("🔥 Testing Novrintech Backend Connection")
    print("=" * 50)
    
    headers = {"X-API-KEY": api_key}
    
    # Test 1: Health check
    print("\n1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{api_base_url}/health", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: File list
    print("\n2️⃣ Testing file list endpoint...")
    try:
        response = requests.get(f"{api_base_url}/file/list", headers=headers, timeout=15)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            files = result.get("files", [])
            print(f"   Found {len(files)} files")
            
            if files:
                print("   📁 Files found:")
                for i, file_info in enumerate(files[:5]):  # Show first 5 files
                    file_id = file_info.get("file_id", "No ID")
                    file_name = file_info.get("file_name", "No Name")
                    file_size = file_info.get("file_size", 0)
                    print(f"      {i+1}. {file_name} (ID: {file_id}, Size: {file_size} bytes)")
                
                if len(files) > 5:
                    print(f"      ... and {len(files) - 5} more files")
                
                print("   ✅ File list working - download should work!")
            else:
                print("   📁 No files found - upload some files first")
                print("   ✅ File list endpoint working")
        else:
            print(f"   ❌ File list failed: {response.text}")
    except Exception as e:
        print(f"   ❌ File list error: {e}")
    
    # Test 3: Test download with first file (if available)
    print("\n3️⃣ Testing download capability...")
    try:
        response = requests.get(f"{api_base_url}/file/list", headers=headers, timeout=15)
        if response.status_code == 200:
            result = response.json()
            files = result.get("files", [])
            
            if files:
                first_file = files[0]
                file_id = first_file.get("file_id")
                file_name = first_file.get("file_name")
                
                if file_id and file_id != "Unknown":
                    print(f"   Testing download for: {file_name} (ID: {file_id})")
                    
                    # Test download endpoint (just check if it responds, don't actually download)
                    download_response = requests.head(f"{api_base_url}/file/download/{file_id}", headers=headers, timeout=10)
                    print(f"   Download endpoint status: {download_response.status_code}")
                    
                    if download_response.status_code == 200:
                        print("   ✅ Download endpoint working!")
                    else:
                        print(f"   ❌ Download endpoint failed: {download_response.status_code}")
                else:
                    print("   ⚠️ First file has no valid ID - backend issue")
            else:
                print("   📁 No files to test download with")
        else:
            print("   ❌ Cannot test download - file list failed")
    except Exception as e:
        print(f"   ❌ Download test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    print("   If file list shows files with valid IDs, download should work")
    print("   If files have 'No ID' or 'Unknown', there's a backend issue")
    print("   If no files found, upload some files first")
    print("=" * 50)

if __name__ == "__main__":
    test_backend()
    input("\nPress Enter to exit...")