@echo off
REM Dynatrace Backup Manager - Windows Launcher
REM This script starts the application with the GUI interface
REM Monaco CLI is included in the application

setlocal enabledelayedexpansion

REM Get the script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo Installing Python environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Check if Monaco CLI exists
if not exist "bin\monaco.exe" (
    echo.
    echo ERROR: Monaco CLI not found at bin\monaco.exe
    echo The application requires Monaco CLI to function.
    echo.
    pause
    exit /b 1
)

REM Start the application
echo Starting Dynatrace Backup Manager...
python main.py --mode gui

pause

