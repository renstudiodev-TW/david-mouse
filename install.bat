@echo off
REM HeadMouse Helper - install Python dependencies
cd /d "%~dp0"
echo Installing HeadMouse Helper dependencies...
echo.
where py >nul 2>&1
if %errorlevel%==0 (
    py -3 -m pip install -r requirements.txt
) else (
    python -m pip install -r requirements.txt
)
echo.
if %errorlevel%==0 (
    echo Install OK.
) else (
    echo Install FAILED. See the error above.
)
echo.
pause
