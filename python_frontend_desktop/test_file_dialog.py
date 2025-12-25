#!/usr/bin/env python3
"""
Test file dialog to verify the fix
"""
import tkinter as tk
from tkinter import filedialog, messagebox

def test_file_dialog():
    """Test the file dialog with correct parameters"""
    print("🧪 Testing file dialog...")
    
    try:
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()
        
        # Test the file dialog with correct parameters
        file_name = "test_file.txt"
        
        print("   Testing asksaveasfilename with initialfile parameter...")
        
        # This should work without errors
        save_path = filedialog.asksaveasfilename(
            title="Save file as...",
            initialfile=file_name,
            defaultextension="",
            filetypes=[("All files", "*.*")]
        )
        
        if save_path:
            print(f"   ✅ File dialog worked! Selected: {save_path}")
        else:
            print("   ✅ File dialog worked! (User cancelled)")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"   ❌ File dialog error: {e}")
        if 'root' in locals():
            root.destroy()
        return False

def test_wrong_parameter():
    """Test with wrong parameter to confirm the error"""
    print("\n🧪 Testing with wrong parameter (should fail)...")
    
    try:
        root = tk.Tk()
        root.withdraw()
        
        # This should fail with the same error
        save_path = filedialog.asksaveasfilename(
            title="Save file as...",
            initialvalue="test_file.txt",  # Wrong parameter
            defaultextension="",
            filetypes=[("All files", "*.*")]
        )
        
        root.destroy()
        print("   ⚠️ Unexpectedly worked (should have failed)")
        return False
        
    except Exception as e:
        print(f"   ✅ Expected error: {str(e)[:50]}...")
        if 'root' in locals():
            root.destroy()
        return True

if __name__ == "__main__":
    print("🔥 File Dialog Test")
    print("=" * 40)
    
    # Test correct parameter
    test1 = test_file_dialog()
    
    # Test wrong parameter
    test2 = test_wrong_parameter()
    
    print("\n" + "=" * 40)
    if test1:
        print("✅ File dialog fix is working!")
        print("💡 The main app should work now")
    else:
        print("❌ File dialog still has issues")
    
    print("=" * 40)