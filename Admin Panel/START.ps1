# Simple and Reliable Server Starter
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SIMPLE SERVER STARTER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill Python processes
Write-Host "[1/4] Stopping all Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start Backend
Write-Host "[2/4] Starting Backend on port 8000..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Minimized
Start-Sleep -Seconds 6

# Test Backend
Write-Host "[3/4] Testing backend..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/" -TimeoutSec 5
    if ($response.message -like "*Admin Panel*") {
        Write-Host "   SUCCESS: Backend API is running!" -ForegroundColor Green
    } else {
        Write-Host "   WARNING: Port 8000 responding but not with API!" -ForegroundColor Red
        Write-Host "   Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ERROR: Backend not responding!" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
}

# Start Frontend
Write-Host "[4/4] Starting Frontend on port 3000..." -ForegroundColor Yellow
$frontendPath = Join-Path $PSScriptRoot "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; python -m http.server 3000" -WindowStyle Minimized
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "SERVERS STARTED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Login: admin@college.edu / admin123" -ForegroundColor Cyan
Write-Host ""
Write-Host "Two PowerShell windows opened (minimized)." -ForegroundColor Yellow
Write-Host "DO NOT CLOSE THEM!" -ForegroundColor Red
Write-Host ""

Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"

Write-Host "Opening browser..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to close this window (servers will keep running)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
