"""
Simple run script for development - starts backend server
"""
import os
import sys

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("Starting College Chatbot Admin Panel Backend")
    print("=" * 60)
    print("\nBackend API: http://localhost:3000")
    print("API Docs: http://localhost:3000/docs")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 60)
    
    # Allow disabling reload for faster startup (useful when started from start.py)
    # Set environment variable RELOAD=1 to enable automatic reload during development.
    reload_flag = os.getenv("RELOAD", "0") in ("1", "true", "True")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=3000,
        reload=reload_flag,
        app_dir="backend"
    )
