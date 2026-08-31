@echo off
TITLE CAS 3:22 System Installer
COLOR 0A

:: Force working directory to project base directory
cd /d %~dp0

echo =======================================================================
echo          CAS 3:22 NIFTY + SENSEX AI SYSTEM - INSTALLER
echo =======================================================================
echo Base Directory: %CD%
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    COLOR 0C
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

if not exist "venv" (
    echo Creating local virtual environment in subfolder 'venv'...
    python -m venv venv
)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo Checking availability of required software libraries...
python -c "import streamlit, pandas, numpy, plotly, scipy, pytest" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] All required libraries are already installed! Skipping pip install.
) else (
    echo Installing missing dependencies from requirements.txt...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
)

echo Initializing database and local subfolders...
python -c "from src.db import init_db; init_db()"

echo.
echo Installation completed successfully! You can now run RUN.bat.
pause
