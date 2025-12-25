#!/usr/bin/env python3
"""
Quick EXE Builder - One command to build everything
"""
import subprocess
import sys
import os

def quick_build():
    """Quick build with minimal output"""
    print("🔥 Building Novrintech Desktop EXE...")
    
    # Install PyInstaller
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile", "--windowed", "--name", "NovrintechDesktop",
        "--add-data", ".env;.", "main.py"
    ]
    
    # Run build
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Build successful!")
        print("📁 EXE location: dist/NovrintechDesktop.exe")
        
        # Check file size
        exe_path = "dist/NovrintechDesktop.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📊 Size: {size_mb:.1f} MB")
        
        print("\n🎉 Ready to distribute!")
    else:
        print("❌ Build failed!")
        print(result.stderr)

if __name__ == "__main__":
    quick_build()
    input("Press Enter to exit...")