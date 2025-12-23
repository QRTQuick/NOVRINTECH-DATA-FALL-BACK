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
        ttk.Label(parent, text="File Manager", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Refresh button
        ttk.Button(parent, text="Refresh Files", command=self.refresh_files).pack(pady=10)
        
        # Files list (placeholder - would need backend endpoint to list files)
        files_frame = ttk.Frame(parent)
        files_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.files_tree = ttk.Treeview(files_frame, columns=("file_id", "filename", "type", "upload_date"), show="headings")
        self.files_tree.heading("file_id", text="File ID")
        self.files_tree.heading("filename", text="File Name")
        self.files_tree.heading("type", text="Type")
        self.files_tree.heading("upload_date", text="Upload Date")
        
        files_scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=files_scrollbar.set)
        
        self.files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File operations
        ops_frame = ttk.Frame(parent)
        ops_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(ops_frame, text="Download Selected", command=self.download_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(ops_frame, text="View Info", command=self.view_file_info).pack(side=tk.LEFT, padx=5)
    
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
        """Refresh files list (placeholder)"""
        messagebox.showinfo("Info", "File listing feature requires backend endpoint implementation")
    
    def download_file(self):
        """Download selected file (placeholder)"""
        messagebox.showinfo("Info", "File download feature requires backend endpoint implementation")
    
    def view_file_info(self):
        """View file information (placeholder)"""
        messagebox.showinfo("Info", "File info feature requires backend endpoint implementation")
    
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