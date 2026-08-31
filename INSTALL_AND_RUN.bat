@echo off
TITLE CAS 3:22 System - One-Click Installer & Launcher
COLOR 0A

echo =======================================================================
echo          CAS 3:22 NIFTY + SENSEX AI SYSTEM - ONE-CLICK INSTALL & RUN
echo =======================================================================
echo Canonical Production Path: C:\Mangesh\Jules\CAS
echo.

cd /d %~dp0

:: Check for Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    COLOR 0C
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.9+ 64-bit and ensure "Add Python to PATH" is checked.
    pause
    exit /b 1
)

echo [1/4] Checking Python Virtual Environment...
if not exist "venv" (
    echo [2/4] Creating virtual environment 'venv'...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [WARNING] Failed to create venv. Proceeding with system Python...
    )
)

if exist "venv\Scripts\activate.bat" (
    echo [2/4] Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo [3/4] Installing / Updating dependencies from requirements.txt...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    COLOR 0C
    echo [ERROR] Dependency installation failed. Please check your internet connection.
    pause
    exit /b 1
)

echo [4/4] Initializing Database & Logging...
python -c "from src.db import init_db; init_db()"

echo.
echo =======================================================================
echo              SUCCESS! Launching Streamlit Dashboard...
echo =======================================================================
echo.

streamlit run app/main.py

pause
