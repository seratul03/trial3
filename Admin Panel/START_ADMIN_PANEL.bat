@echo off
title College Chatbot Admin Panel - Server Manager
color 0A

echo ======================================================================
echo Starting College Chatbot Admin Panel
echo ======================================================================
echo.

REM Kill any existing processes on ports 8000 and 3000
echo Cleaning up ports...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
timeout /t 2 >nul

REM Start backend in new window
echo Starting Backend Server...
start "Backend API - Port 8000" cmd /k "python run_backend.py"
timeout /t 6

REM Start frontend in new window
echo Starting Frontend Server...
start "Frontend - Port 3000" cmd /k "cd frontend && python -m http.server 3000"
timeout /t 3

echo.
echo ======================================================================
echo Both servers are starting!
echo ======================================================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Login: admin@college.edu / admin123
echo.
echo IMPORTANT: Keep the backend and frontend windows OPEN!
echo Close those windows to stop the servers.
echo ======================================================================
echo.
echo Opening browser...
timeout /t 2
start http://localhost:3000

echo.
echo Press any key to exit this window (servers will keep running)...
pause >nul
