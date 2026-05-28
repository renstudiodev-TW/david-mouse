@echo off
REM David Mouse - build and publish a GitHub Release.
REM
REM Flow:
REM   1. Calls build.bat to produce dist\david-mouse.zip.
REM   2. Asks for a version tag (e.g. v1.2.0).
REM   3. Uses gh CLI to create the Release and upload the zip.
REM
REM Requires: gh CLI authenticated (gh auth login), pyinstaller installed.

cd /d "%~dp0"

where gh >nul 2>&1
if errorlevel 1 (
    echo [ERROR] gh CLI not found.
    echo Install from: https://cli.github.com/
    exit /b 1
)

call build.bat
if errorlevel 1 (
    echo [ERROR] build.bat failed. Aborting release.
    exit /b 1
)

if not exist dist\david-mouse.zip (
    echo [ERROR] dist\david-mouse.zip is missing after build.
    exit /b 1
)

echo.
echo ========================================
echo   Create GitHub Release
echo ========================================
echo.
set /p TAG=Enter release tag (e.g. v1.2.0):
if "%TAG%"=="" (
    echo [ERROR] Tag is required.
    exit /b 1
)

set /p TITLE=Release title [%TAG%]:
if "%TITLE%"=="" set "TITLE=%TAG%"

echo.
echo Creating release %TAG%...
gh release create "%TAG%" "dist\david-mouse.zip" --title "%TITLE%" --generate-notes
set "RC=%errorlevel%"
if not "%RC%"=="0" (
    echo [ERROR] gh release create failed with exit code %RC%.
    exit /b %RC%
)

echo.
echo ========================================
echo   Release published.
echo   Download URL:
echo     https://github.com/renstudiodev-TW/david-mouse/releases/latest/download/david-mouse.zip
echo ========================================
echo.
