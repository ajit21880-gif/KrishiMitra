@echo off
echo Stopping KrishiMitra AI Services...

:: Stop Backend (find PID on port 8000 and kill it)
echo Stopping Backend on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process %%a
    taskkill /f /pid %%a >nul 2>&1
)

:: Stop Frontend (find PID on port 3001 and kill it)
echo Stopping Frontend on port 3001...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3001 ^| findstr LISTENING') do (
    echo Killing process %%a
    taskkill /f /pid %%a >nul 2>&1
)

echo All services stopped successfully.
pause
