@echo off
title Earth Trend Explorer - Services Runner
echo ========================================================
echo   Starting Earth Trend Explorer (Africa) Services
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/2] Launching Python FastAPI Microservice on port 8001...
start "FastAPI Microservice (Port 8001)" cmd /k "cd data-analysis-statistics && .venv313\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8001 --reload"

echo [2/2] Launching Laravel Web Server on port 8000...
start "Laravel Server (Port 8000)" cmd /k "cd nasa-laravel && php artisan serve --port 8000"

echo.
echo ========================================================
echo   All services launched!
echo   Dashboard URL: http://127.0.0.1:8000/dashboard
echo   Landing Page:  http://127.0.0.1:8000/
echo ========================================================
echo.
timeout /t 3 >nul
start http://127.0.0.1:8000/dashboard
