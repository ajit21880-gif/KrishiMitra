@echo off
title KrishiMitra WhatsApp Web Gateway Starter
echo ========================================================
echo   KrishiMitra WhatsApp Web Gateway Starter
echo ========================================================
echo.
cd /d "%~dp0whatsapp-gateway"
if not exist node_modules (
  echo Installing WhatsApp Web Gateway dependencies...
  npm install
)
echo Starting WhatsApp Gateway Service...
node index.js
pause
