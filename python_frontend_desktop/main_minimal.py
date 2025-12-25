#!/usr/bin/env python3
"""
Minimal Novrintech Desktop Client for EXE compilation
Includes only essential functionality to ensure successful build
"""
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

class NovrintechDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novrintech Data Fall Back - Desktop Client v2.0")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # API Configuration
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
        """Setup the user interface"""
        # Main container
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_container, text="🔥 Novrintech Data Fall Back", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Status indicator
        self.connection_status = ttk.Label(main_container, text="🔴 Disconnected", 
                                         font=('Arial', 10))
        self.connection_status.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
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
    
    def setup_config_tab(self, parent):
        """Setup configuration tab"""
        ttk.Label(parent, text="API Configuration", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # API URL
        ttk.Label(parent, text="API Base URL:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.url_entry = ttk.Entry(parent, width=70, font=('Arial', 10))
        self.url_entry.insert(0, self.api_base_url)
        self.url_entry.pack(fill=tk.X, pady=(0, 15))
        
        # API Key
        ttk.Label(parent, text="API Key:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.key_entry = ttk.Entry(parent, width=70, show="*", font=('Arial', 10))
        self.key_entry.insert(0, self.api_key)
        self.key_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Test Connection Button
        ttk.Button(parent, text="🔗 Test Connection", command=self.test_connection).pack(pady=10)
        
        # Status
        self.status_label = ttk.Label(parent, text="Status: Ready to connect", font=('Arial', 10))
        self.status_label.pack(pady=10)
    
    def setup_upload_tab(self, parent):
        """Setup file upload tab"""
        ttk.Label(parent, text="File Upload", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # User name
        ttk.Label(parent, text="👤 Your Name:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.user_name_entry = ttk.Entry(parent, width=50, font=('Arial', 10))
        self.user_name_entry.pack(fill=tk.X, pady=(0, 15))
        
        # File selection
        file_frame = ttk.Frame(parent)
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.selected_file_label = ttk.Label(file_frame, text="📄 No file selected", font=('Arial', 10))
        self.selected_file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(file_frame, text="📁 Browse Files", command=self.browse_file).pack(side=tk.RIGHT)
        
        # Upload button
        ttk.Button(parent, text="🚀 Upload File", command=self.upload_file).pack(pady=10)
        
        # Upload history
        ttk.Label(parent, text="Upload History", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(20, 10))
        
        # History listbox
        self.history_listbox = tk.Listbox(parent, height=8)
        self.history_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.update_history_display()
    
    def setup_manager_tab(self, parent):
        """Setup file manager tab"""
        ttk.Label(parent, text="File Manager", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(controls_frame, text="🔄 Refresh Files", command=self.refresh_files).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="📥 Download Selected", command=self.download_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="🗑️ Delete Selected", command=self.delete_file).pack(side=tk.LEFT)
        
        # Files list
        self.files_listbox = tk.Listbox(parent, height=15)
        self.files_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Status
        self.files_status_label = ttk.Label(parent, text="Click 'Refresh Files' to load your files", font=('Arial', 10))
        self.files_status_label.pack()
    
    def start_keep_alive(self):
        """Start keep-alive pinging"""
        if not self.keep_alive_running:
            self.keep_alive_running = True
            self.keep_alive_thread = threading.Thread(target=self.keep_alive_worker, daemon=True)
            self.keep_alive_thread.start()
    
    def keep_alive_worker(self):
        """Background worker that pings the backend"""
        while self.keep_alive_running:
            try:
                response = requests.get(f"{self.api_base_url}/health", timeout=3)
                if response.status_code == 200:
                    self.root.after(0, lambda: self.connection_status.config(text="🟢 Online"))
                else:
                    self.root.after(0, lambda: self.connection_status.config(text="🟡 Issues"))
            except:
                self.root.after(0, lambda: self.connection_status.config(text="🔴 Offline"))
            time.sleep(5)
    
    def load_file_history(self):
        """Load file upload history"""
        try:
            if os.path.exists("upload_history.json"):
                with open("upload_history.json", 'r') as f:
                    self.uploaded_files = json.load(f)
        except:
            self.uploaded_files = {}
    
    def save_file_history(self):
        """Save file upload history"""
        try:
            with open("upload_history.json", 'w') as f:
                json.dump(self.uploaded_files, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def update_history_display(self):
        """Update the history display"""
        if hasattr(self, 'history_listbox'):
            self.history_listbox.delete(0, tk.END)
            for filename, data in self.uploaded_files.items():
                uploader = data.get("uploaded_by", "Unknown")
                count = data.get("count", 0)
                self.history_listbox.insert(tk.END, f"{filename} (by {uploader}, {count} uploads)")
    
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
                self.status_label.config(text="Status: Connected ✓")
                self.connection_status.config(text="🟢 Connected")
                messagebox.showinfo("Success", "Connection successful!")
            else:
                self.status_label.config(text="Status: Connection failed")
                self.connection_status.config(text="🔴 Failed")
                messagebox.showerror("Error", f"Connection failed: {response.status_code}")
        except Exception as e:
            self.status_label.config(text="Status: Connection failed")
            self.connection_status.config(text="🔴 Error")
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
        user_name = self.user_name_entry.get().strip()
        if not user_name:
            messagebox.showerror("Error", "Please enter your name")
            return
        
        if not hasattr(self, 'selected_file'):
            messagebox.showerror("Error", "Please select a file first")
            return
        
        if not self.api_key:
            messagebox.showerror("Error", "Please configure API key first")
            return
        
        try:
            headers = {"X-API-KEY": self.api_key}
            filename = os.path.basename(self.selected_file)
            upload_filename = f"[{user_name}]_{filename}"
            
            with open(self.selected_file, 'rb') as f:
                files = {'file': (upload_filename, f, 'application/octet-stream')}
                response = requests.post(f"{self.api_base_url}/file/upload", headers=headers, files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Update history
                current_time = datetime.now().isoformat()
                if filename in self.uploaded_files:
                    self.uploaded_files[filename]["count"] += 1
                    self.uploaded_files[filename]["last_upload"] = current_time
                else:
                    self.uploaded_files[filename] = {
                        "count": 1,
                        "first_upload": current_time,
                        "last_upload": current_time,
                        "file_id": result.get("file_id"),
                        "uploaded_by": user_name
                    }
                
                self.save_file_history()
                self.update_history_display()
                
                messagebox.showinfo("Success", f"File uploaded successfully!\nFile ID: {result.get('file_id')}")
                
                # Clear selection
                self.selected_file_label.config(text="📄 No file selected")
                if hasattr(self, 'selected_file'):
                    delattr(self, 'selected_file')
            else:
                messagebox.showerror("Error", f"Upload failed: {response.status_code}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Upload error: {str(e)}")
    
    def refresh_files(self):
        """Refresh files list"""
        if not self.api_key:
            self.files_status_label.config(text="❌ Please configure API key first")
            return
        
        try:
            self.files_status_label.config(text="🔄 Loading files...")
            
            headers = {"X-API-KEY": self.api_key}
            response = requests.get(f"{self.api_base_url}/file/list", headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                files = result.get("files", [])
                
                self.files_listbox.delete(0, tk.END)
                for file_info in files:
                    file_name = file_info.get("file_name", "")
                    file_id = file_info.get("file_id", "")
                    self.files_listbox.insert(tk.END, f"{file_name} (ID: {file_id})")
                
                self.files_status_label.config(text=f"✅ Loaded {len(files)} files")
            else:
                self.files_status_label.config(text="❌ Failed to load files")
        
        except Exception as e:
            self.files_status_label.config(text="❌ Connection error")
    
    def download_file(self):
        """Download selected file"""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to download")
            return
        
        # Extract file ID from selection
        selected_text = self.files_listbox.get(selection[0])
        try:
            file_id = selected_text.split("(ID: ")[1].split(")")[0]
            file_name = selected_text.split(" (ID: ")[0]
        except:
            messagebox.showerror("Error", "Could not parse file information")
            return
        
        # Ask where to save
        save_path = filedialog.asksaveasfilename(
            title="Save file as...",
            initialfile=file_name,
            filetypes=[("All files", "*.*")]
        )
        
        if not save_path:
            return
        
        try:
            headers = {"X-API-KEY": self.api_key}
            response = requests.get(f"{self.api_base_url}/file/download/{file_id}", headers=headers, timeout=30)
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                messagebox.showinfo("Success", f"File downloaded successfully!\nSaved to: {save_path}")
            else:
                messagebox.showerror("Error", f"Download failed: {response.status_code}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Download error: {str(e)}")
    
    def delete_file(self):
        """Delete selected file"""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to delete")
            return
        
        # Extract file ID from selection
        selected_text = self.files_listbox.get(selection[0])
        try:
            file_id = selected_text.split("(ID: ")[1].split(")")[0]
            file_name = selected_text.split(" (ID: ")[0]
        except:
            messagebox.showerror("Error", "Could not parse file information")
            return
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{file_name}'?")
        if not result:
            return
        
        try:
            headers = {"X-API-KEY": self.api_key}
            response = requests.delete(f"{self.api_base_url}/file/delete/{file_id}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "File deleted successfully!")
                self.refresh_files()  # Refresh the list
            else:
                messagebox.showerror("Error", f"Delete failed: {response.status_code}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Delete error: {str(e)}")
    
    def on_closing(self):
        """Handle application closing"""
        self.keep_alive_running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = NovrintechDesktopApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()