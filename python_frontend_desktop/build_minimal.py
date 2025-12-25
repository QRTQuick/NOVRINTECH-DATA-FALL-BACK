#!/usr/bin/env python3
"""
Build script for minimal Novrintech Desktop Client
"""
import os
import sys
import subprocess
import shutil

def build_minimal_exe():
    """Build minimal EXE"""
    print("🔥 Building Minimal Novrintech Desktop Client...")
    print("=" * 50)
    
    # Clean previous builds
    print("🧹 Cleaning...")
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    # Simple build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "NovrintechDesktop",
        "--exclude-module", "kivy",
        "--exclude-module", "kivymd", 
        "--exclude-module", "pygame",
        "--exclude-module", "numpy",
        "--exclude-module", "matplotlib",
        "--exclude-module", "IPython",
        "--exclude-module", "jupyter",
        "main_minimal.py"
    ]
    
    print("⚙️ Building...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        
        exe_path = os.path.join("dist", "NovrintechDesktop.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 EXE: {exe_path}")
            print(f"📊 Size: {size_mb:.1f} MB")
            print("🎉 DONE!")
        
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print("Error:", e.stderr)

if __name__ == "__main__":
    build_minimal_exe()
    input("Press Enter to exit...")