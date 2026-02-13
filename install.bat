@echo off
REM Dynatrace Backup Manager - Installation script
REM Monaco CLI est déjà inclus dans l'application

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo ========================================
echo Dynatrace Backup Manager - Installation
echo ========================================
echo.

REM Check Python
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)
echo OK - Python found

REM Create virtual environment
echo [2/4] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo OK - Virtual environment created
)

REM Activate venv
echo [3/4] Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo OK - Dependencies installed

REM Create directories
echo [4/4] Creating directories and configuration...
if not exist "backups" mkdir backups
if not exist "config" mkdir config
echo OK - Directories created

REM Verify Monaco CLI
if exist "bin\monaco.exe" (
    echo OK - Monaco CLI found (bin\monaco.exe)
) else (
    echo WARNING: Monaco CLI not found in bin\monaco.exe
    echo The application won't work without it.
)

REM Copy .env
if not exist ".env" (
    copy .env.example .env >nul 2>&1
    echo OK - Configuration file created (.env)
    echo IMPORTANT: Edit .env with your Dynatrace settings before running the app
) else (
    echo OK - Configuration file already exists
)

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env with your Dynatrace environment URL and API token
echo 2. Run: start.bat (to launch the GUI application)
echo.
pause

