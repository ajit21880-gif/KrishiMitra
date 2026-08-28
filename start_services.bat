@echo off
echo Starting KrishiMitra AI Services...

:: Start Backend Flask App in the background
echo Starting Backend on port 8000...
start /b "" cmd /c "cd /d "%~dp0backend" && set DATAGOV_API_KEY=579b464db66ec23bdd000001a40e8a53305b4bcb40409d2efb7d48dc&& .venv\Scripts\python.exe app\main.py" > nul 2>&1

:: Start Frontend Next.js Dev Server in the background
echo Starting Frontend on port 3001...
start /b "" cmd /c "cd /d "%~dp0frontend" && npm.cmd run dev" > nul 2>&1

:: Wait for services to start up (5 seconds)
echo Waiting for services to initialize...
timeout /t 5 /nobreak > nul

:: Launch the app URL in default browser
echo Launching browser...
start http://localhost:3001

echo Done! Closing command window.
exit
