"""
Robust frontend server startup script
"""
import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 3000
DIRECTORY = Path(__file__).parent / "frontend"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Custom logging
        sys.stdout.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    
    print("=" * 60)
    print("Starting College Chatbot Admin Panel Frontend")
    print("=" * 60)
    print(f"\nFrontend URL: http://localhost:{PORT}")
    print(f"Serving from: {DIRECTORY}")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 60)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        httpd.allow_reuse_address = True
        try:
            print(f"\n✅ Server is running on port {PORT}")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down frontend server...")
            httpd.shutdown()
            print("✅ Frontend server stopped")
