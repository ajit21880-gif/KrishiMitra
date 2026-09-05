@echo off
title KrishiMitra WhatsApp Web Gateway Starter
echo ========================================================
echo   KrishiMitra WhatsApp Web Gateway Starter
echo ========================================================
echo.

:: 1. Check if Backend Python server is running on port 8000
netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Python Backend server is not running on port 8000.
    echo [INFO] Starting KrishiMitra Python Backend server automatically...
    start "KrishiMitra Python Backend Server" cmd /k "cd /d "%~dp0backend" && python app/main.py"
    echo [INFO] Waiting 4 seconds for Python Backend server to initialize...
    timeout /t 4 /nobreak >nul
) else (
    echo [OK] KrishiMitra Python Backend is active on port 8000.
)

:: 2. Launch Node WhatsApp Gateway
cd /d "%~dp0whatsapp-gateway"
if not exist node_modules (
  echo [INFO] Installing WhatsApp Web Gateway dependencies...
  npm install
)
echo [INFO] Starting WhatsApp Gateway Service...
node index.js
pause
