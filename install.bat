@echo off
REM HeadMouse Helper - one-click installer
REM Detects Python 3.10+; if missing/too old, installs Python 3.12 automatically
REM via winget, falling back to the official python.org installer.
REM
REM Notes:
REM  * `chcp 65001` switches the console to UTF-8 before we expand any %VAR%
REM    that may contain non-ASCII characters (e.g. Chinese username in %TEMP%
REM    or %LOCALAPPDATA%). On legacy code pages (Big5/cp950 etc.) certain
REM    multi-byte trail bytes collide with cmd special chars (^, |, \) and
REM    break parenthesized blocks.
REM  * Flow uses `goto` instead of nested parens-blocks for the same reason:
REM    inside a parens-block, %VAR% is expanded at parse time and a non-ASCII
REM    value can wreck the block's bracket matching.
chcp 65001 >nul
cd /d "%~dp0"
title HeadMouse Helper - Install

echo ========================================
echo   HeadMouse Helper - Install
echo ========================================
echo.

call :find_python
if defined PY_CMD goto :install_deps

echo Python 3.10+ was not found on this PC.
echo This installer can download and install Python 3.12 for you.
echo No admin rights needed -- it installs into your user profile.
echo.
choice /c YN /d Y /t 15 /n /m "Install Python automatically? [Y/n, auto-Y in 15s] "
if errorlevel 2 goto :cancelled
echo.

REM --- Attempt 1: winget ---
where winget >nul 2>&1
if errorlevel 1 goto :try_download
echo Installing Python 3.12 via winget. This may take a few minutes...
winget install -e --id Python.Python.3.12 --scope user --silent --accept-source-agreements --accept-package-agreements
call :refresh_path
call :find_python
if defined PY_CMD goto :install_deps

:try_download
REM --- Attempt 2: download official installer from python.org ---
echo.
echo Falling back to direct download from python.org...
set "PY_URL=https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
set "PY_INSTALLER=%TEMP%\headmouse-python-3.12.7-amd64.exe"
echo Downloading: %PY_URL%
powershell -NoProfile -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing -Uri '%PY_URL%' -OutFile '%PY_INSTALLER%' } catch { Write-Host $_.Exception.Message; exit 1 }"
if errorlevel 1 goto :download_failed
echo Running Python installer (silent, per-user, with PATH + py launcher)...
"%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_pip=1 Include_tcltk=1
set "PY_RC=%errorlevel%"
del "%PY_INSTALLER%" >nul 2>&1
if not "%PY_RC%"=="0" goto :installer_failed
call :refresh_path
call :find_python
if defined PY_CMD goto :install_deps

REM --- Attempt 3: probe the well-known per-user install path directly ---
set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PY_EXE%" goto :not_found_after_install
"%PY_EXE%" --version >nul 2>&1
if errorlevel 1 goto :not_found_after_install
set PY_CMD="%PY_EXE%"
goto :install_deps

:install_deps
echo.
echo Using Python: %PY_CMD%
%PY_CMD% --version
echo.
echo Upgrading pip...
%PY_CMD% -m pip install --upgrade pip
echo.
echo Installing dependencies from requirements.txt...
echo.
%PY_CMD% -m pip install -r requirements.txt
set "RC=%errorlevel%"
echo.
if not "%RC%"=="0" goto :pip_failed
echo ========================================
echo   Install OK. You can now run run.bat.
echo ========================================
echo.
pause
exit /b 0

:pip_failed
echo ========================================
echo   Install FAILED with exit code %RC%.
echo   See the pip error above.
echo ========================================
echo.
pause
exit /b %RC%

:cancelled
echo.
echo Cancelled. Install Python 3.10+ manually from:
echo   https://www.python.org/downloads/windows/
echo Then run install.bat again.
pause
exit /b 1

:download_failed
echo.
echo [ERROR] Could not download Python installer.
echo Check your internet connection, or install manually from:
echo   https://www.python.org/downloads/windows/
pause
exit /b 1

:installer_failed
echo.
echo [ERROR] Python installer failed with exit code %PY_RC%.
echo Please install manually: https://www.python.org/downloads/windows/
pause
exit /b 1

:not_found_after_install
echo.
echo [ERROR] Python install seemed to succeed but interpreter is still not found.
echo Please close this window, open a NEW command prompt, and run install.bat again.
pause
exit /b 1


REM ----- subroutines -----

REM Set PY_CMD to a working Python 3.10+ launcher/interpreter, or leave empty.
:find_python
set "PY_CMD="
where py >nul 2>&1 && py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1 && set "PY_CMD=py -3"
if defined PY_CMD exit /b 0
where python >nul 2>&1 && python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1 && set "PY_CMD=python"
exit /b 0

:refresh_path
for /f "usebackq tokens=*" %%P in (`powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [Environment]::GetEnvironmentVariable('PATH','User')"`) do set "PATH=%%P"
exit /b 0
