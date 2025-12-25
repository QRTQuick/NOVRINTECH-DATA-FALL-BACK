#!/usr/bin/env python3
"""
Simple EXE Builder for Novrintech Desktop Client
Creates a standalone Windows executable with minimal dependencies
"""
import os
import sys
import subprocess
import shutil

def build_exe():
    """Build the EXE with minimal dependencies"""
    print("🔥 Building Novrintech Desktop Client EXE...")
    print("=" * 50)
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for folder in ["build", "dist", "__pycache__"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   Cleaned {folder}")
    
    # Remove spec files
    for spec_file in ["*.spec"]:
        import glob
        for f in glob.glob(spec_file):
            os.remove(f)
            print(f"   Cleaned {f}")
    
    # Build command with exclusions for problematic modules
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single executable
        "--windowed",                   # No console window
        "--name", "NovrintechDesktop",  # EXE name
        "--exclude-module", "kivy",     # Exclude Kivy
        "--exclude-module", "kivymd",   # Exclude KivyMD
        "--exclude-module", "pygame",   # Exclude pygame
        "--exclude-module", "numpy",    # Exclude numpy
        "--exclude-module", "matplotlib", # Exclude matplotlib
        "--exclude-module", "IPython",  # Exclude IPython
        "--exclude-module", "jupyter",  # Exclude jupyter
        "--hidden-import", "tkinter",   # Include tkinter
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.filedialog",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "tkinter.scrolledtext",
        "--hidden-import", "requests",
        "--hidden-import", "json",
        "--hidden-import", "threading",
        "--hidden-import", "hashlib",
        "--hidden-import", "datetime",
        "--hidden-import", "pathlib",
        "--hidden-import", "csv",
        "--hidden-import", "notification_system",
        "main.py"
    ]
    
    print("⚙️ Running PyInstaller...")
    print(f"Command: {' '.join(cmd[:10])}...")  # Show first 10 args
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            
            # Check if EXE was created
            exe_path = os.path.join("dist", "NovrintechDesktop.exe")
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"📁 EXE Location: {os.path.abspath(exe_path)}")
                print(f"📊 File Size: {size_mb:.1f} MB")
                print("🎉 BUILD COMPLETE!")
                return True
            else:
                print("❌ EXE file not found after build")
                return False
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout[-1000:])  # Last 1000 chars
            print("STDERR:", result.stderr[-1000:])  # Last 1000 chars
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Build timed out (5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = build_exe()
        if success:
            print("\n✅ SUCCESS: EXE ready for distribution!")
        else:
            print("\n❌ FAILED: Check errors above")
    except KeyboardInterrupt:
        print("\n⏹️ Build cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    input("\nPress Enter to exit...")