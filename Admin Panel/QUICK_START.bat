@echo off
REM Quick restart - kills everything and starts fresh
title Admin Panel Quick Start

REM Kill all Python processes
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

REM Start backend
start "BACKEND - DO NOT CLOSE" cmd /k "color 0A && echo Backend Server Running on Port 8000 && python run_backend.py"
timeout /t 6

REM Start frontend  
start "FRONTEND - DO NOT CLOSE" cmd /k "color 0B && echo Frontend Server Running on Port 3000 && cd frontend && python -m http.server 3000"
timeout /t 3

REM Open browser
start http://localhost:3000

echo.
echo SERVERS ARE RUNNING!
echo.
echo Two windows opened:
echo   - BACKEND
echo   - FRONTEND
echo.
echo Login at: http://localhost:3000
echo Email: admin@college.edu
echo Password: admin123
echo.
echo Press any key to close this window...
pause >nul
