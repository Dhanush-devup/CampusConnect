@echo off
title CampusConnect Backend (Port 8000)
cd /d "%~dp0backend"
echo ===================================================
echo Starting CampusConnect FastAPI Backend...
echo API Docs: http://127.0.0.1:8000/docs
echo ===================================================
.\venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
pause
