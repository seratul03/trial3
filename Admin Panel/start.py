"""
Single file to start both backend and frontend servers
Just run: python start.py
"""
import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def main():
    root_dir = Path(__file__).parent
    backend_dir = root_dir / "backend"
    frontend_dir = root_dir / "frontend"
    
    print("=" * 60)
    print("🚀 Starting College Chatbot Admin Panel")
    print("=" * 60)
    
    # Kill any existing process on port 3000
    print("\n🧹 Cleaning up existing processes...")
    if sys.platform == "win32":
        subprocess.run("FOR /F \"tokens=5\" %P IN ('netstat -ano ^| findstr :3000') DO TaskKill /F /PID %P", shell=True, capture_output=True)
        time.sleep(1)

    print("\n🖡 Starting Backend Server (FastAPI, serves frontend too)...")
    backend_cmd = [sys.executable, "run_backend.py"]
    # Start backend without piping output (avoids PIPE buffer blocking)
    env = os.environ.copy()
    # Disable uvicorn auto-reload for faster startup when launched via this script
    env.setdefault("RELOAD", "0")

    backend_process = subprocess.Popen(
        backend_cmd,
        cwd=str(root_dir),
        env=env,
        stdout=None,
        stderr=None,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )

    # Wait for backend to become healthy (poll /health)
    print("   Waiting for backend to initialize...")
    import urllib.request
    health_url = "http://127.0.0.1:3000/health"
    start_time = time.time()
    timeout = 20  # seconds
    while True:
        try:
            with urllib.request.urlopen(health_url, timeout=2) as r:
                if r.status == 200:
                    print("   Backend healthy")
                    break
        except Exception:
            pass
        if time.time() - start_time > timeout:
            print("   Warning: backend did not become healthy within timeout")
            break
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("✅ Admin Panel is running!")
    print("=" * 60)
    print("\n📍 URLs:")
    print("   Admin Panel: http://localhost:3000")
    print("   API Docs:   http://localhost:3000/docs")
    print("\n🔑 Login Credentials:")
    print("   Admin:   admin@college.edu / admin123")
    print("\n" + "=" * 60)
    print("⚠️  Press Ctrl+C here to stop the server")
    print("=" * 60)

    # Open browser
    print("\n🌍 Opening browser...")
    time.sleep(1)
    webbrowser.open("http://localhost:3000")

    try:
        print("\n✨ Application is running in http://localhost:3000 ! Close this window to stop the server.\n")
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping server...")
        backend_process.terminate()
        print("✅ Server stopped. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
