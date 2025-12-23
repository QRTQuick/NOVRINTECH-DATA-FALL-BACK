#!/usr/bin/env python3
"""
Debug script to test file upload functionality
"""
import requests
import json
import os

# Configuration
API_BASE_URL = "https://novrintech-data-fall-back.onrender.com"
API_KEY = "novrintech_api_key_2024_secure"

def test_health():
    """Test if the API is responding"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        print(f"Health check: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_upload_without_auth():
    """Test upload without authentication"""
    print("\n🔍 Testing upload without authentication...")
    
    # Create a test file
    test_content = "This is a test file for upload debugging"
    test_filename = "test_upload.txt"
    
    with open(test_filename, 'w') as f:
        f.write(test_content)
    
    try:
        with open(test_filename, 'rb') as f:
            files = {'file': (test_filename, f, 'text/plain')}
            response = requests.post(f"{API_BASE_URL}/file/upload", files=files, timeout=30)
        
        print(f"Upload without auth: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Upload without auth failed: {e}")
    finally:
        # Clean up test file
        if os.path.exists(test_filename):
            os.remove(test_filename)

def test_upload_with_auth():
    """Test upload with authentication"""
    print("\n🔍 Testing upload with authentication...")
    
    # Create a test file
    test_content = "This is a test file for upload debugging with auth"
    test_filename = "test_upload_auth.txt"
    
    with open(test_filename, 'w') as f:
        f.write(test_content)
    
    try:
        headers = {"X-API-KEY": API_KEY}
        with open(test_filename, 'rb') as f:
            files = {'file': (test_filename, f, 'text/plain')}
            response = requests.post(f"{API_BASE_URL}/file/upload", headers=headers, files=files, timeout=30)
        
        print(f"Upload with auth: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful! File ID: {result.get('file_id')}")
        
    except Exception as e:
        print(f"❌ Upload with auth failed: {e}")
    finally:
        # Clean up test file
        if os.path.exists(test_filename):
            os.remove(test_filename)

def test_root_endpoint():
    """Test the root endpoint to see API info"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        print(f"Root endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"API Info: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting upload debug tests...")
    print(f"API URL: {API_BASE_URL}")
    print(f"API Key: {API_KEY}")
    
    # Run tests
    if test_health():
        test_root_endpoint()
        test_upload_without_auth()
        test_upload_with_auth()
    else:
        print("❌ API is not responding, skipping upload tests")
    
    print("\n✅ Debug tests completed!")