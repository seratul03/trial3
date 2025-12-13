# Troubleshooting Guide - Network Connection Issues

## Problem: Login Page Shows "Network Error" or "Cannot Connect"

### Root Cause
The backend FastAPI server is not running on port 8000. Instead, a simple HTTP server is serving static files, which causes the login API calls to fail with 404 errors.

### Solution

#### Option 1: Use the New Improved Startup Script (Recommended)

1. **Stop all running servers:**
   ```powershell
   Get-Process python | Stop-Process -Force
   ```

2. **Start servers using the improved script:**
   ```powershell
   python start_servers.py
   ```

3. **Wait for the message:** "✅ Both servers are running!"

4. **Open browser and login:**
   - URL: http://localhost:3000
   - Email: admin@college.edu
   - Password: admin123

#### Option 2: Manual Server Start

1. **Stop all Python processes:**
   ```powershell
   Get-Process python | Stop-Process -Force
   ```

2. **Open TWO separate PowerShell/CMD windows**

3. **In Terminal 1 - Start Backend:**
   ```powershell
   cd "C:\Users\Seratul Mustakim\Downloads\College_chatbot\College_chatbot\Admin Panel"
   python run_backend.py
   ```
   - Wait for: "Uvicorn running on http://0.0.0.0:8000"
   - **Keep this window OPEN!**

4. **In Terminal 2 - Start Frontend:**
   ```powershell
   cd "C:\Users\Seratul Mustakim\Downloads\College_chatbot\College_chatbot\Admin Panel\frontend"
   python -m http.server 3000
   ```
   - Wait for: "Serving HTTP on :: port 3000"
   - **Keep this window OPEN!**

5. **Open browser:** http://localhost:3000

---

## How to Verify Everything is Working

### Check Port Status
```powershell
# Check if port 8000 is listening
Test-NetConnection -ComputerName localhost -Port 8000

# Check if port 3000 is listening  
Test-NetConnection -ComputerName localhost -Port 3000
```

### Test Backend API
```powershell
# Should return JSON with "message" field
curl http://localhost:8000/

# Should show FastAPI documentation
curl http://localhost:8000/docs
```

### Test Frontend
```powershell
# Should return HTML starting with <!DOCTYPE html>
curl http://localhost:3000/
```

---

## Common Issues

### Issue 1: "Port already in use"
**Solution:** Kill the process using the port
```powershell
# For port 8000
FOR /F "tokens=5" %P IN ('netstat -ano ^| findstr :8000') DO TaskKill /F /PID %P

# For port 3000
FOR /F "tokens=5" %P IN ('netstat -ano ^| findstr :3000') DO TaskKill /F /PID %P
```

### Issue 2: Backend returns HTML instead of JSON
**Problem:** Wrong server is running on port 8000

**Solution:**
1. Stop all Python processes
2. Start `run_backend.py` first
3. Verify with: `curl http://localhost:8000/` - should return JSON

### Issue 3: Login shows "Network error"
**Cause:** Backend API not accessible

**Debug steps:**
1. Open browser console (F12)
2. Try to login
3. Check Network tab for failed requests
4. If you see 404 errors to `/api/auth/login`, backend is not running

**Solution:** Restart backend server properly

---

## Files Explained

- **start_servers.py** - New improved startup script (USE THIS!)
- **start.py** - Old startup script (has issues with console windows)
- **run_backend.py** - Starts only the FastAPI backend
- **check_servers.py** - Diagnostic tool to check server status

---

## Quick Fix Commands

```powershell
# Stop everything
Get-Process python | Stop-Process -Force

# Start fresh
python start_servers.py

# If that doesn't work, manual approach:
# Terminal 1:
python run_backend.py

# Terminal 2 (in new window):
cd frontend
python -m http.server 3000
```

---

## What Should You See When Everything Works?

### Backend Terminal (port 8000):
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Frontend Terminal (port 3000):
```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

### Browser (http://localhost:3000):
- Should show login page
- No console errors (F12 → Console tab)
- Login with `admin@college.edu` / `admin123` should work
- After login, should redirect to dashboard

---

## Still Having Issues?

1. Check firewall settings (allow Python on ports 8000 and 3000)
2. Try different ports if 8000/3000 are blocked
3. Check if antivirus is blocking connections
4. Restart your computer and try again

