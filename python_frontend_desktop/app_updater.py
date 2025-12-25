#!/usr/bin/env python3
"""
App Updater Module for Novrintech Desktop Client
Provides multiple strategies for keeping the app updated
"""
import requests
import json
import os
import sys
import subprocess
import shutil
from datetime import datetime
import hashlib
import threading
import tkinter as tk
from tkinter import messagebox

class AppUpdater:
    def __init__(self, current_version="2.0", update_server_url=None):
        self.current_version = current_version
        self.update_server_url = update_server_url or "https://novrintech-updates.onrender.com"
        self.update_check_url = f"{self.update_server_url}/api/check-update"
        self.download_url = f"{self.update_server_url}/api/download"
        
        # Local update settings
        self.update_dir = "updates"
        self.backup_dir = "backup"
        
        # Update strategies
        self.strategies = {
            "auto_download": True,      # Automatically download updates
            "auto_install": False,      # Require user confirmation for install
            "backup_current": True,     # Backup current version before update
            "check_frequency": 3600,    # Check every hour (in seconds)
            "silent_mode": False        # Show update notifications
        }
    
    def check_for_updates(self):
        """Check if updates are available"""
        try:
            payload = {
                "current_version": self.current_version,
                "platform": "windows",
                "app_name": "NovrintechDesktop"
            }
            
            response = requests.post(self.update_check_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "update_available": data.get("update_available", False),
                    "latest_version": data.get("latest_version"),
                    "download_url": data.get("download_url"),
                    "changelog": data.get("changelog", []),
                    "file_size": data.get("file_size", 0),
                    "release_date": data.get("release_date"),
                    "critical": data.get("critical", False)
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def download_update(self, download_url, filename="NovrintechDesktop_new.exe"):
        """Download update file"""
        try:
            # Create update directory
            os.makedirs(self.update_dir, exist_ok=True)
            file_path = os.path.join(self.update_dir, filename)
            
            # Download with progress
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Calculate progress
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"Download progress: {progress:.1f}%")
            
            return {"success": True, "file_path": file_path, "size": downloaded}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def verify_update_file(self, file_path, expected_hash=None):
        """Verify downloaded update file"""
        try:
            if not os.path.exists(file_path):
                return {"success": False, "error": "Update file not found"}
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size < 1000000:  # Less than 1MB is suspicious
                return {"success": False, "error": "Update file too small"}
            
            # Verify hash if provided
            if expected_hash:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                if file_hash != expected_hash:
                    return {"success": False, "error": "Hash verification failed"}
            
            return {"success": True, "verified": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def backup_current_version(self):
        """Backup current executable"""
        try:
            # Create backup directory
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # Get current executable path
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                current_exe = "NovrintechDesktop.exe"  # Fallback
            
            if os.path.exists(current_exe):
                backup_name = f"NovrintechDesktop_v{self.current_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.exe"
                backup_path = os.path.join(self.backup_dir, backup_name)
                
                shutil.copy2(current_exe, backup_path)
                return {"success": True, "backup_path": backup_path}
            else:
                return {"success": False, "error": "Current executable not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def install_update(self, update_file_path):
        """Install the downloaded update"""
        try:
            # Backup current version
            if self.strategies["backup_current"]:
                backup_result = self.backup_current_version()
                if not backup_result["success"]:
                    return {"success": False, "error": f"Backup failed: {backup_result['error']}"}
            
            # Get current executable path
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                current_exe = "NovrintechDesktop.exe"
            
            # Create update script
            update_script = self.create_update_script(update_file_path, current_exe)
            
            # Execute update script and exit current app
            subprocess.Popen([update_script], shell=True)
            
            return {"success": True, "message": "Update initiated. Application will restart."}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_update_script(self, new_exe_path, current_exe_path):
        """Create batch script for update process"""
        script_content = f"""@echo off
echo Updating Novrintech Desktop Client...
timeout /t 3 /nobreak > nul

echo Stopping current application...
taskkill /f /im NovrintechDesktop.exe > nul 2>&1

echo Installing update...
copy /y "{new_exe_path}" "{current_exe_path}"

echo Cleaning up...
del "{new_exe_path}"

echo Starting updated application...
start "" "{current_exe_path}"

echo Update complete!
del "%~f0"
"""
        
        script_path = os.path.join(self.update_dir, "update.bat")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return script_path
    
    def start_auto_update_checker(self, callback=None):
        """Start background thread for automatic update checking"""
        def update_checker():
            while True:
                try:
                    result = self.check_for_updates()
                    
                    if result["success"] and result["update_available"]:
                        if callback:
                            callback(result)
                        elif not self.strategies["silent_mode"]:
                            self.show_update_notification(result)
                    
                    # Wait before next check
                    import time
                    time.sleep(self.strategies["check_frequency"])
                    
                except Exception as e:
                    print(f"Auto-update check error: {e}")
                    import time
                    time.sleep(self.strategies["check_frequency"])
        
        thread = threading.Thread(target=update_checker, daemon=True)
        thread.start()
        return thread
    
    def show_update_notification(self, update_info):
        """Show update notification to user"""
        try:
            # Create notification window
            root = tk.Tk()
            root.withdraw()  # Hide main window
            
            message = f"""New version available: {update_info['latest_version']}
Current version: {self.current_version}

Changes:
{chr(10).join(update_info.get('changelog', ['• Bug fixes and improvements']))}

Would you like to download and install the update?"""
            
            result = messagebox.askyesno("Update Available", message)
            
            if result:
                # Start update process
                self.handle_update_process(update_info)
            
            root.destroy()
            
        except Exception as e:
            print(f"Update notification error: {e}")
    
    def handle_update_process(self, update_info):
        """Handle the complete update process"""
        try:
            # Download update
            print("Downloading update...")
            download_result = self.download_update(update_info["download_url"])
            
            if not download_result["success"]:
                messagebox.showerror("Update Error", f"Download failed: {download_result['error']}")
                return
            
            # Verify update
            print("Verifying update...")
            verify_result = self.verify_update_file(download_result["file_path"])
            
            if not verify_result["success"]:
                messagebox.showerror("Update Error", f"Verification failed: {verify_result['error']}")
                return
            
            # Install update
            if self.strategies["auto_install"] or messagebox.askyesno("Install Update", "Update downloaded successfully. Install now?"):
                print("Installing update...")
                install_result = self.install_update(download_result["file_path"])
                
                if install_result["success"]:
                    messagebox.showinfo("Update", "Update will be installed. Application will restart.")
                    # Exit current application
                    sys.exit(0)
                else:
                    messagebox.showerror("Update Error", f"Installation failed: {install_result['error']}")
            
        except Exception as e:
            messagebox.showerror("Update Error", f"Update process failed: {str(e)}")

# Update Server Configuration (for your backend)
UPDATE_SERVER_CONFIG = {
    "version_info": {
        "current_version": "2.0",
        "latest_version": "2.1",
        "update_available": True,
        "critical": False,
        "release_date": "2024-12-23",
        "download_url": "https://novrintech-updates.onrender.com/files/NovrintechDesktop_v2.1.exe",
        "file_size": 16500000,
        "sha256_hash": "abc123...",
        "changelog": [
            "• Added AI chat integration",
            "• Improved database synchronization", 
            "• Enhanced notification system",
            "• Bug fixes and performance improvements"
        ]
    },
    "update_policies": {
        "force_update_below": "1.0",  # Force update for versions below this
        "notify_update_above": "2.0", # Notify for versions above this
        "check_frequency": 3600,      # Check every hour
        "download_timeout": 300       # 5 minute download timeout
    }
}