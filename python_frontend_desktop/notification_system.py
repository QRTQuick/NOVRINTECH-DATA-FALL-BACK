#!/usr/bin/env python3
"""
EXE-Safe Notification System for Novrintech Desktop Client
Works in both development and compiled EXE environments
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox
import threading
import time

class EXESafeNotifications:
    def __init__(self):
        self.plyer_available = False
        self.notification_queue = []
        self.setup_notification_system()
    
    def setup_notification_system(self):
        """Setup notification system with fallbacks"""
        try:
            # Try to import plyer
            import plyer
            self.plyer = plyer
            self.plyer_available = True
            print("✅ System notifications available (plyer)")
        except ImportError:
            print("⚠️ Plyer not available, using fallback notifications")
            self.plyer_available = False
    
    def show_notification(self, title, message, timeout=3):
        """Show notification with multiple fallback methods"""
        success = False
        
        # Method 1: Try plyer (system notifications)
        if self.plyer_available:
            success = self._try_plyer_notification(title, message, timeout)
        
        # Method 2: Fallback to tkinter popup (EXE-safe)
        if not success:
            success = self._show_tkinter_notification(title, message)
        
        # Method 3: Console fallback
        if not success:
            self._console_notification(title, message)
        
        return success
    
    def _try_plyer_notification(self, title, message, timeout):
        """Try to show plyer notification"""
        try:
            self.plyer.notification.notify(
                title=title,
                message=message,
                app_name="Novrintech Data Fall Back",
                timeout=timeout
            )
            return True
        except Exception as e:
            print(f"Plyer notification failed: {e}")
            return False
    
    def _show_tkinter_notification(self, title, message):
        """Show tkinter-based notification (EXE-safe)"""
        try:
            # Create notification in separate thread to avoid blocking
            def show_popup():
                try:
                    # Create a temporary root if none exists
                    temp_root = tk.Tk()
                    temp_root.withdraw()  # Hide the window
                    
                    # Show notification as info dialog
                    messagebox.showinfo(title, message, parent=temp_root)
                    
                    temp_root.destroy()
                except Exception as e:
                    print(f"Tkinter notification error: {e}")
            
            # Run in thread to avoid blocking
            thread = threading.Thread(target=show_popup, daemon=True)
            thread.start()
            return True
            
        except Exception as e:
            print(f"Tkinter notification failed: {e}")
            return False
    
    def _console_notification(self, title, message):
        """Console fallback notification"""
        print(f"🔔 {title}: {message}")
        return True
    
    def show_toast_notification(self, title, message, duration=3000):
        """Show custom toast notification (EXE-safe)"""
        try:
            def create_toast():
                # Create toast window
                toast = tk.Toplevel()
                toast.title("Notification")
                toast.geometry("300x100")
                toast.configure(bg="#333333")
                toast.overrideredirect(True)  # Remove window decorations
                
                # Position at bottom right of screen
                screen_width = toast.winfo_screenwidth()
                screen_height = toast.winfo_screenheight()
                x = screen_width - 320
                y = screen_height - 120
                toast.geometry(f"300x100+{x}+{y}")
                
                # Make it topmost
                toast.attributes("-topmost", True)
                
                # Add content
                title_label = tk.Label(toast, text=title, bg="#333333", fg="white", 
                                     font=("Arial", 10, "bold"))
                title_label.pack(pady=(10, 5))
                
                message_label = tk.Label(toast, text=message, bg="#333333", fg="white", 
                                       font=("Arial", 9), wraplength=280)
                message_label.pack(pady=(0, 10))
                
                # Auto-close after duration
                def close_toast():
                    try:
                        toast.destroy()
                    except:
                        pass
                
                toast.after(duration, close_toast)
                
                # Click to close
                def on_click(event):
                    close_toast()
                
                toast.bind("<Button-1>", on_click)
                title_label.bind("<Button-1>", on_click)
                message_label.bind("<Button-1>", on_click)
            
            # Run in main thread if possible, otherwise in separate thread
            try:
                create_toast()
            except:
                thread = threading.Thread(target=create_toast, daemon=True)
                thread.start()
            
            return True
            
        except Exception as e:
            print(f"Toast notification failed: {e}")
            return False

# Global notification instance
_notification_system = None

def get_notification_system():
    """Get global notification system instance"""
    global _notification_system
    if _notification_system is None:
        _notification_system = EXESafeNotifications()
    return _notification_system

def show_notification(title, message, timeout=3):
    """Global function to show notifications"""
    return get_notification_system().show_notification(title, message, timeout)

def show_toast(title, message, duration=3000):
    """Global function to show toast notifications"""
    return get_notification_system().show_toast_notification(title, message, duration)

# Test function
def test_notifications():
    """Test all notification methods"""
    print("🧪 Testing notification system...")
    
    notif_system = get_notification_system()
    
    # Test 1: Regular notification
    print("1. Testing regular notification...")
    notif_system.show_notification("Test Notification", "This is a test notification")
    
    time.sleep(2)
    
    # Test 2: Toast notification
    print("2. Testing toast notification...")
    notif_system.show_toast_notification("Toast Test", "This is a toast notification")
    
    print("✅ Notification tests complete!")

if __name__ == "__main__":
    test_notifications()
    input("Press Enter to exit...")