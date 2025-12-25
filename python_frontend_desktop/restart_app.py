#!/usr/bin/env python3
"""
Clean restart of the Novrintech Desktop App
"""
import os
import sys
import subprocess
import time

def clean_restart():
    """Clean restart of the app"""
    print("🔄 Restarting Novrintech Desktop App...")
    
    # Clean Python cache
    print("   🧹 Cleaning Python cache...")
    try:
        import shutil
        if os.path.exists("__pycache__"):
            shutil.rmtree("__pycache__")
        print("   ✅ Cache cleaned")
    except:
        print("   ⚠️ Cache cleaning skipped")
    
    # Wait a moment
    time.sleep(1)
    
    # Start the app
    print("   🚀 Starting app...")
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("   ⏹️ App closed by user")
    except Exception as e:
        print(f"   ❌ App error: {e}")

if __name__ == "__main__":
    clean_restart()