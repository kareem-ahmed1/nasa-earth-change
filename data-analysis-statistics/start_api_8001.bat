@echo off
title NASA Africa Climate Analysis API (Port 8001)
cd /d "%~dp0"

echo ========================================================
echo    Starting NASA Africa Climate Analysis Microservice
echo    Host: 127.0.0.1  Port: 8001
echo ========================================================

.\.venv313\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8001
