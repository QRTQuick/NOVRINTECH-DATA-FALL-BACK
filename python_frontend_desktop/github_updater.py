#!/usr/bin/env python3
"""
GitHub-based App Updater for Novrintech Desktop Client
Uses your GitHub repository for update distribution
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
from tkinter import messagebox, ttk
import tempfile
import zipfile

class GitHubUpdater:
    def __init__(self, repo_owner="QRTQuick", repo_name="fall-back-frontend-updater", current_version="2.0"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        
        # GitHub API URLs
        self.api_base = "https://api.github.com"
        self.releases_url = f"{self.api_base}/repos/{repo_owner}/{repo_name}/releases"
        self.latest_release_url = f"{self.releases_url}/latest"
        
        # Update settings
        self.auto_check_enabled = True
        self.check_interval = 3600  # 1 hour
        self.last_check_time = None
        self.update_thread = None
        
        # Download settings
        self.download_dir = "updates"
        self.backup_dir = "backup"
        
        # Update status
        self.update_available = False
        self.latest_version = None
        self.download_url = None
        self.changelog = []
        
    def check_for_updates(self):
        """Check GitHub releases for updates"""
        try:
            print("🔍 Checking for updates...")
            
            # Get latest release from GitHub
            response = requests.get(self.latest_release_url, timeout=10)
            
            if response.status_code == 200:
                release_data = response.json()
                
                # Extract version info
                latest_version = release_data.get("tag_name", "").replace("v", "")
                release_name = release_data.get("name", "")
                release_body = release_data.get("body", "")
                published_at = release_data.get("published_at", "")
                
                # Find EXE asset
                assets = release_data.get("assets", [])
                exe_asset = None
                
                for asset in assets:
                    if asset["name"].endswith(".exe") and "NovrintechDesktop" in asset["name"]:
                        exe_asset = asset
                        break
                
                if exe_asset:
                    download_url = exe_asset["browser_download_url"]
                    file_size = exe_asset["size"]
                    
                    # Check if update is available
                    if self.is_newer_version(latest_version, self.current_version):
                        self.update_available = True
                        self.latest_version = latest_version
                        self.download_url = download_url
                        self.changelog = self.parse_changelog(release_body)
                        
                        return {
                            "success": True,
                            "update_available": True,
                            "latest_version": latest_version,
                            "current_version": self.current_version,
                            "download_url": download_url,
                            "file_size": file_size,
                            "release_name": release_name,
                            "changelog": self.changelog,
                            "published_at": published_at
                        }
                    else:
                        return {
                            "success": True,
                            "update_available": False,
                            "latest_version": latest_version,
                            "current_version": self.current_version,
                            "message": "You have the latest version"
                        }
                else:
                    return {
                        "success": False,
                        "error": "No EXE file found in latest release"
                    }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Update check failed: {str(e)}"
            }
    
    def is_newer_version(self, latest, current):
        """Compare version strings"""
        try:
            # Simple version comparison (assumes semantic versioning)
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts += [0] * (max_len - len(latest_parts))
            current_parts += [0] * (max_len - len(current_parts))
            
            return latest_parts > current_parts
        except:
            # Fallback to string comparison
            return latest != current
    
    def parse_changelog(self, release_body):
        """Parse changelog from release body"""
        if not release_body:
            return ["• Bug fixes and improvements"]
        
        lines = release_body.split('\n')
        changelog = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('*') or line.startswith('-') or line.startswith('•')):
                changelog.append(line)
            elif line and not line.startswith('#'):
                changelog.append(f"• {line}")
        
        return changelog[:10]  # Limit to 10 items
    
    def download_update(self, progress_callback=None):
        """Download update from GitHub"""
        try:
            if not self.download_url:
                return {"success": False, "error": "No download URL available"}
            
            # Create download directory
            os.makedirs(self.download_dir, exist_ok=True)
            
            # Generate filename
            filename = f"NovrintechDesktop_v{self.latest_version}.exe"
            file_path = os.path.join(self.download_dir, filename)
            
            print(f"📥 Downloading update from: {self.download_url}")
            
            # Download with progress
            response = requests.get(self.download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress callback
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            print(f"✅ Download completed: {file_path}")
            
            return {
                "success": True,
                "file_path": file_path,
                "size": downloaded,
                "filename": filename
            }
            
        except Exception as e:
            return {"success": False, "error": f"Download failed: {str(e)}"}
    
    def verify_download(self, file_path):
        """Verify downloaded file"""
        try:
            if not os.path.exists(file_path):
                return {"success": False, "error": "Downloaded file not found"}
            
            file_size = os.path.getsize(file_path)
            
            # Basic checks
            if file_size < 1000000:  # Less than 1MB
                return {"success": False, "error": "Downloaded file too small"}
            
            if not file_path.endswith('.exe'):
                return {"success": False, "error": "Downloaded file is not an EXE"}
            
            return {"success": True, "verified": True, "size": file_size}
            
        except Exception as e:
            return {"success": False, "error": f"Verification failed: {str(e)}"}
    
    def backup_current_version(self):
        """Backup current executable"""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # Get current executable path
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                current_exe = "NovrintechDesktop.exe"
            
            if os.path.exists(current_exe):
                backup_name = f"NovrintechDesktop_v{self.current_version}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.exe"
                backup_path = os.path.join(self.backup_dir, backup_name)
                
                shutil.copy2(current_exe, backup_path)
                print(f"📦 Backup created: {backup_path}")
                
                return {"success": True, "backup_path": backup_path}
            else:
                return {"success": False, "error": "Current executable not found"}
                
        except Exception as e:
            return {"success": False, "error": f"Backup failed: {str(e)}"}
    
    def install_update(self, update_file_path):
        """Install the downloaded update"""
        try:
            print("🔄 Installing update...")
            
            # Backup current version
            backup_result = self.backup_current_version()
            if not backup_result["success"]:
                print(f"⚠️ Backup failed: {backup_result['error']}")
            
            # Get current executable path
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                current_exe = "NovrintechDesktop.exe"
            
            # Create update script
            script_path = self.create_update_script(update_file_path, current_exe)
            
            print("🚀 Starting update process...")
            
            # Execute update script
            subprocess.Popen([script_path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            return {"success": True, "message": "Update initiated. Application will restart."}
            
        except Exception as e:
            return {"success": False, "error": f"Installation failed: {str(e)}"}
    
    def create_update_script(self, new_exe_path, current_exe_path):
        """Create Windows batch script for update"""
        script_content = f'''@echo off
title Novrintech Desktop Update
echo.
echo ========================================
echo   Novrintech Desktop Client Update
echo ========================================
echo.
echo Updating to version {self.latest_version}...
echo.

echo [1/4] Waiting for application to close...
timeout /t 3 /nobreak > nul

echo [2/4] Stopping any running instances...
taskkill /f /im NovrintechDesktop.exe > nul 2>&1

echo [3/4] Installing update...
copy /y "{new_exe_path}" "{current_exe_path}"

if errorlevel 1 (
    echo ERROR: Failed to copy update file!
    pause
    exit /b 1
)

echo [4/4] Cleaning up...
del "{new_exe_path}" > nul 2>&1

echo.
echo ✅ Update completed successfully!
echo Starting updated application...
echo.

start "" "{current_exe_path}"

echo Update process finished.
timeout /t 2 /nobreak > nul
del "%~f0"
'''
        
        script_path = os.path.join(self.download_dir, "update_installer.bat")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return script_path
    
    def start_auto_update_checker(self, callback=None):
        """Start background update checker"""
        if self.update_thread and self.update_thread.is_alive():
            return
        
        def update_checker():
            while self.auto_check_enabled:
                try:
                    result = self.check_for_updates()
                    self.last_check_time = datetime.now()
                    
                    if result["success"] and result["update_available"]:
                        print(f"🆕 Update available: v{result['latest_version']}")
                        if callback:
                            callback(result)
                    
                    # Wait before next check
                    import time
                    time.sleep(self.check_interval)
                    
                except Exception as e:
                    print(f"❌ Auto-update check error: {e}")
                    import time
                    time.sleep(self.check_interval)
        
        self.update_thread = threading.Thread(target=update_checker, daemon=True)
        self.update_thread.start()
        print("🔄 Auto-update checker started")
    
    def stop_auto_update_checker(self):
        """Stop auto-update checker"""
        self.auto_check_enabled = False
        if self.update_thread:
            self.update_thread.join(timeout=1)
        print("⏹️ Auto-update checker stopped")
    
    def show_update_dialog(self, update_info, parent=None):
        """Show update notification dialog"""
        try:
            # Create update dialog
            dialog = tk.Toplevel(parent) if parent else tk.Tk()
            dialog.title("Update Available")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            
            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
            y = (dialog.winfo_screenheight() // 2) - (400 // 2)
            dialog.geometry(f"500x400+{x}+{y}")
            
            # Main frame
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="🆕 Update Available", 
                                  font=('Arial', 16, 'bold'))
            title_label.pack(pady=(0, 20))
            
            # Version info
            version_frame = ttk.Frame(main_frame)
            version_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(version_frame, text=f"Current Version: {update_info['current_version']}", 
                     font=('Arial', 10)).pack(anchor=tk.W)
            ttk.Label(version_frame, text=f"Latest Version: {update_info['latest_version']}", 
                     font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            
            # Changelog
            ttk.Label(main_frame, text="What's New:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 5))
            
            changelog_frame = ttk.Frame(main_frame)
            changelog_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            changelog_text = tk.Text(changelog_frame, height=8, wrap=tk.WORD, 
                                   font=('Arial', 9), state=tk.DISABLED)
            scrollbar = ttk.Scrollbar(changelog_frame, orient=tk.VERTICAL, command=changelog_text.yview)
            changelog_text.configure(yscrollcommand=scrollbar.set)
            
            # Add changelog content
            changelog_text.config(state=tk.NORMAL)
            changelog_content = "\n".join(update_info.get('changelog', ['• Bug fixes and improvements']))
            changelog_text.insert(tk.END, changelog_content)
            changelog_text.config(state=tk.DISABLED)
            
            changelog_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            def download_and_install():
                dialog.destroy()
                self.handle_update_process(update_info, parent)
            
            def remind_later():
                dialog.destroy()
            
            def skip_version():
                # Could implement version skipping logic here
                dialog.destroy()
            
            ttk.Button(button_frame, text="Download & Install", 
                      command=download_and_install).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="Remind Later", 
                      command=remind_later).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="Skip This Version", 
                      command=skip_version).pack(side=tk.LEFT)
            
            # Make dialog modal
            dialog.transient(parent)
            dialog.grab_set()
            
            return dialog
            
        except Exception as e:
            print(f"❌ Update dialog error: {e}")
            return None
    
    def handle_update_process(self, update_info, parent=None):
        """Handle complete update process with progress"""
        try:
            # Create progress dialog
            progress_dialog = tk.Toplevel(parent) if parent else tk.Tk()
            progress_dialog.title("Downloading Update")
            progress_dialog.geometry("400x150")
            progress_dialog.resizable(False, False)
            
            # Center dialog
            progress_dialog.update_idletasks()
            x = (progress_dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (progress_dialog.winfo_screenheight() // 2) - (150 // 2)
            progress_dialog.geometry(f"400x150+{x}+{y}")
            
            # Progress frame
            progress_frame = ttk.Frame(progress_dialog, padding="20")
            progress_frame.pack(fill=tk.BOTH, expand=True)
            
            # Status label
            status_label = ttk.Label(progress_frame, text="Preparing download...", 
                                   font=('Arial', 10))
            status_label.pack(pady=(0, 10))
            
            # Progress bar
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, 
                                         maximum=100, length=350)
            progress_bar.pack(pady=(0, 10))
            
            # Progress percentage
            percent_label = ttk.Label(progress_frame, text="0%", font=('Arial', 9))
            percent_label.pack()
            
            def update_progress(percentage):
                progress_var.set(percentage)
                percent_label.config(text=f"{percentage:.1f}%")
                progress_dialog.update()
            
            def download_thread():
                try:
                    # Update status
                    status_label.config(text="Downloading update...")
                    progress_dialog.update()
                    
                    # Download update
                    download_result = self.download_update(progress_callback=update_progress)
                    
                    if download_result["success"]:
                        status_label.config(text="Verifying download...")
                        progress_dialog.update()
                        
                        # Verify download
                        verify_result = self.verify_download(download_result["file_path"])
                        
                        if verify_result["success"]:
                            progress_dialog.destroy()
                            
                            # Ask for installation confirmation
                            result = messagebox.askyesno(
                                "Install Update", 
                                f"Update downloaded successfully!\n\n"
                                f"File: {download_result['filename']}\n"
                                f"Size: {download_result['size'] / 1024 / 1024:.1f} MB\n\n"
                                f"Install now? The application will restart.",
                                parent=parent
                            )
                            
                            if result:
                                install_result = self.install_update(download_result["file_path"])
                                
                                if install_result["success"]:
                                    messagebox.showinfo("Update", 
                                                      "Update will be installed. Application will restart.", 
                                                      parent=parent)
                                    # Exit application
                                    if parent:
                                        parent.quit()
                                    else:
                                        sys.exit(0)
                                else:
                                    messagebox.showerror("Update Error", 
                                                       f"Installation failed:\n{install_result['error']}", 
                                                       parent=parent)
                        else:
                            progress_dialog.destroy()
                            messagebox.showerror("Update Error", 
                                               f"Download verification failed:\n{verify_result['error']}", 
                                               parent=parent)
                    else:
                        progress_dialog.destroy()
                        messagebox.showerror("Update Error", 
                                           f"Download failed:\n{download_result['error']}", 
                                           parent=parent)
                        
                except Exception as e:
                    progress_dialog.destroy()
                    messagebox.showerror("Update Error", f"Update process failed:\n{str(e)}", parent=parent)
            
            # Start download in background thread
            threading.Thread(target=download_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Update Error", f"Failed to start update process:\n{str(e)}", parent=parent)
    
    def get_update_status(self):
        """Get current update status"""
        return {
            "auto_check_enabled": self.auto_check_enabled,
            "last_check_time": self.last_check_time,
            "update_available": self.update_available,
            "latest_version": self.latest_version,
            "current_version": self.current_version,
            "repo_url": f"https://github.com/{self.repo_owner}/{self.repo_name}"
        }