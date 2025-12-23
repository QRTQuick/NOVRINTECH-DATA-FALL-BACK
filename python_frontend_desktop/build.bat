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
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building executable...
echo.

REM Build the EXE
pyinstaller --onefile --windowed --name "Novrintech-Desktop" --add-data ".env;." --hidden-import=tkinter --hidden-import=requests --hidden-import=dotenv --hidden-import=hashlib --hidden-import=json --hidden-import=threading main.py

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Your EXE is located at:
echo dist\Novrintech-Desktop.exe
echo.
echo File size: 
dir dist\Novrintech-Desktop.exe | find "Novrintech-Desktop.exe"
echo.
pause
