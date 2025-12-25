@echo off
echo ========================================
echo Novrintech Desktop Client v2.0 - AI Enhanced
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo Testing AI Integration...
python test_ai_integration.py
echo.

REM Install requirements if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing/updating requirements...
pip install -r requirements.txt

echo.
echo Features in this version:
echo - File Upload/Download/Management with User Tracking
echo - JSON Data Operations and Storage
echo - AI Assistant with Complete Application Knowledge
echo - Real-time Chat and Notifications System
echo - Keep-alive System for Server Health Monitoring
echo - Keyboard Shortcuts and Modern UI
echo.
echo Starting Enhanced Desktop Application...
python main.py

pause