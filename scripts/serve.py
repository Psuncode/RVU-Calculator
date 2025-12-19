#!/usr/bin/env python3
"""
Simple HTTP server for the RVU Calculator
==========================================
This script starts a local web server to avoid CORS issues when loading JSON data.

Usage:
    python serve.py [port]

Default port: 8000

Then open: http://localhost:8000
"""

import http.server
import socketserver
import sys
import os
import webbrowser
from pathlib import Path

# Serve the shipping SPA from app/
repo_root = Path(__file__).resolve().parent.parent
app_root = repo_root / 'app'
os.chdir(app_root)

# Get port from command line or use default
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

# Create server
Handler = http.server.SimpleHTTPRequestHandler

# Add CORS headers to allow local development
class CORSRequestHandler(Handler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

    def log_message(self, format, *args):
        # Simplified logging
        print(f"[{self.log_date_time_string()}] {format % args}")

try:
    with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
        print(f"""
╔════════════════════════════════════════════════════════╗
║         RVU Calculator - Local Server                  ║
╚════════════════════════════════════════════════════════╝

✓ Server running at: http://localhost:{PORT}
✓ Serving files from: {os.getcwd()}

📂 Data files:
   • rvu_data.json: {os.path.exists('data/processed/rvu_data.json') and '✓ Found' or '✗ Missing'}
   • gpci_data.json: {os.path.exists('data/processed/gpci_data.json') and '✓ Found' or '✗ Missing'}
   • metadata.json: {os.path.exists('data/processed/metadata.json') and '✓ Found' or '✗ Missing'}
   • rvu_timeline_2019_2025.json: {os.path.exists('data/processed/rvu_timeline_2019_2025.json') and '✓ Found' or '✗ Missing'}

🌐 Opening browser...
   (If it doesn't open, visit: http://localhost:{PORT})

Press Ctrl+C to stop the server.
        """)

        # Open browser
        webbrowser.open(f'http://localhost:{PORT}')

        # Serve
        httpd.serve_forever()

except KeyboardInterrupt:
    print("\n\n✓ Server stopped.")
    sys.exit(0)
except OSError as e:
    if e.errno == 48:  # Address already in use
        print(f"\n✗ Error: Port {PORT} is already in use.")
        print(f"  Try a different port: python serve.py 8001")
    else:
        print(f"\n✗ Error: {e}")
    sys.exit(1)
