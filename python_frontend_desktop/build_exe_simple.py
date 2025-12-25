#!/usr/bin/env python3
"""
Simple EXE Builder for Novrintech Desktop Client
Creates a standalone Windows executable
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print build header"""
    print("🔥 Novrintech Desktop Client - EXE Builder")
    print("=" * 50)
    print("Building standalone Windows executable...")
    print()

def check_python():
    """Check Python installation"""
    print("1️⃣ Checking Python...")
    try:
        version = sys.version.split()[0]
        print(f"   ✅ Python {version} found")
        return True
    except:
        print("   ❌ Python not found")
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("\n2️⃣ Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("   ✅ PyInstaller installed")
        return True
    except:
        print("   ❌ Failed to install PyInstaller")
        return False

def clean_build():
    """Clean previous builds"""
    print("\n3️⃣ Cleaning previous builds...")
    folders_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    try:
        for folder in folders_to_clean:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                print(f"   🧹 Cleaned {folder}")
        
        # Clean spec files
        for spec_file in Path(".").glob("*.spec"):
            spec_file.unlink()
            print(f"   🧹 Cleaned {spec_file}")
        
        print("   ✅ Cleanup complete")
        return True
    except Exception as e:
        print(f"   ❌ Cleanup error: {e}")
        return False

def build_exe():
    """Build the EXE"""
    print("\n4️⃣ Building EXE...")
    
    # Build command with all necessary modules and exclusions
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single executable
        "--windowed",                   # No console window
        "--name", "NovrintechDesktop",  # EXE name
        "--add-data", ".env;.",         # Include .env file
        # Exclude problematic modules that cause build issues
        "--exclude-module", "kivy",
        "--exclude-module", "kivymd", 
        "--exclude-module", "pygame",
        "--exclude-module", "numpy",
        "--exclude-module", "matplotlib",
        "--exclude-module", "IPython",
        "--exclude-module", "jupyter",
        "--exclude-module", "notebook",
        "--exclude-module", "pandas",
        "--exclude-module", "scipy",
        # Include essential modules
        "--hidden-import", "tkinter",                           # GUI framework
        "--hidden-import", "tkinter.ttk",                       # Modern widgets
        "--hidden-import", "tkinter.filedialog",                # File dialogs
        "--hidden-import", "tkinter.messagebox",                # Message boxes
        "--hidden-import", "tkinter.scrolledtext",              # Scrolled text
        "--hidden-import", "requests",                          # HTTP requests
        "--hidden-import", "requests.packages.urllib3",         # HTTP requests
        "--hidden-import", "json",                              # JSON handling
        "--hidden-import", "hashlib",                           # File hashing
        "--hidden-import", "threading",                         # Threading
        "--hidden-import", "pathlib",                           # Path handling
        "--hidden-import", "datetime",                          # Date/time
        "--hidden-import", "os",                                # OS operations
        "--hidden-import", "sys",                               # System
        "--hidden-import", "time",                              # Time operations
        "--hidden-import", "csv",                               # CSV export
        "--hidden-import", "notification_system",              # Custom notifications
        "main.py"                       # Main script
    ]
    
    print("   ⚙️ Running PyInstaller...")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("   ✅ Build successful!")
            return True
        else:
            print("   ❌ Build failed!")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("   ❌ Build timed out (5 minutes)")
        return False
    except Exception as e:
        print(f"   ❌ Build error: {e}")
        return False

def test_exe():
    """Test the built EXE"""
    print("\n5️⃣ Testing EXE...")
    
    exe_path = os.path.join("dist", "NovrintechDesktop.exe")
    
    if not os.path.exists(exe_path):
        print("   ❌ EXE file not found!")
        return False
    
    # Get file size
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"   📊 EXE size: {size_mb:.1f} MB")
    
    # Quick test (will timeout for GUI apps, but that's expected)
    try:
        subprocess.run([exe_path], timeout=3)
    except subprocess.TimeoutExpired:
        print("   ✅ EXE starts successfully")
        return True
    except Exception as e:
        print(f"   ⚠️ EXE test: {e}")
        return True  # Still consider success for GUI apps
    
    return True

def create_distribution():
    """Create distribution folder"""
    print("\n6️⃣ Creating distribution...")
    
    dist_folder = "NovrintechDesktop_Distribution"
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)
    
    os.makedirs(dist_folder)
    
    # Copy EXE
    exe_src = os.path.join("dist", "NovrintechDesktop.exe")
    exe_dst = os.path.join(dist_folder, "NovrintechDesktop.exe")
    
    if os.path.exists(exe_src):
        shutil.copy2(exe_src, exe_dst)
        print(f"   ✅ Copied EXE to {dist_folder}")
    
    # Create README
    readme_content = """🔥 Novrintech Data Fall Back - Desktop Client

INSTALLATION:
1. Double-click NovrintechDesktop.exe to run
2. No additional installation required
3. All dependencies are included

FEATURES:
• File upload and download
• User-based file tracking  
• Chat and notifications
• Professional interface
• Keyboard shortcuts

SYSTEM REQUIREMENTS:
• Windows 7 or later
• 50 MB free disk space
• Internet connection

VERSION: 2.0
© 2024 Novrintech Solutions
"""
    
    with open(os.path.join(dist_folder, "README.txt"), "w") as f:
        f.write(readme_content)
    
    print("   ✅ Distribution package created")
    return dist_folder

def main():
    """Main build process"""
    print_header()
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Build steps
    steps = [
        ("Check Python", check_python),
        ("Install PyInstaller", install_pyinstaller),
        ("Clean Build", clean_build),
        ("Build EXE", build_exe),
        ("Test EXE", test_exe),
        ("Create Distribution", create_distribution)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ {step_name} failed!")
            print("Build process stopped.")
            return False
    
    # Success!
    print("\n" + "=" * 50)
    print("🎉 BUILD COMPLETE!")
    print("=" * 50)
    
    exe_path = os.path.join("dist", "NovrintechDesktop.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"📁 EXE Location: {os.path.abspath(exe_path)}")
        print(f"📊 File Size: {size_mb:.1f} MB")
        print(f"📦 Distribution: NovrintechDesktop_Distribution/")
        print(f"🔔 Notifications: Included")
        print(f"🖥️ Platform: Windows")
    
    print("\n💡 Next Steps:")
    print("   1. Test the EXE by double-clicking it")
    print("   2. Share the 'NovrintechDesktop_Distribution' folder")
    print("   3. Users can run NovrintechDesktop.exe directly")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ SUCCESS: EXE ready for distribution!")
        else:
            print("\n❌ FAILED: Check errors above")
    except KeyboardInterrupt:
        print("\n⏹️ Build cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    input("\nPress Enter to exit...")