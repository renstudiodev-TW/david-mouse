@echo off
REM David Mouse - enable "start at logon as Administrator"
REM
REM The Windows Startup folder cannot launch an elevated program: a shortcut
REM with "Run as administrator" checked is silently blocked by UAC. The only
REM reliable way is a Scheduled Task with RunLevel=Highest triggered at logon,
REM which also skips the UAC prompt.
REM
REM This script self-elevates, then hands off to tools\admin-autostart.ps1.
REM ASCII only on purpose: cmd.exe code pages mangle non-ASCII batch files.

setlocal
cd /d "%~dp0"
title David Mouse - Setup admin autostart

net session >nul 2>&1
if not errorlevel 1 goto :elevated

echo Requesting administrator rights...
powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
exit /b 0

:elevated
echo ========================================
echo   David Mouse - Admin autostart setup
echo ========================================
echo.

set "PS1=%~dp0tools\admin-autostart.ps1"
if not exist "%PS1%" set "PS1=%~dp0admin-autostart.ps1"
if not exist "%PS1%" goto :no_script

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -Action install -BaseDir "%~dp0."
set "RC=%errorlevel%"
echo.
if not "%RC%"=="0" goto :failed

echo Done. Restart Windows to verify.
echo To undo, run remove-admin-autostart.bat
echo.
pause
exit /b 0

:no_script
echo [ERROR] admin-autostart.ps1 not found next to this file or in tools\.
echo.
pause
exit /b 1

:failed
echo [ERROR] Setup failed with exit code %RC%. See the message above.
echo.
pause
exit /b %RC%
