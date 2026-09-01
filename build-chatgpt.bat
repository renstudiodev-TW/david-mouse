@echo off
REM David Mouse - build the "ChatGPT dictation" variant zip.
REM
REM This does NOT touch dist\david-mouse.exe / dist\david-mouse.zip (the
REM regular build). It produces a separately named exe/zip so the existing
REM GitHub Release asset (david-mouse.zip) is never overwritten.
REM
REM Output:
REM   dist\david-mouse-chatgpt.exe
REM   dist\david-mouse-chatgpt.zip   - upload as an EXTRA asset on the
REM                                    existing release (gh release upload),
REM                                    do not replace david-mouse.zip.
REM
REM Requires: pyinstaller, powershell (for zip).

cd /d "%~dp0"

where pyinstaller >nul 2>&1
if not %errorlevel%==0 (
    echo [ERROR] PyInstaller not found. Install with:
    echo   pip install pyinstaller
    exit /b 1
)

echo ========================================
echo   Building david-mouse-chatgpt.exe
echo ========================================
echo.

pyinstaller --onefile --noconsole --name david-mouse-chatgpt ^
    --hidden-import=pynput --hidden-import=win32com.client --hidden-import=pythoncom ^
    src\main.py
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    exit /b 1
)

if not exist dist\david-mouse-chatgpt.exe (
    echo [ERROR] Expected dist\david-mouse-chatgpt.exe was not produced.
    exit /b 1
)

echo.
echo ========================================
echo   Packaging dist\david-mouse-chatgpt.zip
echo ========================================
echo.

copy /Y release-notes\README-chatgpt.txt dist\README.txt >nul
if errorlevel 1 (
    echo [WARN] release-notes\README-chatgpt.txt missing - zip will not include it.
)

copy /Y setup-admin-autostart.bat dist\setup-admin-autostart.bat >nul
copy /Y remove-admin-autostart.bat dist\remove-admin-autostart.bat >nul
copy /Y tools\admin-autostart.ps1 dist\admin-autostart.ps1 >nul
if errorlevel 1 (
    echo [WARN] admin autostart scripts missing - zip will not include them.
)

powershell -NoProfile -Command "Compress-Archive -Force -Path 'dist\david-mouse-chatgpt.exe','dist\README.txt','dist\setup-admin-autostart.bat','dist\remove-admin-autostart.bat','dist\admin-autostart.ps1' -DestinationPath 'dist\david-mouse-chatgpt.zip'"
if errorlevel 1 (
    echo [ERROR] Failed to create dist\david-mouse-chatgpt.zip.
    exit /b 1
)

echo.
echo ========================================
echo   Build OK.
echo   - dist\david-mouse-chatgpt.exe
echo   - dist\david-mouse-chatgpt.zip   (upload as an EXTRA asset, do not
echo     replace david-mouse.zip)
echo ========================================
echo.
