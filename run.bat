@echo off
REM David Mouse - launcher
REM See install.bat for why we chcp 65001 and avoid parens-blocks containing
REM %VAR% expansions that may include non-ASCII characters.
chcp 65001 >nul
cd /d "%~dp0"

call :find_python
if defined PY_CMD goto :run

REM Fallback: probe the well-known per-user Python 3.12 path.
set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PY_EXE%" goto :no_python
"%PY_EXE%" --version >nul 2>&1
if errorlevel 1 goto :no_python
set PY_CMD="%PY_EXE%"

:run
%PY_CMD% -m src.main
set "RC=%errorlevel%"
if not "%RC%"=="0" goto :err
exit /b 0

:err
echo.
echo App exited with error code %RC%.
pause
exit /b %RC%

:no_python
echo [ERROR] Python 3.10+ is not installed.
echo Please run install.bat first -- it will install Python automatically.
echo.
pause
exit /b 1


REM ----- subroutines -----

:find_python
set "PY_CMD="
where py >nul 2>&1 && py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1 && set "PY_CMD=py -3"
if defined PY_CMD exit /b 0
where python >nul 2>&1 && python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1 && set "PY_CMD=python"
exit /b 0
