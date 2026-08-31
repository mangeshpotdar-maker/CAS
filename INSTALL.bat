@echo off
TITLE CAS 3:22 System Installer
COLOR 0A

echo =======================================================================
echo          CAS 3:22 NIFTY + SENSEX AI SYSTEM - INSTALLER
echo =======================================================================
cd /d %~dp0

python --version >nul 2>&1
if %errorlevel% neq 0 (
    COLOR 0C
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo Initializing database...
python -c "from src.db import init_db; init_db()"

echo.
echo Installation completed successfully! You can now run RUN.bat.
pause
