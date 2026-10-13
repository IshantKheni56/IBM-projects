@echo off
title NutriBot — Install Only
color 0B
cd /d "%~dp0"

echo.
echo  Installing NutriBot dependencies...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  Python not found. Install from https://www.python.org/downloads/
    pause & exit /b 1
)

if not exist "venv" python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo  Done! Run "run.bat" to start the application.
pause
