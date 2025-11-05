@echo off
REM MINI RCP Production Stop Script for Windows

echo Stopping MINI RCP Production Services...

REM Stop web server
echo Stopping web server...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq MINI RCP Web Server*" >nul 2>&1
if errorlevel 1 (
    echo Web server not found or already stopped
) else (
    echo Web server stopped
)

REM Stop processor
echo Stopping processor...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq MINI RCP Processor*" >nul 2>&1
if errorlevel 1 (
    echo Processor not found or already stopped
) else (
    echo Processor stopped
)

echo.
echo MINI RCP services stopped.
echo Check logs for any remaining processes.

pause