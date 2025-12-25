#!/usr/bin/env python3
"""
Verify that the file dialog fix is applied correctly
"""
import re

def verify_fix():
    """Verify the fix is applied"""
    print("🔍 Verifying File Dialog Fix")
    print("=" * 40)
    
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for wrong parameter
        wrong_patterns = [
            r"initialvalue\s*=",
            r"initialvalue:",
        ]
        
        wrong_found = False
        for pattern in wrong_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"❌ Found wrong parameter: {matches}")
                wrong_found = True
        
        if not wrong_found:
            print("✅ No wrong 'initialvalue' parameters found")
        
        # Check for correct parameter
        correct_patterns = [
            r"initialfile\s*=",
        ]
        
        correct_found = False
        for pattern in correct_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"✅ Found correct parameter: {matches}")
                correct_found = True
        
        # Find all file dialog calls
        dialog_pattern = r"filedialog\.asksaveasfilename\([^)]+\)"
        dialogs = re.findall(dialog_pattern, content, re.DOTALL)
        
        print(f"\n📋 Found {len(dialogs)} file dialog calls:")
        for i, dialog in enumerate(dialogs, 1):
            # Clean up the dialog call for display
            clean_dialog = re.sub(r'\s+', ' ', dialog.strip())
            if len(clean_dialog) > 80:
                clean_dialog = clean_dialog[:77] + "..."
            print(f"   {i}. {clean_dialog}")
            
            # Check if this specific dialog has the wrong parameter
            if "initialvalue" in dialog.lower():
                print(f"      ❌ This dialog has 'initialvalue' (wrong)")
            elif "initialfile" in dialog.lower():
                print(f"      ✅ This dialog has 'initialfile' (correct)")
        
        print("\n" + "=" * 40)
        
        if wrong_found:
            print("❌ FIX NOT APPLIED - Still has wrong parameters")
            print("💡 The error will continue until this is fixed")
            return False
        elif correct_found:
            print("✅ FIX APPLIED CORRECTLY")
            print("💡 The app should work without file dialog errors")
            return True
        else:
            print("⚠️ NO FILE DIALOG PARAMETERS FOUND")
            print("💡 This might be okay if no dialogs use initialfile")
            return True
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    verify_fix()
    input("\nPress Enter to exit...")