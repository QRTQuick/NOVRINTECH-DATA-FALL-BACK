"""
AI Service Module for Novrintech Desktop Client
Handles communication with the AI backend and provides context-aware assistance
"""
import requests
import json
import threading
import time
from datetime import datetime
from config import AI_API_URL, AI_ENDPOINTS, APP_CONTEXT

class AIService:
    def __init__(self):
        self.ai_api_url = AI_API_URL
        self.chat_endpoint = f"{self.ai_api_url}{AI_ENDPOINTS['chat']}"
        self.health_endpoint = f"{self.ai_api_url}{AI_ENDPOINTS['health']}"
        self.keepalive_endpoint = f"{self.ai_api_url}{AI_ENDPOINTS['keepalive']}"
        
        # AI chat history
        self.ai_chat_history = []
        self.max_history_length = 50
        
        # Connection status
        self.is_connected = False
        self.last_health_check = None
        
        # Keep-alive for AI backend
        self.ai_keepalive_running = False
        self.ai_keepalive_thread = None
        
        # Application context for AI understanding
        self.app_context = APP_CONTEXT
        
        # Start AI backend monitoring
        self.start_ai_keepalive()
    
    def get_application_context(self):
        """Get comprehensive application context for AI understanding"""
        return {
            "application_info": self.app_context,
            "current_session": {
                "timestamp": datetime.now().isoformat(),
                "ai_chat_history_length": len(self.ai_chat_history),
                "connection_status": self.is_connected,
                "last_health_check": self.last_health_check
            },
            "capabilities": [
                "Answer questions about application features and functionality",
                "Provide technical support and troubleshooting guidance",
                "Explain file upload and management processes",
                "Help with data operations and JSON storage",
                "Assist with UI navigation and keyboard shortcuts",
                "Provide information about API endpoints and usage",
                "Explain error messages and suggest solutions",
                "Guide users through complex workflows"
            ]
        }
    
    def send_message_to_ai(self, user_message, include_context=True):
        """Send message to AI backend with full application context"""
        try:
            # Prepare the message with context
            if include_context:
                context_info = self.get_application_context()
                
                enhanced_message = f"""
APPLICATION CONTEXT:
{json.dumps(context_info, indent=2)}

USER QUESTION: {user_message}

Please provide a helpful response based on the application context above. 
If the question is about this specific application, use the context information to give accurate, detailed answers.
If it's a general question, provide helpful information while being aware of the application context.
"""
            else:
                enhanced_message = user_message
            
            # Send request to AI backend
            payload = {"message": enhanced_message}
            response = requests.post(
                self.chat_endpoint,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    ai_response = data.get("reply", "No response received")
                    
                    # Add to chat history
                    self.add_to_ai_history("user", user_message)
                    self.add_to_ai_history("assistant", ai_response)
                    
                    return {
                        "success": True,
                        "response": ai_response,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_msg = data.get("error", "Unknown error occurred")
                    return {
                        "success": False,
                        "error": f"AI API Error: {error_msg}",
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out. The AI service may be slow to respond.",
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to AI backend. Please check your internet connection.",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def add_to_ai_history(self, role, message):
        """Add message to AI chat history"""
        self.ai_chat_history.append({
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep history within limits
        if len(self.ai_chat_history) > self.max_history_length:
            self.ai_chat_history = self.ai_chat_history[-self.max_history_length:]
    
    def get_ai_chat_history(self):
        """Get AI chat history"""
        return self.ai_chat_history.copy()
    
    def clear_ai_chat_history(self):
        """Clear AI chat history"""
        self.ai_chat_history = []
    
    def check_ai_health(self):
        """Check AI backend health"""
        try:
            response = requests.get(self.health_endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.is_connected = True
                self.last_health_check = datetime.now().isoformat()
                return {
                    "success": True,
                    "status": data.get("status", "Unknown"),
                    "message": data.get("message", "No message"),
                    "timestamp": data.get("timestamp", "No timestamp"),
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                self.is_connected = False
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            self.is_connected = False
            return {
                "success": False,
                "error": f"Health check failed: {str(e)}"
            }
    
    def start_ai_keepalive(self):
        """Start keep-alive for AI backend"""
        if not self.ai_keepalive_running:
            self.ai_keepalive_running = True
            self.ai_keepalive_thread = threading.Thread(target=self.ai_keepalive_worker, daemon=True)
            self.ai_keepalive_thread.start()
            print("🤖 AI Keep-alive started - pinging AI backend every 30 seconds")
    
    def stop_ai_keepalive(self):
        """Stop AI keep-alive"""
        self.ai_keepalive_running = False
        if self.ai_keepalive_thread:
            self.ai_keepalive_thread.join(timeout=1)
        print("🤖 AI Keep-alive stopped")
    
    def ai_keepalive_worker(self):
        """Background worker for AI backend keep-alive"""
        while self.ai_keepalive_running:
            try:
                # Ping AI backend health endpoint
                response = requests.get(self.health_endpoint, timeout=5)
                if response.status_code == 200:
                    self.is_connected = True
                    print(f"🤖 AI Keep-alive ping successful: {datetime.now().strftime('%H:%M:%S')}")
                else:
                    self.is_connected = False
                    print(f"🤖 AI Keep-alive ping returned: {response.status_code}")
            except Exception as e:
                self.is_connected = False
                print(f"🤖 AI Keep-alive ping failed: {e}")
            
            # Wait 30 seconds before next ping (less frequent than main backend)
            time.sleep(30)
    
    def get_suggested_questions(self):
        """Get suggested questions for users"""
        return [
            "What features does this application have?",
            "How do I upload files to the server?",
            "What is the keep-alive system and why is it needed?",
            "How can I manage my uploaded files?",
            "What are the keyboard shortcuts available?",
            "How does the duplicate detection work?",
            "What data operations can I perform?",
            "How do I troubleshoot connection issues?",
            "What file types are supported for upload?",
            "How can I export my file list?",
            "What is the notification system?",
            "How does the chat and activity logging work?",
            "What are the API endpoints used by this application?",
            "How can I zoom the interface?",
            "What happens when the server restarts?"
        ]
    
    def get_quick_help(self, topic):
        """Get quick help for specific topics"""
        help_topics = {
            "upload": "To upload files: 1) Enter your name in the File Upload tab, 2) Click 'Browse Files' to select a file, 3) Click 'Upload File'. The app will check for duplicates automatically.",
            
            "download": "To download files: 1) Go to File Manager tab, 2) Select a file from the list, 3) Click 'Download Selected' or press Ctrl+D, 4) Choose where to save the file.",
            
            "delete": "To delete files: 1) Select files in File Manager, 2) Click 'Delete Selected' or press Delete key, 3) Confirm the deletion. You can also bulk delete multiple files.",
            
            "shortcuts": "Key shortcuts: Ctrl+O (Upload), F5 (Refresh), Ctrl+D (Download), Delete (Delete file), Ctrl+A (Select all), Ctrl++ (Zoom in), Ctrl+- (Zoom out)",
            
            "connection": "If connection fails: 1) Check internet connection, 2) Use 'Test Connection' in Configuration tab, 3) Check the status indicator in title bar, 4) Try refreshing the file list.",
            
            "data": "Data operations: Use the Data Operations tab to store and retrieve JSON data with custom keys. Perfect for saving configuration or application settings.",
            
            "notifications": "Notifications show for uploads, downloads, and deletions. You can enable/disable them in the Chat & Notifications tab. EXE-compatible fallback is available.",
            
            "keepalive": "Keep-alive prevents the server from sleeping by pinging it every few seconds. This ensures your files remain accessible on cloud platforms like Render."
        }
        
        return help_topics.get(topic.lower(), f"No quick help available for '{topic}'. Try asking the AI assistant for detailed information.")
    
    def save_ai_chat_history(self, filename="ai_chat_history.json"):
        """Save AI chat history to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.ai_chat_history, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving AI chat history: {e}")
            return False
    
    def load_ai_chat_history(self, filename="ai_chat_history.json"):
        """Load AI chat history from file"""
        try:
            import os
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.ai_chat_history = json.load(f)
                return True
        except Exception as e:
            print(f"Error loading AI chat history: {e}")
        return False