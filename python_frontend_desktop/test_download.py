#!/usr/bin/env python3
"""
Test actual file download
"""
import requests
import os

def test_download():
    """Test actual file download"""
    api_base_url = "https://novrintech-data-fall-back.onrender.com"
    api_key = "novrintech_api_key_2024_secure"
    
    print("🔥 Testing File Download")
    print("=" * 40)
    
    headers = {"X-API-KEY": api_key}
    
    # Get file list first
    print("1️⃣ Getting file list...")
    try:
        response = requests.get(f"{api_base_url}/file/list", headers=headers, timeout=15)
        if response.status_code == 200:
            result = response.json()
            files = result.get("files", [])
            
            if files:
                first_file = files[0]
                file_id = first_file.get("file_id")
                file_name = first_file.get("file_name")
                
                print(f"   Found file: {file_name}")
                print(f"   File ID: {file_id}")
                
                # Test actual download
                print("\n2️⃣ Testing download...")
                download_response = requests.get(f"{api_base_url}/file/download/{file_id}", headers=headers, timeout=30)
                
                print(f"   Status: {download_response.status_code}")
                
                if download_response.status_code == 200:
                    # Save to test file
                    test_filename = f"test_download_{file_name}"
                    with open(test_filename, 'wb') as f:
                        f.write(download_response.content)
                    
                    file_size = len(download_response.content)
                    print(f"   ✅ Download successful!")
                    print(f"   File size: {file_size} bytes")
                    print(f"   Saved as: {test_filename}")
                    
                    # Clean up test file
                    try:
                        os.remove(test_filename)
                        print(f"   🧹 Cleaned up test file")
                    except:
                        pass
                    
                else:
                    print(f"   ❌ Download failed: {download_response.status_code}")
                    print(f"   Error: {download_response.text}")
            else:
                print("   📁 No files found to test download")
        else:
            print(f"   ❌ File list failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    test_download()
    input("Press Enter to exit...")