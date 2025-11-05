@echo off
REM MINI RCP Production Stop Script for Windows

echo Stopping MINI RCP Production Services...

REM Stop all Python processes (web server and processor)
echo Stopping Python processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1

REM Check if any Python processes are still running
tasklist /FI "IMAGENAME eq python.exe" /NH >nul 2>&1
if errorlevel 1 (
    echo All Python processes stopped successfully
) else (
    echo Warning: Some Python processes may still be running
    tasklist /FI "IMAGENAME eq python.exe" /NH
)

echo.
echo MINI RCP services stopped.
echo Check Task Manager to confirm processes are terminated.

pause