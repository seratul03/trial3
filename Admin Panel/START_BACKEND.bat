@echo off
title Backend Server - DO NOT CLOSE
cd /d "%~dp0"
echo ========================================
echo Starting Backend API Server...
echo ========================================
echo.
python run_backend.py
pause
