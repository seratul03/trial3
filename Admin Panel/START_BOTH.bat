@echo off
echo ========================================
echo College Chatbot Admin Panel
echo Starting Both Servers...
echo ========================================
echo.

REM Kill existing processes on ports 8000 and 3000
echo Cleaning up ports...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start backend in new window
echo Starting Backend Server...
start "Backend API - Port 8000" /MIN cmd /c "%~dp0START_BACKEND.bat"
timeout /t 5 /nobreak >nul

REM Start frontend in new window
echo Starting Frontend Server...
start "Frontend - Port 3000" /MIN cmd /c "%~dp0START_FRONTEND.bat"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Login: admin@college.edu / admin123
echo.
echo Two minimized windows will open.
echo DO NOT CLOSE THEM - they are running the servers!
echo.
timeout /t 3 /nobreak >nul
start http://localhost:3000
echo.
echo Opening browser...
echo.
pause
