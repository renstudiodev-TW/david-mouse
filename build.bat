@echo off
REM David Mouse - build single-file exe with PyInstaller
cd /d "%~dp0"
where pyinstaller >nul 2>&1
if not %errorlevel%==0 (
    echo PyInstaller not found. Install with: pip install pyinstaller
    exit /b 1
)
pyinstaller --onefile --noconsole --name david-mouse --hidden-import=pynput --hidden-import=win32com.client --hidden-import=pythoncom src\main.py
