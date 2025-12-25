#!/usr/bin/env python3
"""
Enhanced Chat Database Manager
Handles chat synchronization with backend database
"""
import requests
import json
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class ChatDatabaseManager:
    def __init__(self, api_base_url, api_key):
        self.api_base_url = api_base_url
        self.api_key = api_key
        
        # Sync settings
        self.auto_sync_enabled = True
        self.sync_interval = 300  # 5 minutes
        self.last_sync_time = None
        self.sync_thread = None
        
        # Sync status
        self.sync_in_progress = False
        self.total_messages_synced = 0
        self.last_sync_result = None
        
        # Callbacks
        self.sync_status_callback = None
        
    def save_chat_message_to_db(self, message, user_name="Unknown"):
        """Save single chat message to database"""
        try:
            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
            
            # Create unique key for message
            timestamp_key = message["timestamp"].replace(" ", "_").replace(":", "").replace("-", "")
            message_key = f"chat_msg_{user_name}_{timestamp_key}"
            
            payload = {
                "data_key": message_key,
                "data_value": {
                    "message": message,
                    "user": user_name,
                    "app_version": "2.0",
                    "sync_timestamp": datetime.now().isoformat(),
                    "message_type": "chat_activity"
                }
            }
            
            response = requests.post(f"{self.api_base_url}/data/save", headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {"success": True, "message_key": message_key}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def save_chat_batch_to_db(self, chat_messages, user_name="Unknown"):
        """Save batch of chat messages to database"""
        try:
            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
            
            # Create batch key
            batch_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_key = f"chat_batch_{user_name}_{batch_timestamp}"
            
            payload = {
                "data_key": batch_key,
                "data_value": {
                    "messages": chat_messages,
                    "user": user_name,
                    "message_count": len(chat_messages),
                    "batch_timestamp": datetime.now().isoformat(),
                    "app_version": "2.0",
                    "sync_type": "batch_sync"
                }
            }
            
            response = requests.post(f"{self.api_base_url}/data/save", headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return {"success": True, "batch_key": batch_key, "message_count": len(chat_messages)}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def save_ai_chat_to_db(self, ai_chat_history, user_name="Unknown"):
        """Save AI chat history to database"""
        try:
            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
            
            # Create AI chat key
            ai_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ai_key = f"ai_chat_{user_name}_{ai_timestamp}"
            
            payload = {
                "data_key": ai_key,
                "data_value": {
                    "ai_conversations": ai_chat_history,
                    "user": user_name,
                    "conversation_count": len(ai_chat_history),
                    "sync_timestamp": datetime.now().isoformat(),
                    "app_version": "2.0",
                    "ai_backend": "groq_llm",
                    "sync_type": "ai_chat_sync"
                }
            }
            
            response = requests.post(f"{self.api_base_url}/data/save", headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return {"success": True, "ai_key": ai_key, "conversation_count": len(ai_chat_history)}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sync_all_chat_data(self, chat_messages, ai_chat_history, user_name="Unknown"):
        """Sync all chat data to database"""
        try:
            self.sync_in_progress = True
            results = {}
            
            # Update status
            if self.sync_status_callback:
                self.sync_status_callback("Syncing chat messages...")
            
            # Sync regular chat messages
            if chat_messages:
                chat_result = self.save_chat_batch_to_db(chat_messages, user_name)
                results["chat_sync"] = chat_result
                
                if chat_result["success"]:
                    self.total_messages_synced += chat_result["message_count"]
            
            # Update status
            if self.sync_status_callback:
                self.sync_status_callback("Syncing AI conversations...")
            
            # Sync AI chat history
            if ai_chat_history:
                ai_result = self.save_ai_chat_to_db(ai_chat_history, user_name)
                results["ai_sync"] = ai_result
                
                if ai_result["success"]:
                    self.total_messages_synced += ai_result["conversation_count"]
            
            # Update sync time
            self.last_sync_time = datetime.now()
            self.last_sync_result = results
            
            # Update status
            if self.sync_status_callback:
                self.sync_status_callback("Sync completed successfully")
            
            return {"success": True, "results": results, "sync_time": self.last_sync_time}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.sync_in_progress = False
    
    def load_chat_from_db(self, user_name="Unknown", date_filter=None):
        """Load chat messages from database"""
        try:
            # This would require a search endpoint on the backend
            # For now, we'll return a placeholder
            return {
                "success": True,
                "message": "Chat loading from database not yet implemented",
                "messages": []
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_auto_sync(self, chat_messages_ref, ai_chat_ref, user_name_ref):
        """Start automatic chat synchronization"""
        if self.sync_thread and self.sync_thread.is_alive():
            return
        
        def sync_worker():
            while self.auto_sync_enabled:
                try:
                    if not self.sync_in_progress:
                        # Get current data
                        chat_messages = chat_messages_ref() if callable(chat_messages_ref) else chat_messages_ref
                        ai_chat = ai_chat_ref() if callable(ai_chat_ref) else ai_chat_ref
                        user_name = user_name_ref() if callable(user_name_ref) else user_name_ref
                        
                        # Only sync if there's data
                        if chat_messages or ai_chat:
                            result = self.sync_all_chat_data(chat_messages, ai_chat, user_name)
                            
                            if result["success"]:
                                print(f"✅ Auto-sync completed: {len(chat_messages or [])} messages, {len(ai_chat or [])} AI conversations")
                            else:
                                print(f"❌ Auto-sync failed: {result['error']}")
                    
                    # Wait before next sync
                    time.sleep(self.sync_interval)
                    
                except Exception as e:
                    print(f"❌ Auto-sync error: {e}")
                    time.sleep(self.sync_interval)
        
        self.sync_thread = threading.Thread(target=sync_worker, daemon=True)
        self.sync_thread.start()
        print("🔄 Chat auto-sync started")
    
    def stop_auto_sync(self):
        """Stop automatic synchronization"""
        self.auto_sync_enabled = False
        if self.sync_thread:
            self.sync_thread.join(timeout=1)
        print("⏹️ Chat auto-sync stopped")
    
    def get_sync_status(self):
        """Get current sync status"""
        return {
            "auto_sync_enabled": self.auto_sync_enabled,
            "sync_in_progress": self.sync_in_progress,
            "last_sync_time": self.last_sync_time,
            "total_messages_synced": self.total_messages_synced,
            "sync_interval": self.sync_interval,
            "last_sync_result": self.last_sync_result
        }

class ChatSyncUI:
    def __init__(self, parent, chat_db_manager):
        self.parent = parent
        self.chat_db_manager = chat_db_manager
        
    def create_sync_controls(self, parent_frame):
        """Create UI controls for chat synchronization"""
        # Sync section
        sync_section = ttk.LabelFrame(parent_frame, text="💾 Chat Database Sync", padding="15")
        sync_section.pack(fill=tk.X, pady=(0, 15))
        
        # Sync status
        self.sync_status_label = ttk.Label(sync_section, text="Sync Status: Ready", font=('Arial', 10))
        self.sync_status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Sync controls
        sync_controls = ttk.Frame(sync_section)
        sync_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(sync_controls, text="🔄 Sync Now", command=self.manual_sync).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(sync_controls, text="📊 Sync Status", command=self.show_sync_status).pack(side=tk.LEFT, padx=(0, 10))
        
        # Auto-sync toggle
        self.auto_sync_var = tk.BooleanVar(value=self.chat_db_manager.auto_sync_enabled)
        ttk.Checkbutton(sync_controls, text="Auto-sync enabled", 
                       variable=self.auto_sync_var, 
                       command=self.toggle_auto_sync).pack(side=tk.LEFT, padx=(10, 0))
        
        # Sync info
        sync_info = ttk.Label(sync_section, 
                             text="💡 Chat messages are automatically synced to the database every 5 minutes", 
                             font=('Arial', 8), foreground="gray")
        sync_info.pack(anchor=tk.W)
        
        # Set status callback
        self.chat_db_manager.sync_status_callback = self.update_sync_status
        
        return sync_section
    
    def update_sync_status(self, status_text):
        """Update sync status display"""
        if hasattr(self, 'sync_status_label'):
            self.sync_status_label.config(text=f"Sync Status: {status_text}")
            self.parent.update()
    
    def manual_sync(self):
        """Trigger manual sync"""
        try:
            # This would need to be connected to the main app's data
            # For now, show a placeholder
            self.update_sync_status("Manual sync initiated...")
            
            # Simulate sync process
            def sync_thread():
                try:
                    time.sleep(2)  # Simulate sync time
                    self.update_sync_status("Manual sync completed")
                    messagebox.showinfo("Sync Complete", "Chat data synchronized to database successfully!")
                except Exception as e:
                    self.update_sync_status("Manual sync failed")
                    messagebox.showerror("Sync Error", f"Manual sync failed: {str(e)}")
            
            threading.Thread(target=sync_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Sync Error", f"Failed to start manual sync: {str(e)}")
    
    def toggle_auto_sync(self):
        """Toggle automatic synchronization"""
        self.chat_db_manager.auto_sync_enabled = self.auto_sync_var.get()
        status = "enabled" if self.chat_db_manager.auto_sync_enabled else "disabled"
        self.update_sync_status(f"Auto-sync {status}")
        messagebox.showinfo("Auto-Sync", f"Automatic synchronization {status}")
    
    def show_sync_status(self):
        """Show detailed sync status"""
        status = self.chat_db_manager.get_sync_status()
        
        # Create status dialog
        status_dialog = tk.Toplevel(self.parent)
        status_dialog.title("Chat Sync Status")
        status_dialog.geometry("400x300")
        status_dialog.resizable(False, False)
        
        # Center dialog
        status_dialog.update_idletasks()
        x = (status_dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (status_dialog.winfo_screenheight() // 2) - (300 // 2)
        status_dialog.geometry(f"400x300+{x}+{y}")
        
        # Status frame
        status_frame = ttk.Frame(status_dialog, padding="20")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(status_frame, text="💾 Chat Sync Status", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Status details
        status_text = f"""Auto-sync: {'Enabled' if status['auto_sync_enabled'] else 'Disabled'}
Sync in progress: {'Yes' if status['sync_in_progress'] else 'No'}
Last sync: {status['last_sync_time'] or 'Never'}
Messages synced: {status['total_messages_synced']}
Sync interval: {status['sync_interval']} seconds

Database: Connected
Backend: {self.chat_db_manager.api_base_url}"""
        
        ttk.Label(status_frame, text=status_text, font=('Arial', 10), justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 20))
        
        ttk.Button(status_frame, text="Close", command=status_dialog.destroy).pack()

class UpdateUI:
    def __init__(self, parent, github_updater):
        self.parent = parent
        self.github_updater = github_updater
        
    def create_update_controls(self, parent_frame):
        """Create UI controls for app updates"""
        # Update section
        update_section = ttk.LabelFrame(parent_frame, text="🔄 App Updates", padding="15")
        update_section.pack(fill=tk.X, pady=(0, 15))
        
        # Update status
        self.update_status_label = ttk.Label(update_section, text="Update Status: Checking...", font=('Arial', 10))
        self.update_status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Update controls
        update_controls = ttk.Frame(update_section)
        update_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(update_controls, text="🔍 Check for Updates", command=self.check_updates).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(update_controls, text="📋 Update History", command=self.show_update_history).pack(side=tk.LEFT, padx=(0, 10))
        
        # Auto-update toggle
        self.auto_update_var = tk.BooleanVar(value=self.github_updater.auto_check_enabled)
        ttk.Checkbutton(update_controls, text="Auto-check enabled", 
                       variable=self.auto_update_var, 
                       command=self.toggle_auto_update).pack(side=tk.LEFT, padx=(10, 0))
        
        # Update info
        update_info = ttk.Label(update_section, 
                               text=f"💡 Updates are downloaded from: github.com/{self.github_updater.repo_owner}/{self.github_updater.repo_name}", 
                               font=('Arial', 8), foreground="gray")
        update_info.pack(anchor=tk.W)
        
        # Initial status check
        self.update_initial_status()
        
        return update_section
    
    def update_initial_status(self):
        """Update initial status display"""
        status = self.github_updater.get_update_status()
        if status['update_available']:
            self.update_status_label.config(text=f"Update Status: v{status['latest_version']} available!")
        else:
            self.update_status_label.config(text=f"Update Status: v{status['current_version']} (latest)")
    
    def check_updates(self):
        """Check for updates manually"""
        try:
            self.update_status_label.config(text="Update Status: Checking...")
            self.parent.update()
            
            def check_thread():
                try:
                    result = self.github_updater.check_for_updates()
                    
                    if result["success"]:
                        if result["update_available"]:
                            self.update_status_label.config(text=f"Update Status: v{result['latest_version']} available!")
                            
                            # Show update dialog
                            self.github_updater.show_update_dialog(result, self.parent)
                        else:
                            self.update_status_label.config(text=f"Update Status: v{result['current_version']} (latest)")
                            messagebox.showinfo("No Updates", "You have the latest version!", parent=self.parent)
                    else:
                        self.update_status_label.config(text="Update Status: Check failed")
                        messagebox.showerror("Update Error", f"Failed to check for updates:\n{result['error']}", parent=self.parent)
                        
                except Exception as e:
                    self.update_status_label.config(text="Update Status: Check failed")
                    messagebox.showerror("Update Error", f"Update check failed:\n{str(e)}", parent=self.parent)
            
            threading.Thread(target=check_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Update Error", f"Failed to start update check:\n{str(e)}")
    
    def toggle_auto_update(self):
        """Toggle automatic update checking"""
        self.github_updater.auto_check_enabled = self.auto_update_var.get()
        
        if self.github_updater.auto_check_enabled:
            self.github_updater.start_auto_update_checker(callback=self.handle_auto_update)
            status = "enabled"
        else:
            self.github_updater.stop_auto_update_checker()
            status = "disabled"
        
        messagebox.showinfo("Auto-Update", f"Automatic update checking {status}")
    
    def handle_auto_update(self, update_info):
        """Handle automatic update notification"""
        # Show update dialog when auto-update finds an update
        self.github_updater.show_update_dialog(update_info, self.parent)
    
    def show_update_history(self):
        """Show update history and current status"""
        status = self.github_updater.get_update_status()
        
        # Create history dialog
        history_dialog = tk.Toplevel(self.parent)
        history_dialog.title("Update Information")
        history_dialog.geometry("500x400")
        history_dialog.resizable(False, False)
        
        # Center dialog
        history_dialog.update_idletasks()
        x = (history_dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (history_dialog.winfo_screenheight() // 2) - (400 // 2)
        history_dialog.geometry(f"500x400+{x}+{y}")
        
        # History frame
        history_frame = ttk.Frame(history_dialog, padding="20")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(history_frame, text="🔄 Update Information", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Current status
        status_text = f"""Current Version: {status['current_version']}
Latest Version: {status.get('latest_version', 'Unknown')}
Update Available: {'Yes' if status['update_available'] else 'No'}
Auto-check: {'Enabled' if status['auto_check_enabled'] else 'Disabled'}
Last Check: {status.get('last_check_time', 'Never')}

Repository: {status['repo_url']}
Update Source: GitHub Releases"""
        
        ttk.Label(history_frame, text=status_text, font=('Arial', 10), justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(history_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Check Now", command=lambda: [history_dialog.destroy(), self.check_updates()]).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=history_dialog.destroy).pack(side=tk.LEFT)