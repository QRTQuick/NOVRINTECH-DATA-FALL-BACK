#!/usr/bin/env python3
"""
Test the upload functionality locally
"""
import asyncio
import os
import tempfile
from fastapi.testclient import TestClient
from app.main import app

def test_upload_locally():
    """Test upload with TestClient"""
    client = TestClient(app)
    
    # Create a test file
    test_content = b"This is a test file for local upload testing"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file.write(test_content)
        temp_file_path = temp_file.name
    
    try:
        # Test upload
        with open(temp_file_path, "rb") as f:
            response = client.post(
                "/file/upload",
                files={"file": ("test.txt", f, "text/plain")},
                headers={"X-API-KEY": "novrintech_api_key_2024_secure"}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json() if response.status_code == 200 else response.text}")
        
        return response.status_code == 200
        
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    print("🧪 Testing upload locally...")
    success = test_upload_locally()
    print(f"✅ Test {'PASSED' if success else 'FAILED'}")