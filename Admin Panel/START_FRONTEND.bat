@echo off
title Frontend Server - DO NOT CLOSE
cd /d "%~dp0\frontend"
echo ========================================
echo Starting Frontend Server...
echo ========================================
echo.
python -m http.server 3000
pause
