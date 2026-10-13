@echo off
title NutriBot — Nutrition Agentic AI (IBM Granite LLM)
color 0A
cls

echo.
echo  =========================================================
echo    NutriBot — Nutrition Agentic AI
echo    Powered by IBM Granite LLM ^| watsonx.ai
echo  =========================================================
echo.

:: ── Navigate to script directory ─────────────────────────────
cd /d "%~dp0"

:: ── Check Python ─────────────────────────────────────────────
echo  [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python is not installed or not in PATH.
    echo  Please install Python 3.9+ from https://www.python.org/downloads/
    echo  Make sure to tick "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo  Found: %%i
echo.

:: ── Create virtual environment ────────────────────────────────
echo  [2/5] Setting up virtual environment...
if not exist "venv" (
    echo  Creating new virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo  ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  Virtual environment created.
) else (
    echo  Virtual environment already exists.
)
echo.

:: ── Activate virtual environment ──────────────────────────────
echo  [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo  ERROR: Could not activate virtual environment.
    pause
    exit /b 1
)
echo  Activated.
echo.

:: ── Install dependencies ───────────────────────────────────────
echo  [4/5] Installing dependencies (this may take a minute)...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo  ERROR: Failed to install dependencies.
    echo  Try running: pip install -r requirements.txt
    pause
    exit /b 1
)
echo  Dependencies installed.
echo.

:: ── Set up .env file ───────────────────────────────────────────
if not exist ".env" (
    echo  [INFO] No .env file found. Creating from .env.example...
    copy ".env.example" ".env" >nul
    echo.
    echo  ┌─────────────────────────────────────────────────────────┐
    echo  │  ACTION REQUIRED: Configure IBM watsonx.ai credentials  │
    echo  │                                                         │
    echo  │  Open the .env file in this folder and set:             │
    echo  │    WATSONX_API_KEY    = your IBM Cloud API key           │
    echo  │    WATSONX_PROJECT_ID = your watsonx project ID         │
    echo  │                                                         │
    echo  │  Without credentials, the app runs in DEMO MODE         │
    echo  │  (pre-built responses instead of live IBM Granite LLM)  │
    echo  └─────────────────────────────────────────────────────────┘
    echo.
) else (
    echo  [INFO] .env file already configured.
    echo.
)

:: ── Start Flask server ─────────────────────────────────────────
echo  [5/5] Starting NutriBot server...
echo.
echo  =========================================================
echo    Application URL : http://localhost:5000
echo    Press Ctrl+C to stop the server
echo  =========================================================
echo.

:: Open browser after 2 seconds
start "" /B cmd /C "timeout /t 2 /nobreak >nul && start http://localhost:5000"

:: Start Flask app
python app.py

echo.
echo  Server stopped.
pause
