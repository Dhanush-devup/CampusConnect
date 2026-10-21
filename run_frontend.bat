@echo off
title CampusConnect Frontend (Port 5173)
cd /d "%~dp0frontend"
set PATH=C:\Program Files\nodejs;%PATH%
echo ===================================================
echo Starting CampusConnect React Frontend...
echo App URL: http://localhost:5173
echo ===================================================
npm.cmd run dev
pause
