@echo off
REM David Mouse - remove the "start at logon as Administrator" scheduled task.
REM Self-elevates, then hands off to tools\admin-autostart.ps1 -Action uninstall.
REM ASCII only on purpose: cmd.exe code pages mangle non-ASCII batch files.

setlocal
cd /d "%~dp0"
title David Mouse - Remove admin autostart

net session >nul 2>&1
if not errorlevel 1 goto :elevated

echo Requesting administrator rights...
powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
exit /b 0

:elevated
echo ========================================
echo   David Mouse - Remove admin autostart
echo ========================================
echo.

set "PS1=%~dp0tools\admin-autostart.ps1"
if not exist "%PS1%" set "PS1=%~dp0admin-autostart.ps1"
if not exist "%PS1%" goto :no_script

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -Action uninstall
set "RC=%errorlevel%"
echo.
if not "%RC%"=="0" goto :failed

echo Done.
echo.
pause
exit /b 0

:no_script
echo [ERROR] admin-autostart.ps1 not found next to this file or in tools\.
echo.
pause
exit /b 1

:failed
echo [ERROR] Remove failed with exit code %RC%. See the message above.
echo.
pause
exit /b %RC%
