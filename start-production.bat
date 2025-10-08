@echo off
REM MINI RCP Production Startup Script for Windows
REM This script starts both the web server and processor services

echo Starting MINI RCP Production Services...

REM Check if uv is available
uv --version >nul 2>&1
if errorlevel 1 (
    echo Error: uv is not installed. Please install uv first.
    echo Visit: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

REM Start the web server in background
echo Starting web server...
start "MINI RCP Web Server" uv run python -m app.web

REM Start the processor in background
echo Starting processor...
start "MINI RCP Processor" uv run python -m app.processor

echo.
echo MINI RCP services started successfully!
echo Web server: http://localhost:5000
echo Check logs in logs\ folder for details
echo.
echo Press any key to exit (services will continue running)...
pause > nul