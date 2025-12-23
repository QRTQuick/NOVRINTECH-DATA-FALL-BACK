#!/usr/bin/env python3
"""
Monitor when the deployment is complete by checking for the fix
"""
import requests
import time
import json

API_URL = "https://novrintech-data-fall-back.onrender.com"
API_KEY = "novrintech_api_key_2024_secure"

def check_deployment_status():
    """Check if the latest deployment with database fixes is live"""
    print("🔍 Monitoring deployment status...")
    
    attempt = 1
    max_attempts = 20  # 10 minutes max
    
    while attempt <= max_attempts:
        try:
            print(f"\n📡 Attempt {attempt}/{max_attempts} - Testing upload...")
            
            headers = {"X-API-KEY": API_KEY}
            files = {'file': (f'deployment_test_{attempt}.txt', f'Deployment test #{attempt}', 'text/plain')}
            
            response = requests.post(f"{API_URL}/file/upload", headers=headers, files=files, timeout=15)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"🎉 DEPLOYMENT COMPLETE! Upload works!")
                print(f"✅ File ID: {result.get('file_id')}")
                print(f"✅ File Name: {result.get('file_name')}")
                print(f"\n🚀 Your desktop app upload should now work perfectly!")
                return True
            
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', response.text)
                    print(f"❌ Error: {error_detail}")
                    
                    # Check if it's still the SSL error (old deployment)
                    if 'sslmode' in error_detail:
                        print("⏳ Still old deployment - SSL parameter issue")
                    elif 'apps' in error_detail or 'foreign key' in error_detail.lower():
                        print("⏳ New deployment but database not initialized yet")
                    else:
                        print(f"⚠️ Different error: {error_detail}")
                        
                except:
                    print(f"❌ 500 Error: {response.text}")
            
            else:
                print(f"❌ Unexpected status: {response.status_code} - {response.text}")
            
            if attempt < max_attempts:
                print("⏳ Waiting 30 seconds before next check...")
                time.sleep(30)
            
            attempt += 1
            
        except requests.exceptions.Timeout:
            print("⏳ Request timeout - backend might be starting up")
            time.sleep(30)
            attempt += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(30)
            attempt += 1
    
    print(f"\n❌ Deployment monitoring timed out after {max_attempts} attempts")
    print("💡 Please check Render dashboard manually")
    return False

if __name__ == "__main__":
    print("🚀 Deployment Monitor")
    print("=" * 50)
    print("This will check every 30 seconds until upload works")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 50)
    
    try:
        check_deployment_status()
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitor error: {e}")