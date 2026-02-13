@echo off
REM Dynatrace Backup Manager - API Server
REM Starts the FastAPI backend server

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found. Run install.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo ========================================
echo Starting Dynatrace Backup Manager API
echo ========================================
echo.
echo API will be available at:
echo   http://127.0.0.1:8000
echo.
echo Documentation:
echo   http://127.0.0.1:8000/docs (Swagger UI)
echo   http://127.0.0.1:8000/redoc (ReDoc)
echo.

cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
