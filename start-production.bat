@echo off
REM MINI RCP Production Startup Script for Windows
REM This script starts both the web server and processor services

echo Starting MINI RCP Production Services...

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found. Please run 'uv sync' first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if Python is available in venv
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in virtual environment.
    pause
    exit /b 1
)

REM Start the web server in background
echo Starting web server...
start /B "MINI RCP Web Server" python -m app.web

REM Start the processor in background
echo Starting processor...
start /B "MINI RCP Processor" python -m app.processor

echo.
echo MINI RCP services started successfully!
echo Web server: http://localhost:5000
echo Check logs in logs\ folder for details