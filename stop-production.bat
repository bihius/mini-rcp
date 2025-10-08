@echo off
REM MINI RCP Production Stop Script for Windows

echo Stopping MINI RCP Production Services...

REM Function to stop service
:stop_service
set "name=%~1"
set "pid_file=%name%.pid"

if exist "%pid_file%" (
    for /f "tokens=*" %%i in (%pid_file%) do set "pid=%%i"
    echo Stopping %name% (PID: %pid%)...
    taskkill /PID %pid% /F >nul 2>&1
    if errorlevel 1 (
        echo Process %pid% not found or already stopped
    )
    del "%pid_file%" 2>nul
) else (
    echo %name% PID file not found
)

goto :eof

REM Stop services
call :stop_service "web-server"
call :stop_service "processor"

echo.
echo MINI RCP services stopped.
echo Check logs for any remaining processes.

pause