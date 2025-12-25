import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import json
import os
import sys
from datetime import datetime
import hashlib
from pathlib import Path
import threading
import time

# EXE-safe environment loading
def load_env_safe():
    """Load environment variables safely for EXE compilation"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

# EXE-safe notification system
def setup_notifications_safe():
    """Setup notifications with EXE-safe fallback"""
    try:
        import plyer
        return plyer, True
    except ImportError:
        class MockNotification:
            @staticmethod
            def notify(title="", message="", app_name="", timeout=3):
                print(f"🔔 {title}: {message}")
        
        class MockPlyer:
            notification = MockNotification()
        
        return MockPlyer(), False

# EXE-safe file path handling
def get_app_data_dir():
    """Get application data directory (EXE-safe)"""
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    data_dir = os.path.join(app_dir, "app_data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

# Initialize safely
load_env_safe()
plyer, notification_available = setup_notifications_safe()
APP_DATA_DIR = get_app_data_dir()

class NovrintechEnhancedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NovrinTech AI-Enhanced Desktop Client v3.0")
        
        # Get screen dimensions for responsive sizing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate responsive window size
        window_width = max(1200, min(1600, int(screen_width * 0.85)))
        window_height = max(800, min(1000, int(screen_height * 0.85)))
        
        # Center window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1000, 700)
        
        # Set modern theme colors
        self.bg_color = "#f0f0f0"
        self.primary_color = "#2196F3"
        self.success_color = "#4CAF50"
        self.danger_color = "#f44336"
        self.text_color = "#333333"
        
        self.root.configure(bg=self.bg_color)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Enhanced API Configuration - Your Backend Integration
        self.api_base_url = "https://novrintech-ai.onrender.com"
        self.ai_api_url = "https://novrintech-ai.onrender.com"  # Your AI backend
        self.data_api_url = "https://novrintech-data-fall-back.onrender.com"  # Data backend
        self.api_key = "novrintech_api_key_2024_secure"
        
        # Application Context for AI Understanding
        self.app_context = {
            "application": {
                "name": "NovrinTech AI-Enhanced Desktop Client",
                "version": "3.0",
                "type": "Python tkinter desktop application",
                "purpose": "File management with AI assistance and data operations"
            },
            "features": [
                "AI Chat Assistant with application context awareness",
                "Secure file upload and download with user tracking",
                "Real-time backend health monitoring",
                "Bulk file operations and management",
                "JSON data storage and retrieval",
                "Activity logging and notifications",
                "Responsive UI with zoom controls",
                "Keep-alive system for cloud deployments",
                "Comprehensive keyboard shortcuts",
                "Context-aware help system"
            ],
            "architecture": {
                "frontend": "Python tkinter with ttk styling",
                "ai_backend": "FastAPI with Groq LLM integration",
                "data_backend": "FastAPI with file storage",
                "ai_model": "Llama3-8b-8192 via Groq API",
                "deployment": "Render cloud platform",
                "communication": "REST API with JSON"
            },
            "api_endpoints": {
                "ai_chat": "/api/chat",
                "health_check": "/api/health",
                "keep_alive": "/api/keepalive",
                "file_upload": "/file/upload",
                "file_download": "/file/download/{file_id}",
                "file_list": "/file/list",
                "file_delete": "/file/delete/{file_id}",
                "data_save": "/data/save",
                "data_read": "/data/read"
            },
            "user_capabilities": [
                "Upload files with automatic duplicate detection",
                "Download and manage files with bulk operations",
                "Store and retrieve JSON data",
                "Chat with AI about application features",
                "Monitor system health and performance",
                "Export activity logs and file lists",
                "Customize UI with zoom and preferences"
            ],
            "technical_details": {
                "file_handling": "MD5 hash-based duplicate detection",
                "user_tracking": "Name-based file association",
                "notifications": "Cross-platform with fallback",
                "data_persistence": "Local JSON storage + cloud backend",
                "error_handling": "Comprehensive with user feedback",
                "security": "API key authentication",
                "performance": "Threaded operations for UI responsiveness"
            }
        }
        
        # File tracking and chat system
        self.uploaded_files = {}
        self.chat_messages = []
        self.ai_chat_history = []
        self.load_file_history()
        self.load_chat_history()
        
        # Keep-alive system
        self.keep_alive_running = False
        self.keep_alive_thread = None
        
        # UI and notification system
        self.ui_scale = 1.0
        self.base_font_size = 10
        self.notification_enabled = True
        self.notification_available = notification_available
        self.plyer = plyer
        
        # EXE-safe file paths
        self.app_data_dir = APP_DATA_DIR
        self.history_file = os.path.join(self.app_data_dir, "upload_history.json")
        self.settings_file = os.path.join(self.app_data_dir, "user_settings.json")
        self.chat_file = os.path.join(self.app_data_dir, "chat_history.json")
        self.ai_chat_file = os.path.join(self.app_data_dir, "ai_chat_history.json")
        
        self.setup_ui()
        self.start_keep_alive()
        self.check_backend_health()
        
        # Add startup message
        self.add_chat_message("system", "Application Started", 
                            "NovrinTech AI-Enhanced Desktop Client v3.0 started successfully", "System")
    
    def setup_ui(self):
        # Create custom style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        base_font_size = 10
        if self.root.winfo_screenwidth() > 1600:
            base_font_size = 12
        elif self.root.winfo_screenwidth() < 1200:
            base_font_size = 9
        
        style.configure('Title.TLabel', font=('Arial', base_font_size + 6, 'bold'), 
                       background=self.bg_color, foreground=self.primary_color)
        style.configure('Heading.TLabel', font=('Arial', base_font_size + 2, 'bold'), 
                       background=self.bg_color, foreground=self.text_color)
        style.configure('Success.TLabel', font=('Arial', base_font_size), 
                       background=self.bg_color, foreground=self.success_color)
        style.configure('Error.TLabel', font=('Arial', base_font_size), 
                       background=self.bg_color, foreground=self.danger_color)
        style.configure('Primary.TButton', font=('Arial', base_font_size, 'bold'))
        
        # Main container
        padding = "15" if self.root.winfo_screenwidth() < 1200 else "20"
        main_container = ttk.Frame(self.root, padding=padding)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title with enhanced status bar
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text="🤖 NovrinTech AI-Enhanced Client", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Enhanced status indicators
        status_frame = ttk.Frame(title_frame)
        status_frame.pack(side=tk.RIGHT)
        
        self.ai_status = ttk.Label(status_frame, text="🤖 AI: Connecting...", font=('Arial', 8))
        self.ai_status.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.data_status = ttk.Label(status_frame, text="💾 Data: Connecting...", font=('Arial', 8))
        self.data_status.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.connection_status = ttk.Label(status_frame, text="🔴 Disconnected", font=('Arial', 8))
        self.connection_status.pack(side=tk.RIGHT)
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Enhanced tabs with AI integration
        self.setup_ai_assistant_tab()      # NEW: AI Assistant Tab
        self.setup_config_tab()
        self.setup_upload_tab()
        self.setup_manager_tab()
        self.setup_data_tab()
        self.setup_activity_tab()
        self.setup_app_info_tab()         # NEW: Application Information Tab
    
    def setup_ai_assistant_tab(self):
        """Setup the AI Assistant tab with full application context"""
        ai_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(ai_frame, text="🤖 AI Assistant")
        
        # Header
        header_frame = ttk.Frame(ai_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="🤖 AI Assistant", style='Heading.TLabel').pack(anchor=tk.W)
        ttk.Label(header_frame, text="Powered by Groq LLM with complete application awareness", 
                 font=('Arial', 9, 'italic')).pack(anchor=tk.W)
        
        # Main content with two columns
        main_content = ttk.Frame(ai_frame)
        main_content.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Chat Interface
        left_frame = ttk.Frame(main_content)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # AI Chat Display
        chat_section = ttk.LabelFrame(left_frame, text="💬 AI Conversation", padding="15")
        chat_section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.ai_chat_display = scrolledtext.ScrolledText(
            chat_section, 
            height=20, 
            width=60,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='white'
        )
        self.ai_chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Message input area
        input_section = ttk.Frame(chat_section)
        input_section.pack(fill=tk.X)
        
        ttk.Label(input_section, text="Ask me anything about this application:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        input_frame = ttk.Frame(input_section)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.ai_message_entry = tk.Text(input_frame, height=3, width=50, wrap=tk.WORD, font=('Arial', 10))
        self.ai_message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.ai_message_entry.bind('<Control-Return>', self.send_ai_message)
        
        ai_send_btn = ttk.Button(input_frame, text="🚀 Send", command=self.send_ai_message, style='Primary.TButton')
        ai_send_btn.pack(side=tk.RIGHT)
        
        # Quick action buttons
        quick_actions = ttk.Frame(input_section)
        quick_actions.pack(fill=tk.X)
        
        ttk.Button(quick_actions, text="❓ What can you do?", 
                  command=lambda: self.send_quick_ai_message("What features does this application have and what can you help me with?")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_actions, text="🏗️ Architecture", 
                  command=lambda: self.send_quick_ai_message("Explain the technical architecture of this application")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_actions, text="🔧 Troubleshoot", 
                  command=lambda: self.send_quick_ai_message("I'm having issues with the application. What should I check?")).pack(side=tk.LEFT, padx=(0, 5))
        
        # Right column - AI Status & Context
        right_frame = ttk.Frame(main_content)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # AI Status section
        ai_status_section = ttk.LabelFrame(right_frame, text="🤖 AI Status", padding="15")
        ai_status_section.pack(fill=tk.X, pady=(0, 15))
        
        self.ai_status_label = ttk.Label(ai_status_section, text="Initializing AI connection...", font=('Arial', 10))
        self.ai_status_label.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(ai_status_section, text="🔄 Test AI Connection", command=self.test_ai_connection).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(ai_status_section, text="🧹 Clear Chat", command=self.clear_ai_chat).pack(fill=tk.X)
        
        # Context Information section
        context_section = ttk.LabelFrame(right_frame, text="📋 Application Context", padding="15")
        context_section.pack(fill=tk.X, pady=(0, 15))
        
        context_text = f"""The AI understands:
        
✅ All application features
✅ Technical architecture  
✅ API endpoints & usage
✅ File operations
✅ Data management
✅ Troubleshooting steps
✅ User workflows
✅ System integration

Current Context:
• {len(self.uploaded_files)} files tracked
• {len(self.chat_messages)} activities logged
• Backend: {self.ai_api_url}
• Version: {self.app_context['application']['version']}"""
        
        ttk.Label(context_section, text=context_text, font=('Arial', 8), justify=tk.LEFT).pack(anchor=tk.W)
        
        # Example Questions section
        examples_section = ttk.LabelFrame(right_frame, text="💡 Example Questions", padding="15")
        examples_section.pack(fill=tk.X)
        
        examples = [
            "How do I upload files?",
            "What's the keep-alive system?",
            "How does duplicate detection work?",
            "Explain the API architecture",
            "What keyboard shortcuts are available?",
            "How do I troubleshoot connection issues?"
        ]
        
        for i, example in enumerate(examples[:4]):  # Show first 4
            btn = ttk.Button(examples_section, text=f"• {example}", 
                           command=lambda q=example: self.send_quick_ai_message(q))
            btn.pack(fill=tk.X, pady=1)
        
        # Initialize AI chat
        self.add_ai_message("AI Assistant", 
                           "Hello! I'm your AI assistant with complete knowledge of this application. "
                           "I can help you with features, troubleshooting, technical questions, and more. "
                           "What would you like to know?")
        
        self.load_ai_chat_history()
    
    def setup_app_info_tab(self):
        """Setup comprehensive application information tab"""
        info_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(info_frame, text="ℹ️ App Information")
        
        # Header
        header_frame = ttk.Frame(info_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="ℹ️ Application Information", style='Heading.TLabel').pack(anchor=tk.W)
        ttk.Label(header_frame, text="Complete overview of features, architecture, and capabilities", 
                 font=('Arial', 9, 'italic')).pack(anchor=tk.W)
        
        # Create scrollable text widget for comprehensive info
        info_text_widget = scrolledtext.ScrolledText(info_frame, height=30, width=100,
                                                    bg='#1e1e1e', fg='white', 
                                                    font=('Consolas', 10))
        info_text_widget.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Generate comprehensive application information
        app_info = self.generate_comprehensive_app_info()
        info_text_widget.insert('1.0', app_info)
        info_text_widget.config(state='disabled')
    
    def generate_comprehensive_app_info(self):
        """Generate comprehensive application information for AI context"""
        return f"""
NovrinTech AI-Enhanced Desktop Client - Complete Application Overview
==================================================================

APPLICATION DETAILS:
Name: {self.app_context['application']['name']}
Version: {self.app_context['application']['version']}
Type: {self.app_context['application']['type']}
Purpose: {self.app_context['application']['purpose']}

BACKEND INTEGRATION:
AI Backend: {self.ai_api_url}
Data Backend: {self.data_api_url}
Authentication: API Key based
Keep-alive: Every 4 seconds to prevent cloud sleep

CORE FEATURES:
{chr(10).join(f"• {feature}" for feature in self.app_context['features'])}

ARCHITECTURE OVERVIEW:
Frontend: {self.app_context['architecture']['frontend']}
AI Backend: {self.app_context['architecture']['ai_backend']}
Data Backend: {self.app_context['architecture']['data_backend']}
AI Model: {self.app_context['architecture']['ai_model']}
Deployment: {self.app_context['architecture']['deployment']}
Communication: {self.app_context['architecture']['communication']}

API ENDPOINTS:
{chr(10).join(f"• {endpoint}: {url}" for endpoint, url in self.app_context['api_endpoints'].items())}

USER CAPABILITIES:
{chr(10).join(f"• {capability}" for capability in self.app_context['user_capabilities'])}

TECHNICAL IMPLEMENTATION:
File Handling: {self.app_context['technical_details']['file_handling']}
User Tracking: {self.app_context['technical_details']['user_tracking']}
Notifications: {self.app_context['technical_details']['notifications']}
Data Persistence: {self.app_context['technical_details']['data_persistence']}
Error Handling: {self.app_context['technical_details']['error_handling']}
Security: {self.app_context['technical_details']['security']}
Performance: {self.app_context['technical_details']['performance']}

CURRENT SESSION STATUS:
Files Tracked: {len(self.uploaded_files)}
Activities Logged: {len(self.chat_messages)}
AI Chat Messages: {len(self.ai_chat_history)}
Keep-alive Status: {'Active' if self.keep_alive_running else 'Inactive'}
Notification System: {'Available' if self.notification_available else 'Fallback mode'}

USER WORKFLOWS:

1. FILE UPLOAD WORKFLOW:
   • Enter user name (required)
   • Browse and select file
   • Optional: Enable duplicate detection
   • Click upload
   • System checks for duplicates using MD5 hash
   • File uploaded with user association
   • Activity logged and notification sent

2. FILE MANAGEMENT WORKFLOW:
   • Refresh file list from server
   • Select files for operations
   • Download: Choose save location
   • Delete: Confirm permanent removal
   • Bulk operations: Select multiple files
   • View info: Detailed file metadata

3. AI ASSISTANCE WORKFLOW:
   • Ask questions about application
   • AI has full context of features and architecture
   • Get help with troubleshooting
   • Learn about technical implementation
   • Receive step-by-step guidance

4. DATA OPERATIONS WORKFLOW:
   • Store JSON data with custom keys
   • Retrieve stored configuration
   • Update existing data
   • Delete obsolete entries

KEYBOARD SHORTCUTS:
Global:
• Ctrl+O: Browse & Upload File
• Ctrl+Q: Exit Application
• F5: Refresh File List
• Ctrl+D: Download Selected File
• Ctrl+A: Select All Files
• Delete: Delete Selected File
• Ctrl++: Zoom In
• Ctrl+-: Zoom Out
• Ctrl+0: Reset Zoom

File Manager:
• Enter: View File Info
• Double-click: View File Info
• Right-click: Context Menu
• F5: Refresh Files
• Delete: Delete Selected
• Ctrl+A: Select All
• Ctrl+D: Download Selected

AI Chat:
• Ctrl+Enter: Send Message
• Quick action buttons for common questions

TROUBLESHOOTING GUIDE:

Connection Issues:
• Check internet connectivity
• Verify API endpoints are accessible
• Use "Test Connection" buttons
• Check status indicators in title bar

Upload Problems:
• Ensure file size is reasonable
• Check available disk space
• Verify user name is entered
• Try refreshing and uploading again

Download Issues:
• Refresh file list first
• Check if file exists on server
• Verify sufficient local storage
• Try downloading to different location

AI Chat Problems:
• Test AI connection
• Check backend status
• Clear chat history if needed
• Restart application if persistent

Performance Issues:
• Close unnecessary applications
• Check system resources
• Restart keep-alive system
• Clear application cache

ERROR CODES AND MEANINGS:
200: Success
400: Bad Request (check input data)
401: Unauthorized (check API key)
404: Not Found (file/endpoint missing)
500: Server Error (backend issue)
Timeout: Network or server overload

SECURITY CONSIDERATIONS:
• API keys are stored locally
• File uploads are authenticated
• User names are associated with files
• No sensitive data in logs
• HTTPS communication only

PERFORMANCE OPTIMIZATIONS:
• Threaded operations for UI responsiveness
• Efficient file hash calculations
• Minimal memory footprint
• Optimized network requests
• Smart caching strategies

The AI assistant has complete access to this information and can answer
detailed questions about any aspect of the application, from basic usage
to advanced technical implementation details.
        """
    
    def send_ai_message(self, event=None):
        """Send message to AI assistant with full application context"""
        message = self.ai_message_entry.get(1.0, tk.END).strip()
        if not message:
            return
        
        self.ai_message_entry.delete(1.0, tk.END)
        self.add_ai_message("You", message)
        
        # Send request in separate thread
        threading.Thread(target=self.send_to_ai_backend, args=(message,), daemon=True).start()
    
    def send_quick_ai_message(self, message):
        """Send a quick predefined message to AI"""
        self.ai_message_entry.delete(1.0, tk.END)
        self.ai_message_entry.insert(1.0, message)
        self.send_ai_message()
    
    def send_to_ai_backend(self, user_message):
        """Send message to AI backend with comprehensive context"""
        try:
            # Create comprehensive context message
            context_message = f"""
APPLICATION CONTEXT:
{json.dumps(self.app_context, indent=2)}

CURRENT SESSION DATA:
- Files tracked: {len(self.uploaded_files)}
- Recent activities: {len(self.chat_messages)}
- Backend status: {self.connection_status.cget('text')}
- Keep-alive active: {self.keep_alive_running}

RECENT FILE ACTIVITY:
{json.dumps(list(self.uploaded_files.keys())[-5:] if self.uploaded_files else [], indent=2)}

USER QUESTION: {user_message}

Please provide a helpful response based on the application context above. 
If the question is about this specific application, use the detailed context information.
Be specific and actionable in your responses.
"""
            
            self.ai_status_label.config(text="🤖 AI: Processing...", foreground="blue")
            
            response = requests.post(
                f"{self.ai_api_url}/api/chat",
                json={"message": context_message},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    ai_response = data.get("reply", "No response received")
                    self.root.after(0, lambda: self.add_ai_message("AI Assistant", ai_response))
                    self.root.after(0, lambda: self.ai_status_label.config(text="🤖 AI: Ready", foreground="green"))
                else:
                    error_msg = data.get("error", "Unknown error occurred")
                    self.root.after(0, lambda: self.add_ai_message("Error", f"API Error: {error_msg}"))
                    self.root.after(0, lambda: self.ai_status_label.config(text="🤖 AI: Error", foreground="red"))
            else:
                self.root.after(0, lambda: self.add_ai_message("Error", f"HTTP {response.status_code}: {response.text}"))
                self.root.after(0, lambda: self.ai_status_label.config(text="🤖 AI: Error", foreground="red"))
                
        except requests.exceptions.Timeout:
            self.root.after(0, lambda: self.add_ai_message("Error", "Request timed out. Please try again."))
            self.root.after(0, lambda: self.ai_status_label.config(text="🤖 AI: Timeout", foreground="red"))
        except requests.exceptions.ConnectionError:
            self.root.after(0, lambda: self.add_ai_message("Error", "Cannot connect to AI backend. Please check your connection."))
            self.root.after(0, lambda: self.ai_status_label.config(text="🤖 AI: Offline", foreground="red"))
        except Exception as e:
            self.root.after(0, lambda: self.add_ai_message("Error", f"Unexpected error: {str(e)}"))
            self.root.after(0, lambda: self.ai_status_label.config(text="🤖 AI: Error", foreground="red"))
    
    def add_ai_message(self, sender, message):
        """Add message to AI chat display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add to history
        self.ai_chat_history.append({
            "timestamp": timestamp,
            "sender": sender,
            "message": message
        })
        
        # Update display
        if hasattr(self, 'ai_chat_display'):
            self.ai_chat_display.config(state=tk.NORMAL)
            
            # Color coding for different senders
            if sender == "You":
                self.ai_chat_display.insert(tk.END, f"[{timestamp}] 👤 You:\n", "user_header")
                self.ai_chat_display.insert(tk.END, f"{message}\n\n", "user_message")
            elif sender == "AI Assistant":
                self.ai_chat_display.insert(tk.END, f"[{timestamp}] 🤖 AI Assistant:\n", "ai_header")
                self.ai_chat_display.insert(tk.END, f"{message}\n\n", "ai_message")
            else:
                self.ai_chat_display.insert(tk.END, f"[{timestamp}] ⚠️ {sender}:\n", "error_header")
                self.ai_chat_display.insert(tk.END, f"{message}\n\n", "error_message")
            
            # Configure text tags
            self.ai_chat_display.tag_config("user_header", foreground="#2196F3", font=('Arial', 10, 'bold'))
            self.ai_chat_display.tag_config("user_message", foreground="#1976D2")
            self.ai_chat_display.tag_config("ai_header", foreground="#4CAF50", font=('Arial', 10, 'bold'))
            self.ai_chat_display.tag_config("ai_message", foreground="#388E3C")
            self.ai_chat_display.tag_config("error_header", foreground="#f44336", font=('Arial', 10, 'bold'))
            self.ai_chat_display.tag_config("error_message", foreground="#D32F2F")
            
            self.ai_chat_display.config(state=tk.DISABLED)
            self.ai_chat_display.see(tk.END)
        
        # Save chat history
        self.save_ai_chat_history()
    
    def test_ai_connection(self):
        """Test connection to AI backend"""
        def test_connection():
            try:
                self.root.after(0, lambda: self.ai_status_label.config(text="🤖 AI: Testing...", foreground="blue"))
                
                response = requests.get(f"{self.ai_api_url}/api/health", timeout=10)
                if response.status_code == 200:
                    self.root.after(0, lambda: self.ai_status_label.config(text="🤖 AI: Connected ✓", foreground="green"))
                    self.root.after(0, lambda: self.add_ai_message("System", "AI backend connection successful! Ready to assist you."))
                else:
                    self.root.after(0, lambda: self.ai_status_label.config(text="🤖 AI: Error", foreground="red"))
                    self.root.after(0, lambda: self.add_ai_message("System", f"AI backend returned status {response.status_code}"))
            except Exception as e:
                self.root.after(0, lambda: self.ai_status_label.config(text="🤖 AI: Offline", foreground="red"))
                self.root.after(0, lambda: self.add_ai_message("System", f"AI backend connection failed: {str(e)}"))
        
        threading.Thread(target=test_connection, daemon=True).start()
    
    def clear_ai_chat(self):
        """Clear AI chat history"""
        result = messagebox.askyesno("Clear AI Chat", "Are you sure you want to clear the AI chat history?")
        if result:
            self.ai_chat_history = []
            if hasattr(self, 'ai_chat_display'):
                self.ai_chat_display.config(state=tk.NORMAL)
                self.ai_chat_display.delete(1.0, tk.END)
                self.ai_chat_display.config(state=tk.DISABLED)
            self.save_ai_chat_history()
            self.add_ai_message("System", "Chat history cleared. How can I help you?")
    
    def save_ai_chat_history(self):
        """Save AI chat history to file"""
        try:
            with open(self.ai_chat_file, 'w') as f:
                json.dump(self.ai_chat_history, f, indent=2)
        except Exception as e:
            print(f"Error saving AI chat history: {e}")
    
    def load_ai_chat_history(self):
        """Load AI chat history from file"""
        try:
            if os.path.exists(self.ai_chat_file):
                with open(self.ai_chat_file, 'r') as f:
                    self.ai_chat_history = json.load(f)
                    
                # Restore chat display
                if hasattr(self, 'ai_chat_display') and self.ai_chat_history:
                    for chat in self.ai_chat_history[-20:]:  # Show last 20 messages
                        timestamp = chat.get('timestamp', '')
                        sender = chat.get('sender', '')
                        message = chat.get('message', '')
                        
                        self.ai_chat_display.config(state=tk.NORMAL)
                        if sender == "You":
                            self.ai_chat_display.insert(tk.END, f"[{timestamp}] 👤 You:\n", "user_header")
                            self.ai_chat_display.insert(tk.END, f"{message}\n\n", "user_message")
                        elif sender == "AI Assistant":
                            self.ai_chat_display.insert(tk.END, f"[{timestamp}] 🤖 AI Assistant:\n", "ai_header")
                            self.ai_chat_display.insert(tk.END, f"{message}\n\n", "ai_message")
                        else:
                            self.ai_chat_display.insert(tk.END, f"[{timestamp}] ⚠️ {sender}:\n", "error_header")
                            self.ai_chat_display.insert(tk.END, f"{message}\n\n", "error_message")
                        self.ai_chat_display.config(state=tk.DISABLED)
                    
                    self.ai_chat_display.see(tk.END)
        except Exception as e:
            print(f"Error loading AI chat history: {e}")
            self.ai_chat_history = []
    
    def check_backend_health(self):
        """Check health of both AI and data backends"""
        def health_check():
            # Check AI backend