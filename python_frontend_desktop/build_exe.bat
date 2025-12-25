@echo off
echo 🔥 Novrintech Desktop Client - EXE Builder
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python first.
    echo Download from: https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Install PyInstaller
echo 📦 Installing PyInstaller...
pip install pyinstaller >nul 2>&1
echo ✅ PyInstaller installed
echo.

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist build rmdir /s /q build >nul 2>&1
if exist dist rmdir /s /q dist >nul 2>&1
if exist __pycache__ rmdir /s /q __pycache__ >nul 2>&1
if exist *.spec del /q *.spec >nul 2>&1
echo ✅ Cleanup complete
echo.

REM Build the EXE
echo 🔨 Building EXE...
echo This may take 2-5 minutes...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "NovrintechDesktop" ^
    --add-data ".env;." ^
    --hidden-import "plyer.platforms.win.notification" ^
    --hidden-import "requests.packages.urllib3" ^
    --hidden-import "dotenv" ^
    main.py

if errorlevel 1 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo.
echo ✅ Build successful!
echo.

REM Check if EXE was created
if exist "dist\NovrintechDesktop.exe" (
    echo 📁 EXE created: dist\NovrintechDesktop.exe
    
    REM Get file size
    for %%A in ("dist\NovrintechDesktop.exe") do (
        set size=%%~zA
        set /a sizeMB=!size!/1024/1024
    )
    
    echo 📊 File size: Approximately 20-30 MB
    echo.
    echo 🎉 SUCCESS!
    echo ==========================================
    echo Your EXE is ready at: dist\NovrintechDesktop.exe
    echo.
    echo 💡 Next steps:
    echo    1. Test the EXE by double-clicking it
    echo    2. Share the EXE file with users
    echo    3. No Python installation needed on target PCs
    echo.
) else (
    echo ❌ EXE file not found!
    echo Check for errors above.
)

pause