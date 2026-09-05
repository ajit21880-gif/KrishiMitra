@echo off
title Stop KrishiMitra WhatsApp Gateway & Services
echo ========================================================
echo   Stopping KrishiMitra WhatsApp Gateway & Services
echo ========================================================
echo.

:: 1. Stop Python Backend on port 8000
echo [INFO] Stopping Python Backend on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing Python process PID %%a...
    taskkill /f /pid %%a >nul 2>&1
)

:: 2. Stop Node WhatsApp Gateway processes
echo [INFO] Stopping WhatsApp Gateway Node processes...
taskkill /fi "WINDOWTITLE eq KrishiMitra WhatsApp Web Gateway Starter*" /f >nul 2>&1

echo.
echo [OK] All WhatsApp Gateway services stopped successfully.
pause
