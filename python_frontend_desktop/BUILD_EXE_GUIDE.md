# 🔥 How to Compile Novrintech Desktop App to EXE

This guide will teach you how to convert the Python desktop app into a standalone Windows executable (.exe) file.

## Method 1: Using PyInstaller (Recommended)

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Create the EXE

**Basic Command (Single File):**
```bash
pyinstaller --onefile --windowed --name "Novrintech-Desktop" --icon=icon.ico main.py
```

**Advanced Command (With All Features):**
```bash
pyinstaller --onefile ^
    --windowed ^
    --name "Novrintech-Desktop" ^
    --icon=icon.ico ^
    --add-data ".env;." ^
    --hidden-import=tkinter ^
    --hidden-import=requests ^
    --hidden-import=dotenv ^
    main.py
```

### Step 3: Find Your EXE

After compilation, your EXE will be in:
```
python_frontend_desktop/dist/Novrintech-Desktop.exe
```

### Command Explanation:

- `--onefile`: Creates a single executable file
- `--windowed`: No console window (GUI only)
- `--name`: Name of the output executable
- `--icon`: Custom icon for the EXE (optional)
- `--add-data`: Include additional files like .env
- `--hidden-import`: Ensure specific modules are included

---

## Method 2: Using Auto-py-to-exe (GUI Tool)

### Step 1: Install Auto-py-to-exe

```bash
pip install auto-py-to-exe
```

### Step 2: Launch the GUI

```bash
auto-py-to-exe
```

### Step 3: Configure Settings

1. **Script Location**: Browse and select `main.py`
2. **One File**: Select "One File"
3. **Console Window**: Select "Window Based (hide the console)"
4. **Icon**: (Optional) Add an icon file
5. **Additional Files**: Add `.env` file if needed
6. **Advanced**:
   - Add Hidden Imports: `tkinter`, `requests`, `dotenv`

### Step 4: Convert

Click "CONVERT .PY TO .EXE" button and wait for completion.

---

## Method 3: Using cx_Freeze

### Step 1: Install cx_Freeze

```bash
pip install cx_Freeze
```

### Step 2: Create setup.py

Create a file named `setup.py`:

```python
from cx_Freeze import setup, Executable
import sys

# Dependencies
build_exe_options = {
    "packages": ["tkinter", "requests", "dotenv", "hashlib", "json"],
    "include_files": [".env"],
    "excludes": []
}

# Base for Windows GUI
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Novrintech Desktop",
    version="1.0",
    description="Novrintech Data Fall Back Desktop Client",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, target_name="Novrintech-Desktop.exe")]
)
```

### Step 3: Build

```bash
python setup.py build
```

Your EXE will be in the `build` folder.

---

## 📦 Complete Build Script (Recommended)

Create a file named `build.bat`:

```batch
@echo off
echo ========================================
echo Building Novrintech Desktop App to EXE
echo ========================================
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

echo Cleaning completed...
echo.

REM Install PyInstaller if not installed
pip install pyinstaller

echo.
echo Building executable...
echo.

REM Build the EXE
pyinstaller --onefile ^
    --windowed ^
    --name "Novrintech-Desktop" ^
    --add-data ".env;." ^
    --hidden-import=tkinter ^
    --hidden-import=requests ^
    --hidden-import=dotenv ^
    --hidden-import=hashlib ^
    --hidden-import=json ^
    --hidden-import=threading ^
    main.py

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Your EXE is located at:
echo dist\Novrintech-Desktop.exe
echo.
pause
```

### To Use:
1. Save as `build.bat` in the `python_frontend_desktop` folder
2. Double-click `build.bat`
3. Wait for completion
4. Find your EXE in `dist\Novrintech-Desktop.exe`

---

## 🎨 Adding a Custom Icon (Optional)

### Step 1: Get an Icon

- Create or download a `.ico` file
- Name it `icon.ico`
- Place it in the `python_frontend_desktop` folder

### Step 2: Use in Build

Add `--icon=icon.ico` to your PyInstaller command.

---

## 🚀 Distribution

### What to Share:

**Option 1: Just the EXE (Simplest)**
- Share `Novrintech-Desktop.exe`
- Users can run it directly
- No Python installation needed!

**Option 2: EXE + Config (Flexible)**
- Share `Novrintech-Desktop.exe`
- Include `.env` file for custom configuration
- Users can modify API URL if needed

### File Size:
- Expect 15-30 MB for the EXE
- This includes Python runtime and all dependencies

---

## 🔧 Troubleshooting

### Issue: "Failed to execute script"
**Solution**: Add missing imports:
```bash
pyinstaller --onefile --windowed --hidden-import=MODULE_NAME main.py
```

### Issue: "DLL load failed"
**Solution**: Use `--onefile` instead of `--onedir`

### Issue: Antivirus blocks EXE
**Solution**: 
- This is normal for PyInstaller EXEs
- Add exception in antivirus
- Or sign the EXE with a code signing certificate

### Issue: EXE is too large
**Solution**: Use UPX compression:
```bash
pip install pyinstaller[encryption]
pyinstaller --onefile --upx-dir=PATH_TO_UPX main.py
```

---

## ✅ Testing Your EXE

1. **Test on your machine**: Run the EXE directly
2. **Test on clean machine**: Test on a PC without Python installed
3. **Test all features**: Upload files, save data, test connection
4. **Check keep-alive**: Verify backend stays awake

---

## 📝 Quick Reference

**Fastest Build:**
```bash
pyinstaller --onefile --windowed main.py
```

**Production Build:**
```bash
pyinstaller --onefile --windowed --name "Novrintech-Desktop" --icon=icon.ico main.py
```

**With Config File:**
```bash
pyinstaller --onefile --windowed --add-data ".env;." main.py
```

---

## 🎉 Success!

Your Novrintech Desktop App is now a standalone Windows executable!

**Benefits:**
- ✅ No Python installation required
- ✅ Easy to distribute
- ✅ Professional appearance
- ✅ One-click launch
- ✅ Works on any Windows PC

Share your EXE with your team and start using Novrintech Data Fall Back! 🚀
