import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import json
import os
from datetime import datetime
import hashlib
from pathlib import Path
from dotenv import load_dotenv
import threading
import time

# Load environment variables
load_dotenv()

class NovrintechDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novrintech Data Fall Back - Desktop Client")
        self.root.geometry("900x700")
        
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
        
        self.setup_ui()
        self.start_keep_alive()
    
    def setup_ui(self):
        # Create custom style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background=self.bg_color, foreground=self.primary_color)
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), background=self.bg_color, foreground=self.text_color)
        style.configure('Success.TLabel', font=('Arial', 10), background=self.bg_color, foreground=self.success_color)
        style.configure('Error.TLabel', font=('Arial', 10), background=self.bg_color, foreground=self.danger_color)
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
        
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_container, text="🔥 Novrintech Data Fall Back", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Main notebook for tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Configuration Tab
        config_frame = ttk.Frame(notebook, padding="20")
        notebook.add(config_frame, text="⚙️ Configuration")
        self.setup_config_tab(config_frame)
        
        # File Upload Tab
        upload_frame = ttk.Frame(notebook, padding="20")
        notebook.add(upload_frame, text="📁 File Upload")
        self.setup_upload_tab(upload_frame)
        
        # File Manager Tab
        manager_frame = ttk.Frame(notebook, padding="20")
        notebook.add(manager_frame, text="📂 File Manager")
        self.setup_manager_tab(manager_frame)
        
        # Data Operations Tab
        data_frame = ttk.Frame(notebook, padding="20")
        notebook.add(data_frame, text="💾 Data Operations")
        self.setup_data_tab(data_frame)
    
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
        ttk.Checkbutton(options_section, text="🔍 Check for duplicates before upload", variable=self.check_duplicates).pack(anchor=tk.W)
        
        # Upload button
        upload_btn = ttk.Button(options_section, text="🚀 Upload File", command=self.upload_file, style='Primary.TButton')
        upload_btn.pack(pady=(15, 0))
        
        # Upload history section
        history_section = ttk.LabelFrame(parent, text="Upload History", padding="15")
        history_section.pack(fill=tk.BOTH, expand=True)
        
        # History treeview
        columns = ("filename", "upload_time", "count")
        self.history_tree = ttk.Treeview(history_section, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.history_tree.heading("filename", text="📄 File Name")
        self.history_tree.heading("upload_time", text="🕒 Last Upload")
        self.history_tree.heading("count", text="📊 Count")
        
        self.history_tree.column("filename", width=300)
        self.history_tree.column("upload_time", width=200)
        self.history_tree.column("count", width=100)
        
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
                else:
                    print(f"⚠️ Keep-alive ping returned: {response.status_code}")
            except Exception as e:
                print(f"❌ Keep-alive ping failed: {e}")
            
            # Wait 4 seconds before next ping
            time.sleep(4)
    
    def get_file_hash(self, filepath):
        """Generate MD5 hash of file for duplicate detection"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
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
            self.history_tree.insert("", tk.END, values=(
                filename,
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
                messagebox.showinfo("Success", "Connection successful!")
            else:
                self.status_label.config(text="Status: Connection failed", foreground="red")
                messagebox.showerror("Error", f"Connection failed: {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            self.status_label.config(text="Status: Connection failed", foreground="red")
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
        """Upload selected file"""
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
            
            with open(self.selected_file, 'rb') as f:
                files = {'file': (filename, f, 'application/octet-stream')}
                response = requests.post(f"{self.api_base_url}/file/upload", headers=headers, files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Update upload history
                current_time = datetime.now().isoformat()
                file_hash = self.get_file_hash(self.selected_file)
                
                if filename in self.uploaded_files:
                    self.uploaded_files[filename]["count"] += 1
                    self.uploaded_files[filename]["last_upload"] = current_time
                else:
                    self.uploaded_files[filename] = {
                        "count": 1,
                        "first_upload": current_time,
                        "last_upload": current_time,
                        "hash": file_hash,
                        "file_id": result.get("file_id")
                    }
                
                self.save_file_history()
                self.update_history_display()
                
                messagebox.showinfo("Success", f"File uploaded successfully!\nFile ID: {result.get('file_id')}")
                
                # Clear selection
                self.selected_file_label.config(text="No file selected")
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
            initialvalue=file_name,
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
                
            else:
                self.files_status_label.config(text="❌ Download failed", foreground="red")
                messagebox.showerror("Error", f"Download failed: {response.text}")
        
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
    
    def on_closing(self):
        """Handle application closing"""
        print("🔄 Shutting down Novrintech Desktop Client...")
        self.stop_keep_alive()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = NovrintechDesktopApp(root)
    root.mainloop()