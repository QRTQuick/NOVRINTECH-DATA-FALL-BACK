#!/usr/bin/env python3
"""
Chat Database Integration Module
Extends the existing chat functionality to save chat data to the backend database
"""
import json
import requests
from datetime import datetime

class ChatDatabaseIntegration:
    def __init__(self, api_base_url, api_key):
        self.api_base_url = api_base_url
        self.api_key = api_key
        
    def save_chat_to_database(self, chat_messages, user_name="Unknown"):
        """Save chat messages to backend database"""
        try:
            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
            
            # Create a unique key for this user's chat history
            chat_key = f"chat_history_{user_name}_{datetime.now().strftime('%Y%m%d')}"
            
            payload = {
                "data_key": chat_key,
                "data_value": {
                    "user": user_name,
                    "timestamp": datetime.now().isoformat(),
                    "messages": chat_messages,
                    "message_count": len(chat_messages),
                    "session_info": {
                        "app_version": "2.0",
                        "platform": "desktop"
                    }
                }
            }
            
            response = requests.post(f"{self.api_base_url}/data/save", headers=headers, json=payload)
            
            if response.status_code == 200:
                return {"success": True, "chat_key": chat_key}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def save_ai_chat_to_database(self, ai_chat_history, user_name="Unknown"):
        """Save AI chat history to backend database"""
        try:
            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
            
            # Create a unique key for AI chat history
            ai_chat_key = f"ai_chat_history_{user_name}_{datetime.now().strftime('%Y%m%d')}"
            
            payload = {
                "data_key": ai_chat_key,
                "data_value": {
                    "user": user_name,
                    "timestamp": datetime.now().isoformat(),
                    "ai_conversations": ai_chat_history,
                    "conversation_count": len(ai_chat_history),
                    "session_info": {
                        "app_version": "2.0",
                        "ai_backend": "groq_llm",
                        "platform": "desktop"
                    }
                }
            }
            
            response = requests.post(f"{self.api_base_url}/data/save", headers=headers, json=payload)
            
            if response.status_code == 200:
                return {"success": True, "ai_chat_key": ai_chat_key}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def load_chat_from_database(self, user_name="Unknown", date=None):
        """Load chat messages from backend database"""
        try:
            if date is None:
                date = datetime.now().strftime('%Y%m%d')
            
            chat_key = f"chat_history_{user_name}_{date}"
            headers = {"X-API-KEY": self.api_key}
            
            response = requests.get(f"{self.api_base_url}/data/read/{chat_key}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sync_chat_data(self, local_chat_messages, ai_chat_history, user_name="Unknown"):
        """Sync both regular chat and AI chat to database"""
        results = {}
        
        # Save regular chat messages
        chat_result = self.save_chat_to_database(local_chat_messages, user_name)
        results["chat_sync"] = chat_result
        
        # Save AI chat history
        ai_result = self.save_ai_chat_to_database(ai_chat_history, user_name)
        results["ai_chat_sync"] = ai_result
        
        return results