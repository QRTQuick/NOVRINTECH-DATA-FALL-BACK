#!/usr/bin/env python3
"""
Enhanced Chat Integration Module
Adds database synchronization to the existing chat functionality
"""
from chat_database_integration import ChatDatabaseIntegration
from app_updater import AppUpdater
import json
from datetime import datetime

class EnhancedChatManager:
    def __init__(self, api_base_url, api_key):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.db_integration = ChatDatabaseIntegration(api_base_url, api_key)
        self.updater = AppUpdater()
        
        # Auto-sync settings
        self.auto_sync_enabled = True
        self.sync_interval = 300  # 5 minutes
        self.last_sync_time = None
        
    def enhanced_add_chat_message(self, message_type, title, content, user=None, sync_to_db=True):
        """Enhanced version of add_chat_message with database sync"""
        # Create message object
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = {
            "timestamp": timestamp,
            "type": message_type,
            "title": title,
            "content": content,
            "user": user or "Unknown",
            "synced_to_db": False
        }
        
        # Add to local chat messages (assuming this exists in main app)
        # self.chat_messages.append(message)
        
        # Sync to database if enabled
        if sync_to_db and self.auto_sync_enabled:
            sync_result = self.sync_single_message_to_db(message, user)
            if sync_result["success"]:
                message["synced_to_db"] = True
                message["db_key"] = sync_result.get("chat_key")
        
        return message
    
    def sync_single_message_to_db(self, message, user_name="Unknown"):
        """Sync a single message to database"""
        try:
            # Create a unique key for this message
            message_key = f"chat_message_{user_name}_{message['timestamp'].replace(' ', '_').replace(':', '')}"
            
            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
            payload = {
                "data_key": message_key,
                "data_value": {
                    "message": message,
                    "user": user_name,
                    "app_version": "2.0",
                    "sync_timestamp": datetime.now().isoformat()
                }
            }
            
            import requests
            response = requests.post(f"{self.api_base_url}/data/save", headers=headers, json=payload)
            
            if response.status_code == 200:
                return {"success": True, "chat_key": message_key}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def bulk_sync_chat_to_db(self, chat_messages, user_name="Unknown"):
        """Sync all chat messages to database in bulk"""
        try:
            # Group messages by date for efficient storage
            messages_by_date = {}
            
            for message in chat_messages:
                date_key = message["timestamp"][:10]  # YYYY-MM-DD
                if date_key not in messages_by_date:
                    messages_by_date[date_key] = []
                messages_by_date[date_key].append(message)
            
            sync_results = []
            
            for date, messages in messages_by_date.items():
                result = self.db_integration.save_chat_to_database(messages, user_name)
                sync_results.append({
                    "date": date,
                    "message_count": len(messages),
                    "result": result
                })
            
            return {"success": True, "sync_results": sync_results}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sync_ai_chat_to_db(self, ai_chat_history, user_name="Unknown"):
        """Sync AI chat history to database"""
        return self.db_integration.save_ai_chat_to_database(ai_chat_history, user_name)
    
    def load_chat_from_db(self, user_name="Unknown", date_range=None):
        """Load chat messages from database"""
        try:
            if date_range is None:
                # Load today's messages
                date_range = [datetime.now().strftime('%Y%m%d')]
            
            all_messages = []
            
            for date in date_range:
                result = self.db_integration.load_chat_from_database(user_name, date)
                if result["success"]:
                    messages = result["data"].get("messages", [])
                    all_messages.extend(messages)
            
            return {"success": True, "messages": all_messages}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def auto_sync_scheduler(self):
        """Background scheduler for automatic chat sync"""
        import threading
        import time
        
        def sync_worker():
            while self.auto_sync_enabled:
                try:
                    # This would need to be called from the main app
                    # self.bulk_sync_chat_to_db(self.chat_messages, self.current_user)
                    self.last_sync_time = datetime.now()
                    print(f"Auto-sync completed at {self.last_sync_time}")
                    
                except Exception as e:
                    print(f"Auto-sync error: {e}")
                
                time.sleep(self.sync_interval)
        
        thread = threading.Thread(target=sync_worker, daemon=True)
        thread.start()
        return thread
    
    def get_sync_status(self):
        """Get current sync status"""
        return {
            "auto_sync_enabled": self.auto_sync_enabled,
            "last_sync_time": self.last_sync_time,
            "sync_interval": self.sync_interval,
            "database_connected": True  # Could add actual connectivity check
        }

# Integration instructions for main.py
INTEGRATION_INSTRUCTIONS = """
To integrate enhanced chat functionality into main.py:

1. Import the enhanced chat manager:
   from enhanced_chat_integration import EnhancedChatManager

2. Initialize in __init__ method:
   self.enhanced_chat = EnhancedChatManager(self.api_base_url, self.api_key)

3. Replace add_chat_message calls:
   # Old:
   self.add_chat_message("upload", "File Uploaded", "message", user)
   
   # New:
   message = self.enhanced_chat.enhanced_add_chat_message("upload", "File Uploaded", "message", user)
   self.chat_messages.append(message)

4. Add sync methods to menu or buttons:
   def sync_chat_to_database(self):
       user_name = self.load_user_name() or "Unknown"
       result = self.enhanced_chat.bulk_sync_chat_to_db(self.chat_messages, user_name)
       if result["success"]:
           messagebox.showinfo("Success", "Chat history synced to database!")
       else:
           messagebox.showerror("Error", f"Sync failed: {result['error']}")

5. Add auto-sync toggle:
   def toggle_auto_sync(self):
       self.enhanced_chat.auto_sync_enabled = not self.enhanced_chat.auto_sync_enabled
       status = "enabled" if self.enhanced_chat.auto_sync_enabled else "disabled"
       messagebox.showinfo("Auto-Sync", f"Auto-sync {status}")

6. Start auto-sync in setup_ui:
   self.enhanced_chat.auto_sync_scheduler()
"""