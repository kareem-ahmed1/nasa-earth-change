@echo off
title NASA Africa Climate Explorer
cd /d "%~dp0"

echo ========================================================
echo    Starting NASA Africa Climate Analysis Application
echo ========================================================
echo.

REM 1. Start the backend API server in the background
start "Climate API Backend" /b .\.venv313\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000

REM 2. Wait a moment for the server to initialize
echo Initializing server, please wait...
timeout /t 2 /nobreak >nul

REM 3. Automatically open the frontend in the default browser
echo Opening frontend in your browser...
start "" "frontend\index.html"

echo.
echo Application is running!
echo - API Server: http://127.0.0.1:8000
echo - Swagger Docs: http://127.0.0.1:8000/docs
echo.
echo To stop the application, close this window.
echo ========================================================
pause
