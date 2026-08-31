@echo off
TITLE CAS 3:22 System Dashboard Launcher
COLOR 0B

:: Force working directory to project base directory
cd /d %~dp0

echo =======================================================================
echo          CAS 3:22 NIFTY + SENSEX AI SYSTEM - LAUNCHER
echo =======================================================================
echo Base Directory: %CD%
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

streamlit run app/main.py
pause
