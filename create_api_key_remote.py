"""
Remote API Key Creation Script
This creates the API key directly in the deployed database via HTTP
"""

import requests
import json

# Configuration
API_URL = "https://novrintech-data-fall-back.onrender.com"
API_KEY = "novrintech_api_key_2024_secure"

def create_api_key_remote():
    print("🔥 Creating API Key in Remote Database")
    print("=" * 45)
    
    # Since we can't directly access the database, let's try a different approach
    # We'll create a special admin endpoint call
    
    print("📡 Testing current API status...")
    
    try:
        # Test basic connection
        response = requests.get(f"{API_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ API is responding")
        
        # Test health
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Database status: {health.get('databases', {}).get('postgresql', 'unknown')}")
        
        # The issue is that the API key middleware is blocking all requests
        # Let's check if there's a way to bypass this or if we need to create the key differently
        
        print("\n🔑 Testing API key authentication...")
        headers = {"X-API-KEY": API_KEY}
        response = requests.get(f"{API_URL}/health", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ API key already works!")
            return True
        elif response.status_code == 401:
            print("❌ API key not found in database")
            print("💡 Need to create the API key in the database")
        
        # Since we can't create the key remotely due to middleware blocking,
        # let's provide instructions for manual creation
        print("\n" + "=" * 45)
        print("🛠️  MANUAL SETUP REQUIRED")
        print("=" * 45)
        print("\nThe API key needs to be created directly in the database.")
        print("Here are the options:")
        print("\n1️⃣ SSH into your Render deployment and run:")
        print("   python create_api_key.py")
        print("\n2️⃣ Or add this SQL directly to your Neon database:")
        print(f"""
   INSERT INTO apps (id, app_name, api_key, status, created_at) 
   VALUES (
       gen_random_uuid(), 
       'Novrintech Desktop Client', 
       '{API_KEY}', 
       'active', 
       NOW()
   );
        """)
        print("\n3️⃣ Or temporarily disable API key middleware:")
        print("   - Comment out APIKeyMiddleware in main.py")
        print("   - Deploy and create key via API")
        print("   - Re-enable middleware")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_api_key_remote()