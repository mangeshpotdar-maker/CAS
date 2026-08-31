@echo off
TITLE CAS 3:22 System Dashboard Launcher
COLOR 0B

echo =======================================================================
echo          CAS 3:22 NIFTY + SENSEX AI SYSTEM - LAUNCHER
echo =======================================================================
cd /d %~dp0

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

streamlit run app/main.py
pause
