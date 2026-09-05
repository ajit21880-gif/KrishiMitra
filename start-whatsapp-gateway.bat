@echo off
title KrishiMitra WhatsApp Web Gateway Starter
echo ========================================================
echo   KrishiMitra AI WhatsApp Gateway & Backend Starter
echo ========================================================
echo.

:: 1. Check if Python Backend server is running on port 8000
netstat -aon | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Python Backend server is NOT running on port 8000.
    echo [INFO] Auto-starting KrishiMitra Python Backend server...
    start "KrishiMitra Python Backend (Port 8000)" cmd /k "cd /d "%~dp0backend" && set DATAGOV_API_KEY=579b464db66ec23bdd000001a40e8a53305b4bcb40409d2efb7d48dc && python app/main.py"
    echo [INFO] Waiting 5 seconds for Python Backend to initialize on http://localhost:8000...
    timeout /t 5 /nobreak >nul
) else (
    echo [OK] KrishiMitra Python Backend is active and running on port 8000.
)

echo.
:: 2. Launch Node WhatsApp Gateway
cd /d "%~dp0whatsapp-gateway"
if not exist node_modules (
  echo [INFO] Installing WhatsApp Web Gateway dependencies...
  npm install
)
echo [INFO] Starting WhatsApp Gateway Service...
node index.js
pause
