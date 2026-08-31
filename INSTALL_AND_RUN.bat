@echo off
TITLE CAS 3:22 System - One-Click Installer and Launcher
COLOR 0A

:: Force working directory to project base directory
cd /d %~dp0

echo =======================================================================
echo          CAS 3:22 NIFTY + SENSEX AI SYSTEM - ONE-CLICK INSTALL AND RUN
echo =======================================================================
echo Canonical Production Path: C:\Mangesh\Jules\CAS
echo Base Directory: %CD%
echo.

:: Check for Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    COLOR 0C
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.9+ 64-bit and ensure "Add Python to PATH" is checked.
    pause
    exit /b 1
)

echo [1/4] Checking Python Virtual Environment in base subfolder 'venv'...
if not exist "venv" (
    echo Creating virtual environment 'venv' inside base folder...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [WARNING] Failed to create venv. Proceeding with system Python...
    )
)

if exist "venv\Scripts\activate.bat" (
    echo Activating local virtual environment...
    call venv\Scripts\activate.bat
)

echo [2/4] Checking availability of required software libraries...
python -c "import streamlit, pandas, numpy, plotly, scipy, pytest" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] All required libraries are already installed! Skipping pip install.
) else (
    echo [3/4] Installing missing dependencies from requirements.txt into local environment...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        COLOR 0C
        echo [ERROR] Dependency installation failed. Please check your internet connection.
        pause
        exit /b 1
    )
)

echo [4/4] Initializing Database and Logging subfolders...
python -c "from src.db import init_db; init_db()"

echo.
echo =======================================================================
echo              SUCCESS! Launching Streamlit Dashboard...
echo =======================================================================
echo.

streamlit run app/main.py

pause
