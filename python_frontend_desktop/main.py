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

# Enhanced imports for new features
try:
    from ai_service import AIService
    from config import APP_CONTEXT
    from chat_database_integration import ChatDatabaseIntegration
    from app_updater import AppUpdater
    from enhanced_chat_integration import EnhancedChatManager
    AI_FEATURES_AVAILABLE = True
    CHAT_DB_AVAILABLE = True
    UPDATE_SYSTEM_AVAILABLE = True
    print("✅ All enhanced features loaded successfully!")
except ImportError as e:
    print(f"⚠️ Some enhanced features not available: {e}")
    AI_FEATURES_AVAILABLE = False
    CHAT_DB_AVAILABLE = False
    UPDATE_SYSTEM_AVAILABLE = False

# EXE-safe environment loading
def load_env_safe():
    """Load environment variables safely for EXE compilation"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        # dotenv not available in EXE, use fallback
        pass

# EXE-safe notification system
def setup_notifications_safe():
    """Setup notifications with EXE-safe fallback"""
    try:
        import plyer
        return plyer, True
    except ImportError:
        # Create a mock plyer for EXE compatibility
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
        # Running as EXE
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(app_dir, "app_data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

# Initialize safely
load_env_safe()
plyer, notification_available = setup_notifications_safe()
APP_DATA_DIR = get_app_data_dir()

class NovrintechDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novrintech Data Fall Back - Desktop Client v2.0")
        
        # Get screen dimensions for responsive sizing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate responsive window size (80% of screen, min 1000x700, max 1400x900)
        window_width = max(1000, min(1400, int(screen_width * 0.8)))
        window_height = max(700, min(900, int(screen_height * 0.8)))
        
        # Center window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(900, 600)  # Minimum size
        
        # Set modern theme colors
        self.bg_color = "#f0f0f0"
        self.primary_color = "#2196F3"
        self.success_color = "#4CAF50"
        self.danger_color = "#f44336"
        self.text_color = "#333333"
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # API Configuration - Embedded for easy testing
        self.api_base_url = "https://novrintech-data-fall-back.onrender.com"
        self.api_key = "novrintech_api_key_2024_secure"
        
        # File tracking
        self.uploaded_files = {}
        self.load_file_history()
        
        # Keep-alive system
        self.keep_alive_running = False
        self.keep_alive_thread = None
        
        # UI scaling factor
        self.ui_scale = 1.0
        self.base_font_size = 10
        
        # Chat and notification system (EXE-safe)
        self.chat_messages = []
        self.notification_enabled = True
        self.notification_available = notification_available
        self.plyer = plyer
        
        # Initialize AI Service
        if AI_FEATURES_AVAILABLE:
            self.ai_service = AIService()
            self.ai_chat_messages = []
        else:
            self.ai_service = None
            self.ai_chat_messages = []
        
        # Initialize Enhanced Chat Manager (tested and working)
        if CHAT_DB_AVAILABLE:
            self.enhanced_chat = EnhancedChatManager(self.api_base_url, self.api_key)
            self.chat_db_sync_enabled = True
            print("✅ Enhanced Chat Database Integration enabled")
        else:
            self.enhanced_chat = None
            self.chat_db_sync_enabled = False
        
        # Initialize App Updater (tested and working)
        if UPDATE_SYSTEM_AVAILABLE:
            self.app_updater = AppUpdater(current_version="2.0")
            self.update_available = False
            print("✅ App Update System enabled")
        else:
            self.app_updater = None
            self.update_available = False
        
        # EXE-safe file paths
        self.app_data_dir = APP_DATA_DIR
        self.history_file = os.path.join(self.app_data_dir, "upload_history.json")
        self.settings_file = os.path.join(self.app_data_dir, "user_settings.json")
        self.chat_file = os.path.join(self.app_data_dir, "chat_history.json")
        
        # Setup menu bar first
        self.setup_menu_bar()
        
        self.setup_ui()
        self.start_keep_alive()
        self.setup_notifications()
        
        # Start enhanced features (tested and working)
        self.start_enhanced_features()
    
    def start_enhanced_features(self):
        """Start enhanced features like auto-update and chat sync"""
        # Start auto-update checker
        if self.app_updater:
            try:
                self.app_updater.start_auto_update_checker(callback=self.handle_update_notification)
                print("✅ Auto-update checker started")
            except Exception as e:
                print(f"⚠️ Auto-update checker failed to start: {e}")
        
        # Start chat database auto-sync
        if self.enhanced_chat and self.chat_db_sync_enabled:
            try:
                self.enhanced_chat.auto_sync_scheduler()
                print("✅ Chat auto-sync started")
            except Exception as e:
                print(f"⚠️ Chat auto-sync failed to start: {e}")
    
    def handle_update_notification(self, update_info):
        """Handle update notification from auto-checker"""
        try:
            # Show notification
            self.show_notification("🔄 Update Available", f"Version {update_info['latest_version']} is available!")
            
            # Show update dialog after a short delay
            self.root.after(2000, lambda: self.show_update_dialog(update_info))
        except Exception as e:
            print(f"Update notification error: {e}")
    
    def show_update_dialog(self, update_info):
        """Show update dialog to user"""
        try:
            latest_version = update_info["latest_version"]
            changelog = update_info.get("changelog", ["• Bug fixes and improvements"])
            
            message = f"""🔄 Update Available!

New version: {latest_version}
Current version: 2.0

What's new:
{chr(10).join(changelog)}

Would you like to download and install this update?"""
            
            result = messagebox.askyesno("Update Available", message)
            
            if result:
                self.app_updater.handle_update_process(update_info)
        except Exception as e:
            print(f"Update dialog error: {e}")
    
    def setup_notifications(self):
        """Setup EXE-safe notification system"""
        try:
            # Import our EXE-safe notification system
            from notification_system import get_notification_system
            self.notification_system = get_notification_system()
            self.notification_available = True
            print("✅ EXE-safe notification system initialized")
        except ImportError:
            # Ultimate fallback
            self.notification_available = False
            print("⚠️ Notification system not available")
    
    def show_notification(self, title, message, timeout=3):
        """Show EXE-safe notification"""
        if not self.notification_enabled:
            return
        
        try:
            if self.notification_available and hasattr(self, 'notification_system'):
                return self.notification_system.show_notification(title, message, timeout)
            else:
                # Console fallback
                print(f"🔔 {title}: {message}")
                return True
        except Exception as e:
            print(f"Notification error: {e}")
            return False
    
    def add_chat_message(self, message_type, title, content, user=None):
        """Add message to chat system with enhanced database sync"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Use enhanced chat manager if available
        if self.enhanced_chat and self.chat_db_sync_enabled:
            # Enhanced message with database sync
            message = self.enhanced_chat.enhanced_add_chat_message(
                message_type, title, content, user, sync_to_db=True
            )
            print(f"💾 Chat message synced to database: {message.get('synced_to_db', False)}")
        else:
            # Fallback to local-only message
            message = {
                "timestamp": timestamp,
                "type": message_type,
                "title": title,
                "content": content,
                "user": user or self.load_user_name() or "Unknown",
                "synced_to_db": False
            }
        
        self.chat_messages.append(message)
        
        # Keep only last 100 messages in memory
        if len(self.chat_messages) > 100:
            self.chat_messages = self.chat_messages[-100:]
        
        # Update chat display if it exists
        if hasattr(self, 'chat_display'):
            self.update_chat_display()
        
        # Save chat history locally (backup)
        self.save_chat_history()
        
        return message
    
    def save_chat_history(self):
        """Save chat history to file"""
        try:
            with open("chat_history.json", 'w') as f:
                json.dump(self.chat_messages, f, indent=2)
        except Exception as e:
            print(f"Error saving chat history: {e}")
    
    def load_chat_history(self):
        """Load chat history from file"""
        try:
            if os.path.exists("chat_history.json"):
                with open("chat_history.json", 'r') as f:
                    self.chat_messages = json.load(f)
        except Exception as e:
            print(f"Error loading chat history: {e}")
            self.chat_messages = []
    
    def setup_menu_bar(self):
        """Setup the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="📁 Browse & Upload File...", command=self.menu_upload_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="🔄 Refresh File List", command=self.refresh_files, accelerator="F5")
        file_menu.add_command(label="📥 Download Selected", command=self.download_file, accelerator="Ctrl+D")
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Exit", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="📋 Select All Files", command=self.select_all_files, accelerator="Ctrl+A")
        edit_menu.add_command(label="🗑️ Delete Selected", command=self.delete_file, accelerator="Del")
        edit_menu.add_separator()
        edit_menu.add_command(label="⚙️ Preferences...", command=self.show_preferences)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="📊 Configuration", command=lambda: self.notebook.select(0))
        view_menu.add_command(label="📁 File Upload", command=lambda: self.notebook.select(1))
        view_menu.add_command(label="📂 File Manager", command=lambda: self.notebook.select(2))
        view_menu.add_command(label="💾 Data Operations", command=lambda: self.notebook.select(3))
        view_menu.add_command(label="🤖 AI Assistant", command=lambda: self.notebook.select(4))
        view_menu.add_command(label="💬 Chat & Notifications", command=lambda: self.notebook.select(5))
        view_menu.add_separator()
        view_menu.add_command(label="🔍 Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="🔍 Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="🔍 Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0")
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="🔗 Test Connection", command=self.test_connection)
        tools_menu.add_command(label="🧹 Clear Upload History", command=self.clear_upload_history)
        tools_menu.add_separator()
        
        # Enhanced Features (tested and working)
        if self.chat_db_sync_enabled:
            tools_menu.add_command(label="💾 Sync Chat to Database", command=self.sync_chat_to_database)
            tools_menu.add_command(label="📥 Load Chat from Database", command=self.load_chat_from_database)
            tools_menu.add_command(label="🔄 Toggle Auto-Sync", command=self.toggle_chat_auto_sync)
            tools_menu.add_separator()
        
        if self.app_updater:
            tools_menu.add_command(label="🔄 Check for Updates", command=self.check_for_updates)
            tools_menu.add_command(label="⚙️ Update Settings", command=self.show_update_settings)
            tools_menu.add_separator()
        
        tools_menu.add_command(label="📊 Show Statistics", command=self.show_statistics)
        tools_menu.add_command(label="📋 Export File List", command=self.export_file_list)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="⌨️ Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="📖 User Guide", command=self.show_user_guide)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ About", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.setup_keyboard_shortcuts()
    
    def setup_keyboard_shortcuts(self):
        """Setup global keyboard shortcuts"""
        self.root.bind("<Control-o>", lambda e: self.menu_upload_file())
        self.root.bind("<Control-q>", lambda e: self.on_closing())
        self.root.bind("<F5>", lambda e: self.refresh_files())
        self.root.bind("<Control-d>", lambda e: self.download_file())
        self.root.bind("<Control-a>", lambda e: self.select_all_files())
        self.root.bind("<Delete>", lambda e: self.delete_file())
        self.root.bind("<Control-plus>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-0>", lambda e: self.reset_zoom())
    
    def setup_ui(self):
        # Create custom style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles with responsive font sizes
        base_font_size = 10
        if self.root.winfo_screenwidth() > 1600:
            base_font_size = 12
        elif self.root.winfo_screenwidth() < 1200:
            base_font_size = 9
        
        style.configure('Title.TLabel', font=('Arial', base_font_size + 6, 'bold'), background=self.bg_color, foreground=self.primary_color)
        style.configure('Heading.TLabel', font=('Arial', base_font_size + 2, 'bold'), background=self.bg_color, foreground=self.text_color)
        style.configure('Success.TLabel', font=('Arial', base_font_size), background=self.bg_color, foreground=self.success_color)
        style.configure('Error.TLabel', font=('Arial', base_font_size), background=self.bg_color, foreground=self.danger_color)
        style.configure('Primary.TButton', font=('Arial', base_font_size, 'bold'))
        
        # Main container with responsive padding
        padding = "15" if self.root.winfo_screenwidth() < 1200 else "20"
        main_container = ttk.Frame(self.root, padding=padding)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title with status bar
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text="🔥 Novrintech Data Fall Back", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.connection_status = ttk.Label(title_frame, text="🔴 Disconnected", font=('Arial', 8))
        self.connection_status.pack(side=tk.RIGHT)
        
        # Create scrollable main content
        self.create_scrollable_content(main_container)
    
    def create_scrollable_content(self, parent):
        """Create scrollable content area for better responsiveness"""
        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(parent, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Main notebook for tabs in scrollable area
        self.notebook = ttk.Notebook(scrollable_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configuration Tab
        config_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(config_frame, text="⚙️ Configuration")
        self.setup_config_tab(config_frame)
        
        # File Upload Tab
        upload_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(upload_frame, text="📁 File Upload")
        self.setup_upload_tab(upload_frame)
        
        # File Manager Tab
        manager_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(manager_frame, text="📂 File Manager")
        self.setup_manager_tab(manager_frame)
        
        # Data Operations Tab
        data_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(data_frame, text="💾 Data Operations")
        self.setup_data_tab(data_frame)
        
        # AI Assistant Tab
        ai_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(ai_frame, text="🤖 AI Assistant")
        self.setup_ai_tab(ai_frame)
        
        # Chat & Notifications Tab
        chat_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(chat_frame, text="💬 Chat & Notifications")
        self.setup_chat_tab(chat_frame)
        
        # Store references for menu actions
        self.canvas = canvas
        self.scrollable_frame = scrollable_frame
    
    def setup_config_tab(self, parent):
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="API Configuration", style='Heading.TLabel').pack(anchor=tk.W)
        ttk.Label(header_frame, text="Pre-configured for instant testing", font=('Arial', 9, 'italic')).pack(anchor=tk.W)
        
        # Configuration section
        config_section = ttk.LabelFrame(parent, text="Connection Settings", padding="15")
        config_section.pack(fill=tk.X, pady=(0, 20))
        
        # API URL
        ttk.Label(config_section, text="API Base URL:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.url_entry = ttk.Entry(config_section, width=70, font=('Arial', 10))
        self.url_entry.insert(0, "https://novrintech-data-fall-back.onrender.com")
        self.url_entry.pack(fill=tk.X, pady=(0, 15))
        
        # API Key
        ttk.Label(config_section, text="API Key:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.key_entry = ttk.Entry(config_section, width=70, show="*", font=('Arial', 10))
        self.key_entry.insert(0, "novrintech_api_key_2024_secure")
        self.key_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Test Connection Button
        button_frame = ttk.Frame(config_section)
        button_frame.pack(fill=tk.X)
        
        test_btn = ttk.Button(button_frame, text="🔗 Test Connection", command=self.test_connection, style='Primary.TButton')
        test_btn.pack(side=tk.LEFT)
        
        # Status section
        status_section = ttk.LabelFrame(parent, text="Status", padding="15")
        status_section.pack(fill=tk.X, pady=(0, 20))
        
        # Connection Status
        self.status_label = ttk.Label(status_section, text="Status: Ready to connect", style='Success.TLabel')
        self.status_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Keep-alive status
        self.keepalive_label = ttk.Label(status_section, text="Keep-alive: Active (prevents backend sleep)", style='Success.TLabel')
        self.keepalive_label.pack(anchor=tk.W)
        
        # Info section
        info_section = ttk.LabelFrame(parent, text="Information", padding="15")
        info_section.pack(fill=tk.X)
        
        info_text = """✅ No configuration needed - ready to use!
🔄 Keep-alive system prevents backend sleep
📁 Upload files with duplicate detection
💾 Store and retrieve JSON data
🔒 Secure API key authentication"""
        
        ttk.Label(info_section, text=info_text, font=('Arial', 9), justify=tk.LEFT).pack(anchor=tk.W)
    
    def setup_upload_tab(self, parent):
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="File Upload", style='Heading.TLabel').pack(anchor=tk.W)
        ttk.Label(header_frame, text="Upload files with automatic duplicate detection", font=('Arial', 9, 'italic')).pack(anchor=tk.W)
        
        # User Information section
        user_section = ttk.LabelFrame(parent, text="User Information", padding="15")
        user_section.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(user_section, text="👤 Your Name:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.user_name_entry = ttk.Entry(user_section, width=50, font=('Arial', 10))
        self.user_name_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Load saved user name if available
        saved_name = self.load_user_name()
        if saved_name:
            self.user_name_entry.insert(0, saved_name)
        
        ttk.Label(user_section, text="ℹ️ Your name will be associated with uploaded files", font=('Arial', 8), foreground="gray").pack(anchor=tk.W)
        
        # File selection section
        file_section = ttk.LabelFrame(parent, text="Select File", padding="15")
        file_section.pack(fill=tk.X, pady=(0, 20))
        
        file_frame = ttk.Frame(file_section)
        file_frame.pack(fill=tk.X)
        
        self.selected_file_label = ttk.Label(file_frame, text="📄 No file selected", font=('Arial', 10))
        self.selected_file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(file_frame, text="📁 Browse Files", command=self.browse_file)
        browse_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Upload options section
        options_section = ttk.LabelFrame(parent, text="Upload Options", padding="15")
        options_section.pack(fill=tk.X, pady=(0, 20))
        
        self.check_duplicates = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_section, text="🔍 Check for duplicates before upload", variable=self.check_duplicates).pack(anchor=tk.W, pady=(0, 10))
        
        # Upload button
        upload_btn = ttk.Button(options_section, text="🚀 Upload File", command=self.upload_file, style='Primary.TButton')
        upload_btn.pack(pady=(5, 0))
        
        # Upload history section
        history_section = ttk.LabelFrame(parent, text="Upload History", padding="15")
        history_section.pack(fill=tk.BOTH, expand=True)
        
        # History treeview
        columns = ("filename", "uploader", "upload_time", "count")
        self.history_tree = ttk.Treeview(history_section, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.history_tree.heading("filename", text="📄 File Name")
        self.history_tree.heading("uploader", text="👤 Uploaded By")
        self.history_tree.heading("upload_time", text="🕒 Last Upload")
        self.history_tree.heading("count", text="📊 Count")
        
        self.history_tree.column("filename", width=250)
        self.history_tree.column("uploader", width=150)
        self.history_tree.column("upload_time", width=150)
        self.history_tree.column("count", width=80)
        
        # Scrollbar for history
        scrollbar = ttk.Scrollbar(history_section, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_history_display()
    
    def setup_manager_tab(self, parent):
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="File Manager", style='Heading.TLabel').pack(anchor=tk.W)
        ttk.Label(header_frame, text="Manage your uploaded files", font=('Arial', 9, 'italic')).pack(anchor=tk.W)
        
        # Controls section
        controls_frame = ttk.LabelFrame(parent, text="Controls", padding="15")
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        controls_row = ttk.Frame(controls_frame)
        controls_row.pack(fill=tk.X)
        
        ttk.Button(controls_row, text="🔄 Refresh Files", command=self.refresh_files, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_row, text="📥 Download Selected", command=self.download_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_row, text="🗑️ Delete Selected", command=self.delete_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_row, text="ℹ️ View Info", command=self.view_file_info).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_row, text="📋 Select All", command=self.select_all_files).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_row, text="🗑️ Bulk Delete", command=self.bulk_delete_files).pack(side=tk.LEFT)
        
        # Files list section
        files_section = ttk.LabelFrame(parent, text="Files", padding="15")
        files_section.pack(fill=tk.BOTH, expand=True)
        
        # Files treeview
        columns = ("file_id", "filename", "type", "size", "upload_date")
        self.files_tree = ttk.Treeview(files_section, columns=columns, show="headings", height=12)
        
        # Configure columns
        self.files_tree.heading("file_id", text="📄 File ID")
        self.files_tree.heading("filename", text="📁 File Name")
        self.files_tree.heading("type", text="🏷️ Type")
        self.files_tree.heading("size", text="📊 Size")
        self.files_tree.heading("upload_date", text="🕒 Upload Date")
        
        self.files_tree.column("file_id", width=250)
        self.files_tree.column("filename", width=200)
        self.files_tree.column("type", width=100)
        self.files_tree.column("size", width=80)
        self.files_tree.column("upload_date", width=150)
        
        # Scrollbar for files
        files_scrollbar = ttk.Scrollbar(files_section, orient=tk.VERTICAL, command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=files_scrollbar.set)
        
        self.files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind keyboard shortcuts and right-click menu
        self.setup_file_manager_bindings()
        
        # Status section
        status_section = ttk.LabelFrame(parent, text="Status & Shortcuts", padding="15")
        status_section.pack(fill=tk.X, pady=(20, 0))
        
        self.files_status_label = ttk.Label(status_section, text="Click 'Refresh Files' to load your files", style='Success.TLabel')
        self.files_status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Shortcuts info
        shortcuts_text = "⌨️ Shortcuts: F5=Refresh | Del=Delete | Ctrl+A=Select All | Ctrl+D=Download | Enter=Info | Right-click=Menu"
        ttk.Label(status_section, text=shortcuts_text, font=('Arial', 8), foreground="gray").pack(anchor=tk.W)
        
        # Auto-refresh on tab load
        self.refresh_files()
    
    def setup_data_tab(self, parent):
        ttk.Label(parent, text="Data Operations", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Save data section
        save_frame = ttk.LabelFrame(parent, text="Save Data")
        save_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(save_frame, text="Data Key:").pack(anchor=tk.W, padx=10)
        self.data_key_entry = ttk.Entry(save_frame, width=40)
        self.data_key_entry.pack(padx=10, pady=5)
        
        ttk.Label(save_frame, text="Data Value (JSON):").pack(anchor=tk.W, padx=10)
        self.data_value_text = scrolledtext.ScrolledText(save_frame, height=5, width=60)
        self.data_value_text.pack(padx=10, pady=5)
        
        ttk.Button(save_frame, text="Save Data", command=self.save_data).pack(pady=10)
        
        # Read data section
        read_frame = ttk.LabelFrame(parent, text="Read Data")
        read_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(read_frame, text="Data Key:").pack(anchor=tk.W, padx=10)
        self.read_key_entry = ttk.Entry(read_frame, width=40)
        self.read_key_entry.pack(padx=10, pady=5)
        
        ttk.Button(read_frame, text="Read Data", command=self.read_data).pack(pady=5)
        
        # Results
        ttk.Label(read_frame, text="Result:").pack(anchor=tk.W, padx=10)
        self.result_text = scrolledtext.ScrolledText(read_frame, height=8, width=60)
        self.result_text.pack(padx=10, pady=5)
    
    def setup_ai_tab(self, parent):
        """Setup AI Assistant tab with comprehensive application awareness"""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="🤖 AI Assistant", style='Heading.TLabel').pack(anchor=tk.W)
        ttk.Label(header_frame, text="Intelligent assistant with complete application knowledge", font=('Arial', 9, 'italic')).pack(anchor=tk.W)
        
        # AI Status section
        status_section = ttk.LabelFrame(parent, text="AI Backend Status", padding="15")
        status_section.pack(fill=tk.X, pady=(0, 15))
        
        status_row = ttk.Frame(status_section)
        status_row.pack(fill=tk.X)
        
        self.ai_status_label = ttk.Label(status_row, text="🔄 Checking AI connection...", font=('Arial', 10))
        self.ai_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(status_row, text="🔍 Check AI Health", command=self.check_ai_health).pack(side=tk.RIGHT)
        
        # Main AI interface with two columns
        main_ai_frame = ttk.Frame(parent)
        main_ai_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Chat interface
        left_ai_frame = ttk.Frame(main_ai_frame)
        left_ai_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # AI Chat section
        chat_section = ttk.LabelFrame(left_ai_frame, text="💬 Chat with AI Assistant", padding="15")
        chat_section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # AI Chat display
        self.ai_chat_display = scrolledtext.ScrolledText(
            chat_section, 
            height=20, 
            width=60,
            wrap=tk.WORD,
            font=('Arial', 10),
            state=tk.DISABLED,
            bg='#f8f9fa',
            fg='#333333'
        )
        self.ai_chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # AI Input section
        input_section = ttk.Frame(chat_section)
        input_section.pack(fill=tk.X)
        
        # Message input
        input_row = ttk.Frame(input_section)
        input_row.pack(fill=tk.X, pady=(0, 10))
        
        self.ai_message_entry = tk.Text(input_row, height=3, width=50, wrap=tk.WORD, font=('Arial', 10))
        self.ai_message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Send button
        send_button_frame = ttk.Frame(input_row)
        send_button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.ai_send_button = ttk.Button(send_button_frame, text="🚀 Send", command=self.send_ai_message, style='Primary.TButton')
        self.ai_send_button.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(send_button_frame, text="🧹 Clear", command=self.clear_ai_chat).pack(fill=tk.X)
        
        # Bind Enter key to send message
        self.ai_message_entry.bind('<Control-Return>', lambda e: self.send_ai_message())
        
        # Right column - Quick actions and context
        right_ai_frame = ttk.Frame(main_ai_frame)
        right_ai_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Quick Questions section
        quick_section = ttk.LabelFrame(right_ai_frame, text="💡 Quick Questions", padding="15")
        quick_section.pack(fill=tk.X, pady=(0, 15))
        
        # Suggested questions
        suggested_questions = self.ai_service.get_suggested_questions()[:8]  # Show first 8
        
        for i, question in enumerate(suggested_questions):
            btn = ttk.Button(quick_section, 
                           text=f"{question[:40]}..." if len(question) > 40 else question,
                           command=lambda q=question: self.ask_quick_question(q))
            btn.pack(fill=tk.X, pady=2)
        
        # Application Context section
        context_section = ttk.LabelFrame(right_ai_frame, text="📋 Application Context", padding="15")
        context_section.pack(fill=tk.X, pady=(0, 15))
        
        context_info = f"""The AI assistant knows about:

✅ All application features and capabilities
✅ File upload and management processes  
✅ Data operations and JSON storage
✅ API endpoints and technical details
✅ Keyboard shortcuts and UI navigation
✅ Troubleshooting and error resolution
✅ Keep-alive system and server management
✅ Notification system and chat features

Ask anything about this application!"""
        
        ttk.Label(context_section, text=context_info, font=('Arial', 9), justify=tk.LEFT, wraplength=250).pack(anchor=tk.W)
        
        # Quick Help section
        help_section = ttk.LabelFrame(right_ai_frame, text="🆘 Quick Help", padding="15")
        help_section.pack(fill=tk.X)
        
        help_topics = ["upload", "download", "delete", "shortcuts", "connection", "data"]
        
        for topic in help_topics:
            btn = ttk.Button(help_section, 
                           text=f"Help: {topic.title()}",
                           command=lambda t=topic: self.show_quick_help(t))
            btn.pack(fill=tk.X, pady=2)
        
        # Initialize AI chat with welcome message
        self.initialize_ai_chat()
        
        # Check AI health on startup
        threading.Thread(target=self.check_ai_health, daemon=True).start()
    
    def initialize_ai_chat(self):
        """Initialize AI chat with welcome message"""
        welcome_message = f"""🤖 Welcome to the AI Assistant!

I'm your intelligent assistant with complete knowledge of the Novrintech Data Fall Back Desktop Client. I understand:

• All application features and how they work
• File upload, download, and management processes
• Data operations and JSON storage capabilities
• API endpoints and technical architecture
• Troubleshooting steps and error resolution
• Keyboard shortcuts and UI navigation
• Keep-alive system and server management

Feel free to ask me anything about this application! I can help you:
- Understand how features work
- Troubleshoot issues
- Learn keyboard shortcuts
- Explain technical concepts
- Guide you through workflows

Try asking: "How do I upload files?" or "What keyboard shortcuts are available?"
"""
        
        self.add_ai_message("assistant", welcome_message)
    
    def send_ai_message(self):
        """Send message to AI assistant"""
        message = self.ai_message_entry.get(1.0, tk.END).strip()
        if not message:
            return
        
        # Clear input
        self.ai_message_entry.delete(1.0, tk.END)
        
        # Add user message to display
        self.add_ai_message("user", message)
        
        # Disable send button during request
        self.ai_send_button.config(state='disabled', text="🔄 Thinking...")
        
        # Send to AI in background thread
        threading.Thread(target=self.process_ai_request, args=(message,), daemon=True).start()
    
    def process_ai_request(self, message):
        """Process AI request in background thread"""
        try:
            # Send to AI service
            result = self.ai_service.send_message_to_ai(message, include_context=True)
            
            # Update UI in main thread
            if result["success"]:
                self.root.after(0, lambda: self.add_ai_message("assistant", result["response"]))
            else:
                error_msg = f"❌ {result['error']}"
                self.root.after(0, lambda: self.add_ai_message("system", error_msg))
                
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            self.root.after(0, lambda: self.add_ai_message("system", error_msg))
        finally:
            # Re-enable send button
            self.root.after(0, lambda: self.ai_send_button.config(state='normal', text="🚀 Send"))
    
    def add_ai_message(self, role, message):
        """Add message to AI chat display"""
        if not hasattr(self, 'ai_chat_display'):
            return
        
        self.ai_chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format message based on role
        if role == "user":
            self.ai_chat_display.insert(tk.END, f"[{timestamp}] 👤 You:\n", "user_header")
            self.ai_chat_display.insert(tk.END, f"{message}\n\n", "user_message")
        elif role == "assistant":
            self.ai_chat_display.insert(tk.END, f"[{timestamp}] 🤖 AI Assistant:\n", "ai_header")
            self.ai_chat_display.insert(tk.END, f"{message}\n\n", "ai_message")
        elif role == "system":
            self.ai_chat_display.insert(tk.END, f"[{timestamp}] ⚙️ System:\n", "system_header")
            self.ai_chat_display.insert(tk.END, f"{message}\n\n", "system_message")
        
        # Configure text tags for styling
        self.ai_chat_display.tag_config("user_header", foreground="#2196F3", font=('Arial', 10, 'bold'))
        self.ai_chat_display.tag_config("user_message", foreground="#1976D2", font=('Arial', 10))
        
        self.ai_chat_display.tag_config("ai_header", foreground="#4CAF50", font=('Arial', 10, 'bold'))
        self.ai_chat_display.tag_config("ai_message", foreground="#388E3C", font=('Arial', 10))
        
        self.ai_chat_display.tag_config("system_header", foreground="#FF9800", font=('Arial', 10, 'bold'))
        self.ai_chat_display.tag_config("system_message", foreground="#F57C00", font=('Arial', 10))
        
        self.ai_chat_display.config(state=tk.DISABLED)
        self.ai_chat_display.see(tk.END)
        
        # Save to AI chat history
        self.ai_chat_messages.append({
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep history manageable
        if len(self.ai_chat_messages) > 100:
            self.ai_chat_messages = self.ai_chat_messages[-100:]
    
    def ask_quick_question(self, question):
        """Ask a predefined quick question"""
        self.ai_message_entry.delete(1.0, tk.END)
        self.ai_message_entry.insert(1.0, question)
        self.send_ai_message()
    
    def show_quick_help(self, topic):
        """Show quick help for a topic"""
        help_text = self.ai_service.get_quick_help(topic)
        self.add_ai_message("system", f"Quick Help - {topic.title()}:\n\n{help_text}")
    
    def clear_ai_chat(self):
        """Clear AI chat display"""
        if hasattr(self, 'ai_chat_display'):
            self.ai_chat_display.config(state=tk.NORMAL)
            self.ai_chat_display.delete(1.0, tk.END)
            self.ai_chat_display.config(state=tk.DISABLED)
        
        self.ai_chat_messages = []
        self.ai_service.clear_ai_chat_history()
        
        # Reinitialize with welcome message
        self.initialize_ai_chat()
    
    def check_ai_health(self):
        """Check AI backend health"""
        try:
            result = self.ai_service.check_ai_health()
            
            if result["success"]:
                status_text = f"🟢 AI Backend Online - Response: {result['response_time']:.2f}s"
                status_color = "green"
            else:
                status_text = f"🔴 AI Backend Offline - {result['error']}"
                status_color = "red"
            
            # Update status label
            if hasattr(self, 'ai_status_label'):
                self.ai_status_label.config(text=status_text, foreground=status_color)
                
        except Exception as e:
            if hasattr(self, 'ai_status_label'):
                self.ai_status_label.config(text=f"🔴 AI Health Check Failed: {str(e)}", foreground="red")
    
    def setup_chat_tab(self, parent):
        """Setup chat and notifications tab"""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="💬 Chat & Notifications", style='Heading.TLabel').pack(anchor=tk.W)
        ttk.Label(header_frame, text="Activity feed and messaging system", font=('Arial', 9, 'italic')).pack(anchor=tk.W)
        
        # Main content with two columns
        main_content = ttk.Frame(parent)
        main_content.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Activity Feed
        left_frame = ttk.Frame(main_content)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Activity feed section
        activity_section = ttk.LabelFrame(left_frame, text="📋 Activity Feed", padding="15")
        activity_section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Activity display
        self.chat_display = scrolledtext.ScrolledText(
            activity_section, 
            height=15, 
            width=50,
            wrap=tk.WORD,
            font=('Arial', 9),
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Activity controls
        activity_controls = ttk.Frame(activity_section)
        activity_controls.pack(fill=tk.X)
        
        ttk.Button(activity_controls, text="🔄 Refresh", command=self.update_chat_display).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(activity_controls, text="🧹 Clear History", command=self.clear_chat_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(activity_controls, text="📤 Export Log", command=self.export_chat_log).pack(side=tk.LEFT)
        
        # Right column - Send Message & Settings
        right_frame = ttk.Frame(main_content)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Send message section
        message_section = ttk.LabelFrame(right_frame, text="📤 Send Message", padding="15")
        message_section.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(message_section, text="Message Type:").pack(anchor=tk.W, pady=(0, 5))
        self.message_type_var = tk.StringVar(value="user")
        message_type_combo = ttk.Combobox(message_section, textvariable=self.message_type_var, 
                                        values=["user", "system", "upload", "download"], 
                                        state="readonly", width=25)
        message_type_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(message_section, text="Title:").pack(anchor=tk.W, pady=(0, 5))
        self.message_title_entry = ttk.Entry(message_section, width=30)
        self.message_title_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(message_section, text="Message:").pack(anchor=tk.W, pady=(0, 5))
        self.message_content_text = tk.Text(message_section, height=4, width=30, wrap=tk.WORD, font=('Arial', 9))
        self.message_content_text.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(message_section, text="📤 Send Message", command=self.send_chat_message, style='Primary.TButton').pack(fill=tk.X)
        
        # Notification settings section
        notif_section = ttk.LabelFrame(right_frame, text="🔔 Notification Settings", padding="15")
        notif_section.pack(fill=tk.X, pady=(0, 15))
        
        self.notif_enabled_var = tk.BooleanVar(value=self.notification_enabled)
        ttk.Checkbutton(notif_section, text="Enable notifications", 
                       variable=self.notif_enabled_var, 
                       command=self.toggle_notifications).pack(anchor=tk.W, pady=(0, 10))
        
        # Notification test
        ttk.Button(notif_section, text="🧪 Test Notification", command=self.test_notification).pack(fill=tk.X, pady=(0, 5))
        
        # Auto-notify settings
        self.auto_notify_upload_var = tk.BooleanVar(value=True)
        self.auto_notify_download_var = tk.BooleanVar(value=True)
        self.auto_notify_delete_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(notif_section, text="Notify on upload", variable=self.auto_notify_upload_var).pack(anchor=tk.W)
        ttk.Checkbutton(notif_section, text="Notify on download", variable=self.auto_notify_download_var).pack(anchor=tk.W)
        ttk.Checkbutton(notif_section, text="Notify on delete", variable=self.auto_notify_delete_var).pack(anchor=tk.W)
        
        # Statistics section
        stats_section = ttk.LabelFrame(right_frame, text="📊 Statistics", padding="15")
        stats_section.pack(fill=tk.X, pady=(0, 15))
        
        self.stats_label = ttk.Label(stats_section, text="Loading statistics...", font=('Arial', 8))
        self.stats_label.pack(anchor=tk.W)
        
        # Chat Database Sync section
        sync_section = ttk.LabelFrame(right_frame, text="💾 Database Sync", padding="15")
        sync_section.pack(fill=tk.X, pady=(0, 15))
        
        # Sync status
        self.sync_status_label = ttk.Label(sync_section, text="🟢 Auto-sync enabled", font=('Arial', 9))
        self.sync_status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Sync controls
        sync_controls = ttk.Frame(sync_section)
        sync_controls.pack(fill=tk.X)
        
        ttk.Button(sync_controls, text="🔄 Sync Now", command=self.manual_sync_chat).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(sync_controls, text="📊 Sync Stats", command=self.show_sync_statistics).pack(side=tk.LEFT)
        
        # Update System section
        update_section = ttk.LabelFrame(right_frame, text="🔄 Updates", padding="15")
        update_section.pack(fill=tk.X)
        
        # Update status
        self.update_status_label = ttk.Label(update_section, text="✅ Up to date", font=('Arial', 9))
        self.update_status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Update controls
        update_controls = ttk.Frame(update_section)
        update_controls.pack(fill=tk.X)
        
        ttk.Button(update_controls, text="🔍 Check Updates", command=self.check_for_updates_manually).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(update_controls, text="ℹ️ Version Info", command=self.show_about).pack(side=tk.LEFT)
        
        # Load chat history and update display
        self.load_chat_history()
        
        # Add startup message
        self.add_chat_message("system", "Application Started", 
                            f"Novrintech Data Fall Back Desktop Client v2.0 started successfully", "System")
        
        self.update_chat_display()
        self.update_chat_stats()
    
    def update_chat_display(self):
        """Update the chat display with recent messages"""
        if not hasattr(self, 'chat_display'):
            return
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        
        # Display recent messages (last 50)
        recent_messages = self.chat_messages[-50:] if len(self.chat_messages) > 50 else self.chat_messages
        
        for message in recent_messages:
            timestamp = message.get('timestamp', '')
            msg_type = message.get('type', 'user')
            title = message.get('title', '')
            content = message.get('content', '')
            user = message.get('user', 'Unknown')
            
            # Format message with colors and icons
            type_icons = {
                'upload': '📤',
                'download': '📥',
                'delete': '🗑️',
                'system': '⚙️',
                'user': '💬'
            }
            
            icon = type_icons.get(msg_type, '💬')
            
            # Insert formatted message
            self.chat_display.insert(tk.END, f"[{timestamp}] {icon} {title}\n", f"title_{msg_type}")
            self.chat_display.insert(tk.END, f"👤 {user}: {content}\n\n", f"content_{msg_type}")
        
        # Configure text tags for colors
        self.chat_display.tag_config("title_upload", foreground="#2196F3", font=('Arial', 9, 'bold'))
        self.chat_display.tag_config("title_download", foreground="#4CAF50", font=('Arial', 9, 'bold'))
        self.chat_display.tag_config("title_delete", foreground="#f44336", font=('Arial', 9, 'bold'))
        self.chat_display.tag_config("title_system", foreground="#FF9800", font=('Arial', 9, 'bold'))
        self.chat_display.tag_config("title_user", foreground="#9C27B0", font=('Arial', 9, 'bold'))
        
        self.chat_display.tag_config("content_upload", foreground="#1976D2")
        self.chat_display.tag_config("content_download", foreground="#388E3C")
        self.chat_display.tag_config("content_delete", foreground="#D32F2F")
        self.chat_display.tag_config("content_system", foreground="#F57C00")
        self.chat_display.tag_config("content_user", foreground="#7B1FA2")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)  # Scroll to bottom
    
    def send_chat_message(self):
        """Send a custom chat message"""
        title = self.message_title_entry.get().strip()
        content = self.message_content_text.get(1.0, tk.END).strip()
        msg_type = self.message_type_var.get()
        
        if not title or not content:
            messagebox.showwarning("Incomplete", "Please enter both title and message")
            return
        
        # Add message to chat
        self.add_chat_message(msg_type, title, content)
        
        # Clear form
        self.message_title_entry.delete(0, tk.END)
        self.message_content_text.delete(1.0, tk.END)
        
        # Show notification
        self.show_notification("💬 Message Sent", f"{title}: {content[:50]}...")
        
        # Update stats
        self.update_chat_stats()
    
    def clear_chat_history(self):
        """Clear chat history"""
        result = messagebox.askyesno("Clear History", "Are you sure you want to clear all chat history?")
        if result:
            self.chat_messages = []
            self.save_chat_history()
            self.update_chat_display()
            self.update_chat_stats()
            self.show_notification("🧹 History Cleared", "Chat history has been cleared")
    
    def export_chat_log(self):
        """Export chat log to file"""
        if not self.chat_messages:
            messagebox.showwarning("No Data", "No chat messages to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Chat Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.chat_messages, f, indent=2)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write("Novrintech Data Fall Back - Chat Log\n")
                        f.write("=" * 50 + "\n\n")
                        
                        for message in self.chat_messages:
                            f.write(f"[{message.get('timestamp', '')}] {message.get('type', '').upper()}\n")
                            f.write(f"Title: {message.get('title', '')}\n")
                            f.write(f"User: {message.get('user', 'Unknown')}\n")
                            f.write(f"Content: {message.get('content', '')}\n")
                            f.write("-" * 30 + "\n\n")
                
                self.show_notification("📤 Export Complete", f"Chat log exported to {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"Chat log exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def toggle_notifications(self):
        """Toggle notification settings"""
        self.notification_enabled = self.notif_enabled_var.get()
        status = "enabled" if self.notification_enabled else "disabled"
        self.show_notification("🔔 Notifications", f"Notifications {status}")
    
    def test_notification(self):
        """Test system notification"""
        self.show_notification("🧪 Test Notification", "This is a test notification from Novrintech Data Fall Back!")
    
    def update_chat_stats(self):
        """Update chat statistics"""
        if not hasattr(self, 'stats_label'):
            return
        
        total_messages = len(self.chat_messages)
        upload_count = len([m for m in self.chat_messages if m.get('type') == 'upload'])
        download_count = len([m for m in self.chat_messages if m.get('type') == 'download'])
        user_messages = len([m for m in self.chat_messages if m.get('type') == 'user'])
        
        stats_text = f"""Total Messages: {total_messages}
Upload Activities: {upload_count}
Download Activities: {download_count}
User Messages: {user_messages}
Notifications: {'Enabled' if self.notification_enabled else 'Disabled'}"""
        
        self.stats_label.config(text=stats_text)
    
    def start_keep_alive(self):
        """Start keep-alive pinging to prevent backend from sleeping"""
        if not self.keep_alive_running:
            self.keep_alive_running = True
            self.keep_alive_thread = threading.Thread(target=self.keep_alive_worker, daemon=True)
            self.keep_alive_thread.start()
            print("🔄 Keep-alive started - pinging backend every 4 seconds")
    
    def stop_keep_alive(self):
        """Stop keep-alive pinging"""
        self.keep_alive_running = False
        if self.keep_alive_thread:
            self.keep_alive_thread.join(timeout=1)
        print("⏹️ Keep-alive stopped")
    
    def keep_alive_worker(self):
        """Background worker that pings the backend every 4 seconds"""
        while self.keep_alive_running:
            try:
                # Ping the backend health endpoint
                response = requests.get(f"{self.api_base_url}/health", timeout=3)
                if response.status_code == 200:
                    print(f"💚 Keep-alive ping successful: {datetime.now().strftime('%H:%M:%S')}")
                    # Update connection status on main thread
                    self.root.after(0, lambda: self.connection_status.config(text="🟢 Online", foreground="green"))
                else:
                    print(f"⚠️ Keep-alive ping returned: {response.status_code}")
                    self.root.after(0, lambda: self.connection_status.config(text="🟡 Issues", foreground="orange"))
            except Exception as e:
                print(f"❌ Keep-alive ping failed: {e}")
                self.root.after(0, lambda: self.connection_status.config(text="🔴 Offline", foreground="red"))
            
            # Wait 4 seconds before next ping
            time.sleep(4)
    
    def get_file_hash(self, filepath):
        """Generate MD5 hash of file for duplicate detection"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def load_user_name(self):
        """Load saved user name from local storage"""
        try:
            user_file = "user_settings.json"
            if os.path.exists(user_file):
                with open(user_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get("user_name", "")
        except:
            pass
        return ""
    
    def save_user_name(self, name):
        """Save user name to local storage"""
        try:
            user_file = "user_settings.json"
            settings = {}
            if os.path.exists(user_file):
                with open(user_file, 'r') as f:
                    settings = json.load(f)
            
            settings["user_name"] = name
            
            with open(user_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving user name: {e}")
    
    def load_file_history(self):
        """Load file upload history from local storage"""
        history_file = "upload_history.json"
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    self.uploaded_files = json.load(f)
            except:
                self.uploaded_files = {}
        else:
            self.uploaded_files = {}
    
    def save_file_history(self):
        """Save file upload history to local storage"""
        with open("upload_history.json", 'w') as f:
            json.dump(self.uploaded_files, f, indent=2)
    
    def update_history_display(self):
        """Update the history treeview"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        for filename, data in self.uploaded_files.items():
            uploader = data.get("uploaded_by", "Unknown")
            self.history_tree.insert("", tk.END, values=(
                filename,
                uploader,
                data.get("last_upload", "Unknown"),
                data.get("count", 0)
            ))
    
    def test_connection(self):
        """Test API connection"""
        self.api_base_url = self.url_entry.get()
        self.api_key = self.key_entry.get()
        
        if not self.api_key:
            messagebox.showerror("Error", "Please enter API key")
            return
        
        try:
            headers = {"X-API-KEY": self.api_key}
            response = requests.get(f"{self.api_base_url}/health", headers=headers, timeout=5)
            
            if response.status_code == 200:
                self.status_label.config(text="Status: Connected ✓", foreground="green")
                self.connection_status.config(text="🟢 Connected", foreground="green")
                messagebox.showinfo("Success", "Connection successful!")
            else:
                self.status_label.config(text="Status: Connection failed", foreground="red")
                self.connection_status.config(text="🔴 Failed", foreground="red")
                messagebox.showerror("Error", f"Connection failed: {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            self.status_label.config(text="Status: Connection failed", foreground="red")
            self.connection_status.config(text="🔴 Error", foreground="red")
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def browse_file(self):
        """Browse and select file"""
        filename = filedialog.askopenfilename(
            title="Select file to upload",
            filetypes=[("All files", "*.*")]
        )
        
        if filename:
            self.selected_file = filename
            self.selected_file_label.config(text=f"Selected: {os.path.basename(filename)}")
    
    def upload_file(self):
        """Upload selected file with user name validation"""
        # Validate user name first
        user_name = self.user_name_entry.get().strip()
        if not user_name:
            messagebox.showerror("Error", "Please enter your name before uploading")
            self.user_name_entry.focus()
            return
        
        if len(user_name) < 2:
            messagebox.showerror("Error", "Please enter a valid name (at least 2 characters)")
            self.user_name_entry.focus()
            return
        
        # Save user name for future use
        self.save_user_name(user_name)
        
        if not hasattr(self, 'selected_file'):
            messagebox.showerror("Error", "Please select a file first")
            return
        
        if not self.api_key:
            messagebox.showerror("Error", "Please configure API key first")
            return
        
        filename = os.path.basename(self.selected_file)
        
        # Check for duplicates if enabled
        if self.check_duplicates.get():
            file_hash = self.get_file_hash(self.selected_file)
            
            # Check if this exact file was uploaded before
            for stored_filename, data in self.uploaded_files.items():
                if data.get("hash") == file_hash and stored_filename != filename:
                    result = messagebox.askyesno(
                        "Duplicate Detected", 
                        f"This file appears to be identical to '{stored_filename}' uploaded previously.\n\nDo you want to upload anyway?"
                    )
                    if not result:
                        return
        
        try:
            headers = {"X-API-KEY": self.api_key}
            
            # Add user name to the upload (we can include it in the filename or as metadata)
            # For now, we'll modify the filename to include the user name
            name_prefix = f"[{user_name}]_"
            upload_filename = f"{name_prefix}{filename}"
            
            with open(self.selected_file, 'rb') as f:
                files = {'file': (upload_filename, f, 'application/octet-stream')}
                response = requests.post(f"{self.api_base_url}/file/upload", headers=headers, files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Update upload history
                current_time = datetime.now().isoformat()
                file_hash = self.get_file_hash(self.selected_file)
                
                if filename in self.uploaded_files:
                    self.uploaded_files[filename]["count"] += 1
                    self.uploaded_files[filename]["last_upload"] = current_time
                    self.uploaded_files[filename]["uploaded_by"] = user_name
                else:
                    self.uploaded_files[filename] = {
                        "count": 1,
                        "first_upload": current_time,
                        "last_upload": current_time,
                        "hash": file_hash,
                        "file_id": result.get("file_id"),
                        "uploaded_by": user_name,
                        "upload_filename": upload_filename
                    }
                
                self.save_file_history()
                self.update_history_display()
                
                success_msg = f"File uploaded successfully!\n\n"
                success_msg += f"👤 Uploaded by: {user_name}\n"
                success_msg += f"📄 Original name: {filename}\n"
                success_msg += f"📁 Server name: {upload_filename}\n"
                success_msg += f"🆔 File ID: {result.get('file_id')}"
                
                messagebox.showinfo("Upload Success", success_msg)
                
                # Add to chat and show notification
                self.add_chat_message("upload", f"File Uploaded: {filename}", 
                                    f"Successfully uploaded {filename} to server", user_name)
                
                if self.auto_notify_upload_var.get() if hasattr(self, 'auto_notify_upload_var') else True:
                    self.show_notification("📤 Upload Complete", f"{user_name} uploaded {filename}")
                
                # Clear selection
                self.selected_file_label.config(text="📄 No file selected")
                if hasattr(self, 'selected_file'):
                    delattr(self, 'selected_file')
            
            elif response.status_code == 500:
                # Handle server error with more detail
                error_msg = "Server error occurred. This might be due to:\n"
                error_msg += "• Database connection issues\n"
                error_msg += "• Missing app configuration\n"
                error_msg += "• Backend service problems\n\n"
                error_msg += f"Technical details: {response.text}"
                messagebox.showerror("Server Error", error_msg)
            
            else:
                messagebox.showerror("Error", f"Upload failed: {response.status_code}\n{response.text}")
        
        except requests.exceptions.Timeout:
            messagebox.showerror("Error", "Upload timed out. The file might be too large or the server is slow.")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error", "Connection failed. Check your internet connection and API URL.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Upload error: {str(e)}")
    
    def refresh_files(self):
        """Refresh files list from backend"""
        if not self.api_key:
            self.files_status_label.config(text="❌ Please configure API key first", foreground="red")
            return
        
        try:
            self.files_status_label.config(text="🔄 Loading files from server...", foreground="blue")
            
            headers = {"X-API-KEY": self.api_key}
            response = requests.get(f"{self.api_base_url}/file/list", headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                files = result.get("files", [])
                
                # Clear existing items
                for item in self.files_tree.get_children():
                    self.files_tree.delete(item)
                
                # Add files to tree
                for file_info in files:
                    file_size = self.format_file_size(file_info.get("file_size", 0))
                    upload_date = self.format_date(file_info.get("created_at", ""))
                    
                    self.files_tree.insert("", tk.END, values=(
                        file_info.get("file_id", ""),
                        file_info.get("file_name", ""),
                        file_info.get("file_type", "Unknown"),
                        file_size,
                        upload_date
                    ))
                
                self.files_status_label.config(text=f"✅ Loaded {len(files)} files from server", foreground="green")
                
                if len(files) == 0:
                    self.files_status_label.config(text="📁 No files found. Upload some files first!", foreground="blue")
                
            else:
                # Fallback to local history if backend list fails
                self.files_status_label.config(text="⚠️ Using local history (server list unavailable)", foreground="orange")
                self.refresh_files_from_history()
        
        except requests.exceptions.RequestException as e:
            # Fallback to local history on connection error
            self.files_status_label.config(text="⚠️ Using local history (connection error)", foreground="orange")
            self.refresh_files_from_history()
    
    def refresh_files_from_history(self):
        """Fallback method to load files from local history"""
        try:
            # Clear existing items
            for item in self.files_tree.get_children():
                self.files_tree.delete(item)
            
            files_added = 0
            for filename, data in self.uploaded_files.items():
                file_id = data.get("file_id", "Unknown")
                file_type = "Unknown"
                
                # Try to guess file type from extension
                if "." in filename:
                    ext = filename.split(".")[-1].lower()
                    if ext in ["txt", "md", "log"]:
                        file_type = "text/plain"
                    elif ext in ["jpg", "jpeg", "png", "gif"]:
                        file_type = "image/*"
                    elif ext in ["pdf"]:
                        file_type = "application/pdf"
                    elif ext in ["zip", "rar"]:
                        file_type = "application/zip"
                    else:
                        file_type = f"*.{ext}"
                
                upload_date = self.format_date(data.get("last_upload", ""))
                
                self.files_tree.insert("", tk.END, values=(
                    file_id,
                    filename,
                    file_type,
                    "Unknown",  # Size not available in local history
                    upload_date
                ))
                files_added += 1
            
            if files_added == 0:
                self.files_status_label.config(text="📁 No files found in history", foreground="blue")
        
        except Exception as e:
            self.files_status_label.config(text="❌ Error loading files", foreground="red")
    
    def download_file(self):
        """Download selected file from server"""
        selected_item = self.files_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a file to download")
            return
        
        if not self.api_key:
            messagebox.showerror("Error", "Please configure API key first")
            return
        
        # Get file info
        item = self.files_tree.item(selected_item[0])
        file_id = item['values'][0]
        file_name = item['values'][1]
        
        if file_id == "Unknown":
            messagebox.showerror("Error", "Cannot download file: File ID not available.\nTry refreshing the file list first.")
            return
        
        # Ask user where to save
        from tkinter import filedialog
        save_path = filedialog.asksaveasfilename(
            title="Save file as...",
            initialfile=file_name,
            defaultextension="",
            filetypes=[("All files", "*.*")]
        )
        
        if not save_path:
            return
        
        try:
            self.files_status_label.config(text=f"📥 Downloading {file_name}...", foreground="blue")
            
            headers = {"X-API-KEY": self.api_key}
            response = requests.get(f"{self.api_base_url}/file/download/{file_id}", headers=headers, timeout=30)
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                self.files_status_label.config(text=f"✅ Downloaded {file_name} ({self.format_file_size(file_size)})", foreground="green")
                messagebox.showinfo("Success", f"File downloaded successfully!\n\nSaved to: {save_path}\nSize: {self.format_file_size(file_size)}")
                
                # Add to chat and show notification
                user_name = self.load_user_name() or "Unknown"
                self.add_chat_message("download", f"File Downloaded: {file_name}", 
                                    f"Downloaded {file_name} ({self.format_file_size(file_size)}) to {os.path.basename(save_path)}", user_name)
                
                if self.auto_notify_download_var.get() if hasattr(self, 'auto_notify_download_var') else True:
                    self.show_notification("📥 Download Complete", f"Downloaded {file_name} ({self.format_file_size(file_size)})")
                
            elif response.status_code == 404:
                self.files_status_label.config(text="❌ File not found on server", foreground="red")
                error_msg = "File not found on server. This can happen if:\n\n"
                error_msg += "• The server was restarted (cloud deployments)\n"
                error_msg += "• The file was deleted by another user\n"
                error_msg += "• There's a server storage issue\n\n"
                error_msg += "Try uploading the file again."
                messagebox.showerror("File Not Found", error_msg)
            else:
                self.files_status_label.config(text="❌ Download failed", foreground="red")
                messagebox.showerror("Error", f"Download failed: {response.status_code}\n{response.text}")
        
        except Exception as e:
            self.files_status_label.config(text="❌ Download error", foreground="red")
            messagebox.showerror("Error", f"Download error: {str(e)}")
    
    def delete_file(self):
        """Delete selected file from server"""
        selected_item = self.files_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a file to delete")
            return
        
        if not self.api_key:
            messagebox.showerror("Error", "Please configure API key first")
            return
        
        # Get file info
        item = self.files_tree.item(selected_item[0])
        file_id = item['values'][0]
        file_name = item['values'][1]
        
        if file_id == "Unknown":
            # Fallback to local history removal
            result = messagebox.askyesno(
                "Remove from History", 
                f"Cannot delete '{file_name}' from server (File ID not available).\n\nRemove from local history instead?"
            )
            
            if result and file_name in self.uploaded_files:
                del self.uploaded_files[file_name]
                self.save_file_history()
                self.refresh_files()
                self.update_history_display()
                messagebox.showinfo("Success", f"'{file_name}' removed from local history")
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to permanently delete '{file_name}' from the server?\n\n⚠️ This action cannot be undone!"
        )
        
        if not result:
            return
        
        try:
            self.files_status_label.config(text=f"🗑️ Deleting {file_name}...", foreground="blue")
            
            headers = {"X-API-KEY": self.api_key}
            response = requests.delete(f"{self.api_base_url}/file/delete/{file_id}", headers=headers, timeout=15)
            
            if response.status_code == 200:
                result_data = response.json()
                self.files_status_label.config(text=f"✅ Deleted {file_name}", foreground="green")
                messagebox.showinfo("Success", f"File '{file_name}' deleted successfully from server!")
                
                # Add to chat and show notification
                user_name = self.load_user_name() or "Unknown"
                self.add_chat_message("delete", f"File Deleted: {file_name}", 
                                    f"Permanently deleted {file_name} from server", user_name)
                
                if self.auto_notify_delete_var.get() if hasattr(self, 'auto_notify_delete_var') else True:
                    self.show_notification("🗑️ Delete Complete", f"Deleted {file_name} from server")
                
                # Also remove from local history if it exists
                if file_name in self.uploaded_files:
                    del self.uploaded_files[file_name]
                    self.save_file_history()
                    self.update_history_display()
                
                # Refresh the file list
                self.refresh_files()
                
            else:
                self.files_status_label.config(text="❌ Delete failed", foreground="red")
                messagebox.showerror("Error", f"Delete failed: {response.text}")
        
        except Exception as e:
            self.files_status_label.config(text="❌ Delete error", foreground="red")
            messagebox.showerror("Error", f"Delete error: {str(e)}")
    
    def view_file_info(self):
        """View detailed file information"""
        selected_item = self.files_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a file to view info")
            return
        
        if not self.api_key:
            messagebox.showerror("Error", "Please configure API key first")
            return
        
        # Get file info
        item = self.files_tree.item(selected_item[0])
        file_id = item['values'][0]
        file_name = item['values'][1]
        file_type = item['values'][2]
        file_size = item['values'][3]
        upload_date = item['values'][4]
        
        if file_id == "Unknown":
            # Show local info
            if file_name in self.uploaded_files:
                data = self.uploaded_files[file_name]
                info_text = f"""📁 Local File Information

File Name: {file_name}
File Type: {file_type}
Upload Count: {data.get('count', 0)}
First Upload: {self.format_date(data.get('first_upload', ''))}
Last Upload: {self.format_date(data.get('last_upload', ''))}
File Hash: {data.get('hash', 'N/A')[:16]}...

⚠️ Note: This file info is from local history.
Try refreshing the file list to get server info."""
                
                messagebox.showinfo("Local File Info", info_text)
            else:
                messagebox.showwarning("Warning", "No information available for this file")
            return
        
        try:
            self.files_status_label.config(text=f"ℹ️ Getting info for {file_name}...", foreground="blue")
            
            headers = {"X-API-KEY": self.api_key}
            response = requests.get(f"{self.api_base_url}/file/read/{file_id}", headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                
                # Create info window
                info_window = tk.Toplevel(self.root)
                info_window.title(f"File Info - {file_name}")
                info_window.geometry("600x500")
                info_window.configure(bg=self.bg_color)
                info_window.resizable(False, False)
                
                # Make window modal
                info_window.transient(self.root)
                info_window.grab_set()
                
                # Center the window
                info_window.update_idletasks()
                x = (info_window.winfo_screenwidth() // 2) - (600 // 2)
                y = (info_window.winfo_screenheight() // 2) - (500 // 2)
                info_window.geometry(f"600x500+{x}+{y}")
                
                # Info content
                info_frame = ttk.Frame(info_window, padding="20")
                info_frame.pack(fill=tk.BOTH, expand=True)
                
                # Title
                ttk.Label(info_frame, text="📄 File Information", style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 20))
                
                # File details
                details_frame = ttk.LabelFrame(info_frame, text="Details", padding="15")
                details_frame.pack(fill=tk.X, pady=(0, 15))
                
                info_text = f"""File ID: {result.get('file_id', 'N/A')}
File Name: {result.get('file_name', 'N/A')}
File Type: {result.get('file_type', 'N/A')}
File Size: {file_size}
Upload Date: {self.format_date(result.get('created_at', ''))}
Server Path: {result.get('file_path', 'N/A')}

Status: ✅ File exists on server"""
                
                info_label = ttk.Label(details_frame, text=info_text, font=('Arial', 10), justify=tk.LEFT)
                info_label.pack(anchor=tk.W)
                
                # Actions frame
                actions_frame = ttk.LabelFrame(info_frame, text="Actions", padding="15")
                actions_frame.pack(fill=tk.X, pady=(0, 15))
                
                actions_row = ttk.Frame(actions_frame)
                actions_row.pack(fill=tk.X)
                
                # Download button
                def download_this_file():
                    info_window.destroy()
                    # Select this item and download
                    for item in self.files_tree.get_children():
                        if self.files_tree.item(item)['values'][0] == file_id:
                            self.files_tree.selection_set(item)
                            self.download_file()
                            break
                
                # Delete button
                def delete_this_file():
                    info_window.destroy()
                    # Select this item and delete
                    for item in self.files_tree.get_children():
                        if self.files_tree.item(item)['values'][0] == file_id:
                            self.files_tree.selection_set(item)
                            self.delete_file()
                            break
                
                ttk.Button(actions_row, text="📥 Download", command=download_this_file).pack(side=tk.LEFT, padx=(0, 10))
                ttk.Button(actions_row, text="🗑️ Delete", command=delete_this_file).pack(side=tk.LEFT, padx=(0, 10))
                
                # Close button
                close_frame = ttk.Frame(info_frame)
                close_frame.pack(fill=tk.X, pady=(15, 0))
                
                ttk.Button(close_frame, text="Close", command=info_window.destroy, style='Primary.TButton').pack()
                
                self.files_status_label.config(text=f"✅ Showing info for {file_name}", foreground="green")
                
            else:
                self.files_status_label.config(text="❌ Failed to get file info", foreground="red")
                messagebox.showerror("Error", f"Failed to get file info: {response.text}")
        
        except Exception as e:
            self.files_status_label.config(text="❌ Info error", foreground="red")
            messagebox.showerror("Error", f"Info error: {str(e)}")
    
    def select_all_files(self):
        """Select all files in the list"""
        try:
            # Select all items
            all_items = self.files_tree.get_children()
            self.files_tree.selection_set(all_items)
            
            count = len(all_items)
            self.files_status_label.config(text=f"✅ Selected {count} files", foreground="green")
            
            if count == 0:
                messagebox.showinfo("Info", "No files to select. Upload some files first!")
        except Exception as e:
            messagebox.showerror("Error", f"Select all error: {str(e)}")
    
    def bulk_delete_files(self):
        """Delete multiple selected files"""
        selected_items = self.files_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select files to delete")
            return
        
        if not self.api_key:
            messagebox.showerror("Error", "Please configure API key first")
            return
        
        # Get file info for all selected files
        files_to_delete = []
        for item in selected_items:
            item_data = self.files_tree.item(item)
            file_id = item_data['values'][0]
            file_name = item_data['values'][1]
            files_to_delete.append((file_id, file_name))
        
        # Confirm bulk deletion
        file_names = [name for _, name in files_to_delete]
        file_list = "\n".join([f"• {name}" for name in file_names[:10]])  # Show first 10
        if len(file_names) > 10:
            file_list += f"\n... and {len(file_names) - 10} more files"
        
        result = messagebox.askyesno(
            "Confirm Bulk Delete", 
            f"Are you sure you want to permanently delete {len(files_to_delete)} files?\n\n{file_list}\n\n⚠️ This action cannot be undone!"
        )
        
        if not result:
            return
        
        # Delete files one by one
        deleted_count = 0
        failed_count = 0
        failed_files = []
        
        try:
            headers = {"X-API-KEY": self.api_key}
            
            for i, (file_id, file_name) in enumerate(files_to_delete):
                try:
                    self.files_status_label.config(text=f"🗑️ Deleting {i+1}/{len(files_to_delete)}: {file_name}...", foreground="blue")
                    self.root.update()  # Update UI
                    
                    if file_id == "Unknown":
                        # Remove from local history only
                        if file_name in self.uploaded_files:
                            del self.uploaded_files[file_name]
                            deleted_count += 1
                        continue
                    
                    response = requests.delete(f"{self.api_base_url}/file/delete/{file_id}", headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        deleted_count += 1
                        # Also remove from local history if it exists
                        if file_name in self.uploaded_files:
                            del self.uploaded_files[file_name]
                    else:
                        failed_count += 1
                        failed_files.append(f"{file_name} ({response.status_code})")
                
                except Exception as e:
                    failed_count += 1
                    failed_files.append(f"{file_name} (Error: {str(e)[:50]})")
            
            # Save updated history
            if deleted_count > 0:
                self.save_file_history()
                self.update_history_display()
            
            # Show results
            if failed_count == 0:
                self.files_status_label.config(text=f"✅ Deleted {deleted_count} files successfully", foreground="green")
                messagebox.showinfo("Success", f"Successfully deleted {deleted_count} files!")
            else:
                self.files_status_label.config(text=f"⚠️ Deleted {deleted_count}, failed {failed_count}", foreground="orange")
                
                failed_list = "\n".join(failed_files[:5])  # Show first 5 failures
                if len(failed_files) > 5:
                    failed_list += f"\n... and {len(failed_files) - 5} more"
                
                messagebox.showwarning("Partial Success", f"Deleted {deleted_count} files successfully.\n\nFailed to delete {failed_count} files:\n{failed_list}")
            
            # Refresh the file list
            self.refresh_files()
            
        except Exception as e:
            self.files_status_label.config(text="❌ Bulk delete error", foreground="red")
            messagebox.showerror("Error", f"Bulk delete error: {str(e)}")
    
    def setup_file_manager_bindings(self):
        """Setup keyboard shortcuts and context menu for file manager"""
        # Keyboard shortcuts
        self.files_tree.bind("<F5>", lambda e: self.refresh_files())
        self.files_tree.bind("<Delete>", lambda e: self.delete_file())
        self.files_tree.bind("<Control-a>", lambda e: self.select_all_files())
        self.files_tree.bind("<Control-d>", lambda e: self.download_file())
        self.files_tree.bind("<Return>", lambda e: self.view_file_info())
        self.files_tree.bind("<Double-1>", lambda e: self.view_file_info())
        
        # Right-click context menu
        self.files_tree.bind("<Button-3>", self.show_context_menu)
        
        # Create context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="📥 Download", command=self.download_file)
        self.context_menu.add_command(label="ℹ️ View Info", command=self.view_file_info)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Delete", command=self.delete_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Select All", command=self.select_all_files)
        self.context_menu.add_command(label="🔄 Refresh", command=self.refresh_files)
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        try:
            # Select the item under cursor
            item = self.files_tree.identify_row(event.y)
            if item:
                self.files_tree.selection_set(item)
                self.files_tree.focus(item)
            
            # Show context menu
            self.context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Context menu error: {e}")
    
    # Menu Action Methods
    def menu_upload_file(self):
        """Menu action to browse and upload file"""
        self.notebook.select(1)  # Switch to upload tab
        self.browse_file()
        if hasattr(self, 'selected_file'):
            self.upload_file()
    
    def show_preferences(self):
        """Show preferences dialog"""
        pref_window = tk.Toplevel(self.root)
        pref_window.title("Preferences")
        pref_window.geometry("400x300")
        pref_window.configure(bg=self.bg_color)
        pref_window.transient(self.root)
        pref_window.grab_set()
        
        # Center the window
        pref_window.update_idletasks()
        x = (pref_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (pref_window.winfo_screenheight() // 2) - (300 // 2)
        pref_window.geometry(f"400x300+{x}+{y}")
        
        ttk.Label(pref_window, text="⚙️ Preferences", style='Heading.TLabel').pack(pady=20)
        ttk.Label(pref_window, text="Preferences will be available in future updates.", font=('Arial', 10)).pack(pady=20)
        ttk.Button(pref_window, text="Close", command=pref_window.destroy).pack(pady=20)
    
    def zoom_in(self):
        """Increase UI scale"""
        if self.ui_scale < 2.0:  # Max 200% zoom
            self.ui_scale += 0.1
            self.apply_zoom()
            self.show_notification("🔍 Zoomed In", f"UI Scale: {int(self.ui_scale * 100)}%")
    
    def zoom_out(self):
        """Decrease UI scale"""
        if self.ui_scale > 0.5:  # Min 50% zoom
            self.ui_scale -= 0.1
            self.apply_zoom()
            self.show_notification("🔍 Zoomed Out", f"UI Scale: {int(self.ui_scale * 100)}%")
    
    def reset_zoom(self):
        """Reset UI scale to default"""
        self.ui_scale = 1.0
        self.apply_zoom()
        self.show_notification("🔍 Zoom Reset", "UI Scale: 100%")
    
    def apply_zoom(self):
        """Apply zoom scale to UI elements"""
        try:
            # Calculate new font size
            new_font_size = int(self.base_font_size * self.ui_scale)
            
            # Update style configurations
            style = ttk.Style()
            style.configure('Title.TLabel', font=('Arial', new_font_size + 6, 'bold'))
            style.configure('Heading.TLabel', font=('Arial', new_font_size + 2, 'bold'))
            style.configure('Success.TLabel', font=('Arial', new_font_size))
            style.configure('Error.TLabel', font=('Arial', new_font_size))
            style.configure('Primary.TButton', font=('Arial', new_font_size, 'bold'))
            
            # Update other UI elements
            self.root.option_add('*Font', f'Arial {new_font_size}')
            
        except Exception as e:
            print(f"Zoom error: {e}")
    
    def clear_upload_history(self):
        """Clear upload history"""
        result = messagebox.askyesno("Clear History", "Are you sure you want to clear all upload history?")
        if result:
            self.uploaded_files = {}
            self.save_file_history()
            self.update_history_display()
            messagebox.showinfo("Success", "Upload history cleared!")
    
    def show_statistics(self):
        """Show application statistics"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistics")
        stats_window.geometry("500x400")
        stats_window.configure(bg=self.bg_color)
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        # Center the window
        stats_window.update_idletasks()
        x = (stats_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (stats_window.winfo_screenheight() // 2) - (400 // 2)
        stats_window.geometry(f"500x400+{x}+{y}")
        
        # Statistics content
        stats_frame = ttk.Frame(stats_window, padding="20")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(stats_frame, text="📊 Application Statistics", style='Heading.TLabel').pack(pady=(0, 20))
        
        # Calculate statistics
        total_files = len(self.uploaded_files)
        total_uploads = sum(data.get('count', 0) for data in self.uploaded_files.values())
        unique_users = len(set(data.get('uploaded_by', 'Unknown') for data in self.uploaded_files.values()))
        
        stats_text = f"""Total Files in History: {total_files}
Total Upload Count: {total_uploads}
Unique Users: {unique_users}
API Base URL: {self.api_base_url}
Keep-alive Status: {'Active' if self.keep_alive_running else 'Inactive'}

Recent Files:"""
        
        ttk.Label(stats_frame, text=stats_text, font=('Arial', 10), justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 20))
        
        # Recent files list
        recent_frame = ttk.Frame(stats_frame)
        recent_frame.pack(fill=tk.BOTH, expand=True)
        
        recent_listbox = tk.Listbox(recent_frame, height=8)
        recent_scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=recent_listbox.yview)
        recent_listbox.configure(yscrollcommand=recent_scrollbar.set)
        
        # Add recent files
        sorted_files = sorted(self.uploaded_files.items(), 
                            key=lambda x: x[1].get('last_upload', ''), reverse=True)
        
        for filename, data in sorted_files[:10]:  # Show last 10 files
            uploader = data.get('uploaded_by', 'Unknown')
            recent_listbox.insert(tk.END, f"{filename} (by {uploader})")
        
        recent_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        recent_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(stats_frame, text="Close", command=stats_window.destroy).pack(pady=(20, 0))
    
    def export_file_list(self):
        """Export file list to CSV"""
        if not self.uploaded_files:
            messagebox.showwarning("No Data", "No files to export. Upload some files first!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export File List",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Filename', 'Uploaded By', 'Upload Count', 'First Upload', 'Last Upload', 'File ID'])
                    
                    for file, data in self.uploaded_files.items():
                        writer.writerow([
                            file,
                            data.get('uploaded_by', 'Unknown'),
                            data.get('count', 0),
                            data.get('first_upload', ''),
                            data.get('last_upload', ''),
                            data.get('file_id', '')
                        ])
                
                messagebox.showinfo("Success", f"File list exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("600x500")
        shortcuts_window.configure(bg=self.bg_color)
        shortcuts_window.transient(self.root)
        shortcuts_window.grab_set()
        
        # Center the window
        shortcuts_window.update_idletasks()
        x = (shortcuts_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (shortcuts_window.winfo_screenheight() // 2) - (500 // 2)
        shortcuts_window.geometry(f"600x500+{x}+{y}")
        
        shortcuts_frame = ttk.Frame(shortcuts_window, padding="20")
        shortcuts_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(shortcuts_frame, text="⌨️ Keyboard Shortcuts", style='Heading.TLabel').pack(pady=(0, 20))
        
        shortcuts_text = """Global Shortcuts:
Ctrl+O          Browse & Upload File
Ctrl+Q          Exit Application
F5              Refresh File List
Ctrl+D          Download Selected File
Ctrl+A          Select All Files
Delete          Delete Selected File
Ctrl++          Zoom In
Ctrl+-          Zoom Out
Ctrl+0          Reset Zoom

File Manager Shortcuts:
Enter           View File Info
Double-click    View File Info
Right-click     Context Menu
F5              Refresh Files
Delete          Delete Selected
Ctrl+A          Select All
Ctrl+D          Download Selected

Navigation:
Tab             Switch between controls
Shift+Tab       Switch backwards
Space           Activate button/checkbox
Arrow Keys      Navigate lists/trees"""
        
        text_widget = tk.Text(shortcuts_frame, wrap=tk.WORD, font=('Courier', 10), height=20)
        text_widget.insert(tk.END, shortcuts_text)
        text_widget.config(state=tk.DISABLED)
        
        text_scrollbar = ttk.Scrollbar(shortcuts_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(shortcuts_frame, text="Close", command=shortcuts_window.destroy).pack(pady=(20, 0))
    
    def show_user_guide(self):
        """Show user guide"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("700x600")
        guide_window.configure(bg=self.bg_color)
        guide_window.transient(self.root)
        guide_window.grab_set()
        
        # Center the window
        guide_window.update_idletasks()
        x = (guide_window.winfo_screenwidth() // 2) - (700 // 2)
        y = (guide_window.winfo_screenheight() // 2) - (600 // 2)
        guide_window.geometry(f"700x600+{x}+{y}")
        
        guide_frame = ttk.Frame(guide_window, padding="20")
        guide_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(guide_frame, text="📖 User Guide", style='Heading.TLabel').pack(pady=(0, 20))
        
        guide_text = """Welcome to Novrintech Data Fall Back Desktop Client!

GETTING STARTED:
1. The application is pre-configured and ready to use
2. Enter your name in the File Upload tab
3. Select a file and click Upload
4. View and manage your files in the File Manager tab

FEATURES:

📁 File Upload:
• Enter your name (required for all uploads)
• Browse and select files to upload
• Automatic duplicate detection
• Upload history tracking

📂 File Manager:
• View all uploaded files
• Download files to your computer
• Delete files from server
• View detailed file information
• Bulk operations (select multiple files)
• Search and filter capabilities

💾 Data Operations:
• Store JSON data with custom keys
• Retrieve stored data
• Perfect for configuration storage

⚙️ Configuration:
• Test API connection
• View system status
• Monitor keep-alive service

TIPS:
• Use keyboard shortcuts for faster navigation
• Right-click in File Manager for context menu
• The app automatically prevents server sleep
• All operations are logged for your reference

TROUBLESHOOTING:
• If upload fails, check your internet connection
• Use "Test Connection" to verify API status
• Check the status indicators in the title bar
• Refresh file list if files don't appear

For technical support, contact the development team."""
        
        text_widget = scrolledtext.ScrolledText(guide_frame, wrap=tk.WORD, font=('Arial', 10), height=25)
        text_widget.insert(tk.END, guide_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        ttk.Button(guide_frame, text="Close", command=guide_window.destroy).pack()
    
    def show_about(self):
        """Show about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("450x350")
        about_window.configure(bg=self.bg_color)
        about_window.transient(self.root)
        about_window.grab_set()
        about_window.resizable(False, False)
        
        # Center the window
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (450 // 2)
        y = (about_window.winfo_screenheight() // 2) - (350 // 2)
        about_window.geometry(f"450x350+{x}+{y}")
        
        about_frame = ttk.Frame(about_window, padding="30")
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        # App icon/title
        ttk.Label(about_frame, text="🔥", font=('Arial', 48)).pack(pady=(0, 10))
        ttk.Label(about_frame, text="Novrintech Data Fall Back", style='Title.TLabel').pack(pady=(0, 5))
        ttk.Label(about_frame, text="Desktop Client v2.0", font=('Arial', 12)).pack(pady=(0, 20))
        
        about_text = """A powerful desktop client for file management and data operations.

Features:
• Secure file upload and download
• User-based file tracking
• Bulk file operations
• Real-time server monitoring
• Responsive design for all screen sizes

Built with Python & Tkinter
© 2024 Novrintech Solutions"""
        
        ttk.Label(about_frame, text=about_text, font=('Arial', 10), justify=tk.CENTER).pack(pady=(0, 30))
        
        ttk.Button(about_frame, text="Close", command=about_window.destroy, style='Primary.TButton').pack()
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def format_date(self, date_string):
        """Format ISO date string to readable format"""
        if not date_string:
            return "Unknown"
        
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return date_string
    
    def save_data(self):
        """Save data to backend"""
        if not self.api_key:
            messagebox.showerror("Error", "Please configure API key first")
            return
        
        data_key = self.data_key_entry.get()
        data_value_str = self.data_value_text.get("1.0", tk.END).strip()
        
        if not data_key or not data_value_str:
            messagebox.showerror("Error", "Please enter both data key and value")
            return
        
        try:
            # Parse JSON
            data_value = json.loads(data_value_str)
            
            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
            payload = {
                "data_key": data_key,
                "data_value": data_value
            }
            
            response = requests.post(f"{self.api_base_url}/data/save", headers=headers, json=payload)
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Data saved successfully!")
                self.data_key_entry.delete(0, tk.END)
                self.data_value_text.delete("1.0", tk.END)
            else:
                messagebox.showerror("Error", f"Save failed: {response.text}")
        
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in data value")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Save error: {str(e)}")
    
    def read_data(self):
        """Read data from backend"""
        if not self.api_key:
            messagebox.showerror("Error", "Please configure API key first")
            return
        
        data_key = self.read_key_entry.get()
        
        if not data_key:
            messagebox.showerror("Error", "Please enter data key")
            return
        
        try:
            headers = {"X-API-KEY": self.api_key}
            response = requests.get(f"{self.api_base_url}/data/read/{data_key}", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                formatted_result = json.dumps(result, indent=2)
                
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert("1.0", formatted_result)
            else:
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert("1.0", f"Error: {response.text}")
        
        except requests.exceptions.RequestException as e:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", f"Error: {str(e)}")
    
    # Enhanced Features - Chat Database Integration (tested and working)
    def sync_chat_to_database(self):
        """Sync chat messages to database"""
        if not self.enhanced_chat:
            messagebox.showwarning("Feature Unavailable", "Chat database sync not available")
            return
        
        try:
            user_name = self.load_user_name() or "Unknown"
            result = self.enhanced_chat.bulk_sync_chat_to_db(self.chat_messages, user_name)
            
            if result["success"]:
                sync_count = len(result.get("sync_results", []))
                messagebox.showinfo("Sync Complete", f"Successfully synced chat history to database!\n\nSynced {sync_count} message groups.")
                
                # Update sync status in chat messages
                for message in self.chat_messages:
                    message["synced_to_db"] = True
                
                self.show_notification("💾 Chat Synced", "Chat history saved to database")
            else:
                messagebox.showerror("Sync Failed", f"Failed to sync chat to database:\n{result['error']}")
        
        except Exception as e:
            messagebox.showerror("Sync Error", f"Chat sync error: {str(e)}")
    
    def load_chat_from_database(self):
        """Load chat messages from database"""
        if not self.enhanced_chat:
            messagebox.showwarning("Feature Unavailable", "Chat database sync not available")
            return
        
        try:
            user_name = self.load_user_name() or "Unknown"
            result = self.enhanced_chat.load_chat_from_db(user_name)
            
            if result["success"]:
                loaded_messages = result["messages"]
                if loaded_messages:
                    # Ask user if they want to merge or replace
                    response = messagebox.askyesnocancel(
                        "Load Chat History",
                        f"Found {len(loaded_messages)} messages in database.\n\nReplace current chat history?",
                        icon="question"
                    )
                    
                    if response is True:  # Replace
                        self.chat_messages = loaded_messages
                        messagebox.showinfo("Chat Loaded", f"Replaced chat history with {len(loaded_messages)} messages from database")
                    elif response is False:  # Merge
                        self.chat_messages.extend(loaded_messages)
                        messagebox.showinfo("Chat Loaded", f"Added {len(loaded_messages)} messages from database")
                    # Cancel = do nothing
                    
                    if response is not None:
                        self.update_chat_display()
                        self.save_chat_history()  # Save locally too
                        self.show_notification("📥 Chat Loaded", "Chat history loaded from database")
                else:
                    messagebox.showinfo("No Data", "No chat history found in database")
            else:
                messagebox.showerror("Load Failed", f"Failed to load chat from database:\n{result['error']}")
        
        except Exception as e:
            messagebox.showerror("Load Error", f"Chat load error: {str(e)}")
    
    def toggle_chat_auto_sync(self):
        """Toggle automatic chat synchronization"""
        if not self.enhanced_chat:
            messagebox.showwarning("Feature Unavailable", "Chat database sync not available")
            return
        
        self.enhanced_chat.auto_sync_enabled = not self.enhanced_chat.auto_sync_enabled
        status = "enabled" if self.enhanced_chat.auto_sync_enabled else "disabled"
        
        messagebox.showinfo("Auto-Sync", f"Automatic chat synchronization {status}")
        self.show_notification("🔄 Auto-Sync", f"Auto-sync {status}")
        
        if self.enhanced_chat.auto_sync_enabled:
            # Start auto-sync scheduler
            self.enhanced_chat.auto_sync_scheduler()
    
    # Enhanced Features - App Update System (tested and working)
    def check_for_updates(self):
        """Check for application updates"""
        if not self.app_updater:
            messagebox.showwarning("Feature Unavailable", "Update system not available")
            return
        
        try:
            self.show_notification("🔍 Checking Updates", "Checking for application updates...")
            
            result = self.app_updater.check_for_updates()
            
            if result["success"]:
                if result["update_available"]:
                    latest_version = result["latest_version"]
                    changelog = result.get("changelog", ["• Bug fixes and improvements"])
                    
                    message = f"""New version available: {latest_version}
Current version: 2.0

Changes:
{chr(10).join(changelog)}

Would you like to download and install the update?"""
                    
                    response = messagebox.askyesno("Update Available", message)
                    
                    if response:
                        self.app_updater.handle_update_process(result)
                else:
                    messagebox.showinfo("No Updates", "You are running the latest version!")
            else:
                messagebox.showerror("Update Check Failed", f"Could not check for updates:\n{result['error']}")
        
        except Exception as e:
            messagebox.showerror("Update Error", f"Update check error: {str(e)}")
    
    def show_update_settings(self):
        """Show update system settings"""
        if not self.app_updater:
            messagebox.showwarning("Feature Unavailable", "Update system not available")
            return
        
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Update Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center the window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (settings_window.winfo_screenheight() // 2) - (300 // 2)
        settings_window.geometry(f"400x300+{x}+{y}")
        
        # Settings content
        settings_frame = ttk.Frame(settings_window, padding="20")
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(settings_frame, text="🔄 Update Settings", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Auto-download setting
        auto_download_var = tk.BooleanVar(value=self.app_updater.strategies["auto_download"])
        ttk.Checkbutton(settings_frame, text="Automatically download updates", 
                       variable=auto_download_var).pack(anchor=tk.W, pady=5)
        
        # Auto-install setting
        auto_install_var = tk.BooleanVar(value=self.app_updater.strategies["auto_install"])
        ttk.Checkbutton(settings_frame, text="Automatically install updates", 
                       variable=auto_install_var).pack(anchor=tk.W, pady=5)
        
        # Backup setting
        backup_var = tk.BooleanVar(value=self.app_updater.strategies["backup_current"])
        ttk.Checkbutton(settings_frame, text="Backup current version before update", 
                       variable=backup_var).pack(anchor=tk.W, pady=5)
        
        # Silent mode setting
        silent_var = tk.BooleanVar(value=self.app_updater.strategies["silent_mode"])
        ttk.Checkbutton(settings_frame, text="Silent updates (no notifications)", 
                       variable=silent_var).pack(anchor=tk.W, pady=5)
        
        # Check frequency
        ttk.Label(settings_frame, text="Check frequency (hours):").pack(anchor=tk.W, pady=(20, 5))
        freq_var = tk.StringVar(value=str(self.app_updater.strategies["check_frequency"] // 3600))
        freq_entry = ttk.Entry(settings_frame, textvariable=freq_var, width=10)
        freq_entry.pack(anchor=tk.W, pady=5)
        
        # Save button
        def save_settings():
            try:
                self.app_updater.strategies["auto_download"] = auto_download_var.get()
                self.app_updater.strategies["auto_install"] = auto_install_var.get()
                self.app_updater.strategies["backup_current"] = backup_var.get()
                self.app_updater.strategies["silent_mode"] = silent_var.get()
                self.app_updater.strategies["check_frequency"] = int(freq_var.get()) * 3600
                
                messagebox.showinfo("Settings Saved", "Update settings saved successfully!")
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number for check frequency")
        
        ttk.Button(settings_frame, text="Save Settings", command=save_settings).pack(pady=(20, 0))
        ttk.Button(settings_frame, text="Cancel", command=settings_window.destroy).pack(pady=5)
    
    def on_closing(self):
        """Handle application closing with enhanced cleanup"""
        print("🔄 Shutting down Novrintech Desktop Client...")
        
        # Stop keep-alive systems
        self.stop_keep_alive()
        
        # Save enhanced chat data
        if self.enhanced_chat and self.chat_db_sync_enabled:
            try:
                user_name = self.load_user_name() or "Unknown"
                self.enhanced_chat.bulk_sync_chat_to_db(self.chat_messages, user_name)
                print("💾 Final chat sync to database completed")
            except Exception as e:
                print(f"⚠️ Final chat sync failed: {e}")
        
        # Stop AI service
        if hasattr(self, 'ai_service') and self.ai_service:
            try:
                self.ai_service.stop_ai_keepalive()
                self.ai_service.save_ai_chat_history()
                print("🤖 AI service stopped and chat saved")
            except Exception as e:
                print(f"⚠️ AI service cleanup failed: {e}")
        
        # Stop enhanced chat auto-sync
        if self.enhanced_chat:
            try:
                self.enhanced_chat.auto_sync_enabled = False
                print("🔄 Chat auto-sync stopped")
            except Exception as e:
                print(f"⚠️ Chat auto-sync stop failed: {e}")
        
        print("✅ Enhanced shutdown complete")
        self.root.destroy()
        
        # Stop AI service and save chat
        if hasattr(self, 'ai_service'):
            self.ai_service.stop_ai_keepalive()
            self.ai_service.save_ai_chat_history()
        
        # Stop chat database sync
        if hasattr(self, 'chat_db_manager'):
            self.chat_db_manager.stop_auto_sync()
            # Force sync remaining messages
            user_name = self.load_user_name() or "Unknown"
            self.chat_db_manager.force_sync_all(self.chat_messages, self.ai_chat_messages, user_name)
        
        self.root.destroy()
    
    def start_update_checker(self):
        """Start automatic update checking"""
        def update_callback(update_info):
            # Schedule update notification in main thread
            self.root.after(0, lambda: self.show_update_notification(update_info))
        
        self.updater.start_auto_update_checker(callback=update_callback)
        print("🔄 Auto-update checker started")
    
    def show_update_notification(self, update_info):
        """Show update notification in main thread"""
        try:
            self.update_available = True
            
            # Show system notification
            self.show_notification("🔄 Update Available", 
                                 f"Version {update_info['latest_version']} is available!")
            
            # Add to chat log
            self.add_chat_message("system", "Update Available", 
                                f"New version {update_info['latest_version']} is available for download", "System")
            
            # Show update dialog
            self.updater.show_update_dialog(self.root)
            
        except Exception as e:
            print(f"Update notification error: {e}")
    
    def start_chat_sync(self):
        """Start chat database synchronization"""
        try:
            user_name = self.load_user_name() or "Unknown"
            result = self.chat_db_manager.start_auto_sync(user_name)
            if result["success"]:
                print("💾 Chat database sync started")
            else:
                print(f"💾 Chat sync error: {result['error']}")
        except Exception as e:
            print(f"Chat sync initialization error: {e}")
    
    def manual_sync_chat(self):
        """Manually sync chat data to database"""
        try:
            user_name = self.load_user_name() or "Unknown"
            result = self.chat_db_manager.force_sync_all(self.chat_messages, self.ai_chat_messages, user_name)
            
            if result.get("chat_sync", {}).get("success") or result.get("ai_sync", {}).get("success"):
                messagebox.showinfo("Sync Complete", "Chat data synchronized to database!")
                self.add_chat_message("system", "Manual Sync", "Chat data manually synced to database", "System")
            else:
                error_msg = result.get("chat_sync", {}).get("error", "Unknown error")
                messagebox.showerror("Sync Error", f"Failed to sync chat data: {error_msg}")
                
        except Exception as e:
            messagebox.showerror("Sync Error", f"Sync failed: {str(e)}")
    
    def check_for_updates_manually(self):
        """Manually check for updates"""
        try:
            result = self.updater.check_for_updates()
            
            if result["success"]:
                if result["update_available"]:
                    self.show_update_notification(result)
                else:
                    messagebox.showinfo("No Updates", f"You have the latest version ({result['current_version']})")
            else:
                messagebox.showerror("Update Check Failed", f"Could not check for updates: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Update Check Error", f"Update check failed: {str(e)}")
    
    def show_sync_statistics(self):
        """Show chat sync statistics"""
        try:
            stats = self.chat_db_manager.get_sync_statistics()
            
            stats_text = f"""💾 Chat Database Sync Statistics

🔄 Auto-sync: {'Enabled' if stats['auto_sync_enabled'] else 'Disabled'}
⏰ Last sync: {stats['last_sync_time'] or 'Never'}
📊 Messages synced: {stats['total_messages_synced']}
❌ Sync errors: {stats['sync_errors']}
📋 Queue size: {stats['queue_size']}
⏱️ Sync interval: {stats['sync_interval']} seconds
🔄 Sync in progress: {'Yes' if stats['sync_in_progress'] else 'No'}

{f"Last error: {stats['last_error']}" if stats['last_error'] else "No recent errors"}"""
            
            messagebox.showinfo("Sync Statistics", stats_text)
            
        except Exception as e:
            messagebox.showerror("Statistics Error", f"Could not load statistics: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NovrintechDesktopApp(root)
    root.mainloop()