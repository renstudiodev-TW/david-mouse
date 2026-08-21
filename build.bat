@echo off
REM David Mouse - build single-file exe and package a release zip.
REM
REM Output:
REM   dist\david-mouse.exe                  - portable single-file binary
REM   dist\david-mouse.zip                  - release-ready archive
REM       contains: david-mouse.exe, README.txt
REM
REM Requires: pyinstaller, powershell (for zip).
REM Run install.bat first to install Python deps.

cd /d "%~dp0"

where pyinstaller >nul 2>&1
if not %errorlevel%==0 (
    echo [ERROR] PyInstaller not found. Install with:
    echo   pip install pyinstaller
    exit /b 1
)

echo ========================================
echo   Building david-mouse.exe
echo ========================================
echo.

REM Clean previous build artifacts so the zip never carries stale files.
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

pyinstaller --onefile --noconsole --name david-mouse ^
    --hidden-import=pynput --hidden-import=win32com.client --hidden-import=pythoncom ^
    src\main.py
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    exit /b 1
)

if not exist dist\david-mouse.exe (
    echo [ERROR] Expected dist\david-mouse.exe was not produced.
    exit /b 1
)

echo.
echo ========================================
echo   Packaging dist\david-mouse.zip
echo ========================================
echo.

REM Drop a short readme into dist before zipping. End users unzip and double-click.
copy /Y release-notes\README.txt dist\README.txt >nul
if errorlevel 1 (
    echo [WARN] release-notes\README.txt missing - zip will not include it.
)

REM Admin-autostart helper scripts ship next to the exe. The .ps1 sits beside
REM the .bat in the zip (the .bat looks for it in tools\ first, then alongside).
copy /Y setup-admin-autostart.bat dist\setup-admin-autostart.bat >nul
copy /Y remove-admin-autostart.bat dist\remove-admin-autostart.bat >nul
copy /Y tools\admin-autostart.ps1 dist\admin-autostart.ps1 >nul
if errorlevel 1 (
    echo [WARN] admin autostart scripts missing - zip will not include them.
)

REM Use PowerShell Compress-Archive for a portable, dependency-free zip.
powershell -NoProfile -Command "Compress-Archive -Force -Path 'dist\david-mouse.exe','dist\README.txt','dist\setup-admin-autostart.bat','dist\remove-admin-autostart.bat','dist\admin-autostart.ps1' -DestinationPath 'dist\david-mouse.zip'"
if errorlevel 1 (
    echo [ERROR] Failed to create dist\david-mouse.zip.
    exit /b 1
)

echo.
echo ========================================
echo   Build OK.
echo   - dist\david-mouse.exe
echo   - dist\david-mouse.zip   (upload this to GitHub Releases)
echo ========================================
echo.
