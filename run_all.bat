@echo off
title CampusConnect Launcher
echo Starting CampusConnect Full Stack Application...
start "CampusConnect Backend" cmd /c "%~dp0run_backend.bat"
timeout /t 2 >nul
start "CampusConnect Frontend" cmd /c "%~dp0run_frontend.bat"
timeout /t 3 >nul
echo Opening application in browser...
start http://localhost:5173
echo CampusConnect is running!
