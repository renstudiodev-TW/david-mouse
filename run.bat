@echo off
REM HeadMouse Helper - launcher
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (
    py -3 -m src.main
) else (
    python -m src.main
)
