"""
Quick diagnostic script to check server status
"""
import subprocess
import requests
import sys

def check_port(port):
    """Check what's running on a port"""
    if sys.platform == "win32":
        result = subprocess.run(
            f'netstat -ano | findstr :{port} | findstr LISTENING',
            shell=True,
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    return False

def test_backend():
    """Test if backend API is responding correctly"""
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        data = response.json()
        if isinstance(data, dict) and "message" in data:
            return True, "✅ Backend API is running correctly"
        else:
            return False, "❌ Port 8000 is occupied by wrong service (not FastAPI)"
    except requests.exceptions.ConnectionError:
        return False, "❌ Cannot connect to port 8000"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def test_frontend():
    """Test if frontend is accessible"""
    try:
        response = requests.get("http://localhost:3000/", timeout=2)
        if response.status_code == 200 and "<!DOCTYPE html>" in response.text:
            return True, "✅ Frontend is serving correctly"
        else:
            return False, "❌ Frontend not responding properly"
    except requests.exceptions.ConnectionError:
        return False, "❌ Cannot connect to port 3000"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def main():
    print("=" * 70)
    print("🔍 Server Status Checker")
    print("=" * 70)
    
    print("\n📊 Port Status:")
    port_8000 = check_port(8000)
    port_3000 = check_port(3000)
    print(f"   Port 8000: {'🟢 LISTENING' if port_8000 else '🔴 NOT LISTENING'}")
    print(f"   Port 3000: {'🟢 LISTENING' if port_3000 else '🔴 NOT LISTENING'}")
    
    print("\n🧪 Backend API Test:")
    backend_ok, backend_msg = test_backend()
    print(f"   {backend_msg}")
    
    print("\n🌐 Frontend Test:")
    frontend_ok, frontend_msg = test_frontend()
    print(f"   {frontend_msg}")
    
    print("\n" + "=" * 70)
    if backend_ok and frontend_ok:
        print("✅ All systems operational!")
        print("\n💡 You can now login at: http://localhost:3000")
        print("   Email: admin@college.edu")
        print("   Password: admin123")
    else:
        print("⚠️  Issues detected!")
        if not backend_ok:
            print("\n🔧 To fix backend issues:")
            print("   1. Stop all Python processes using port 8000")
            print("   2. Run: python start_servers.py")
        if not frontend_ok:
            print("\n🔧 To fix frontend issues:")
            print("   1. Stop all Python processes using port 3000")
            print("   2. Run: python start_servers.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
