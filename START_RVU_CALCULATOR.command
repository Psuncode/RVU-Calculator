#!/bin/bash

# RVU Calculator Launcher Script
# Double-click this file to start the calculator

clear
echo "================================================"
echo "   RVU Calculator - Starting Local Server"
echo "================================================"
echo ""

# Navigate to app directory
cd "$(dirname "$0")/app"

# Function to check if port is in use
check_port() {
    lsof -i :8000 >/dev/null 2>&1
    return $?
}

# Check if port 8000 is already in use
if check_port; then
    echo "⚠️  Port 8000 is already in use."
    echo "    Opening browser to existing server..."
    open "http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to exit this terminal window"
    read -r -d '' _ </dev/tty
    exit 0
fi

# Detect available server
if command -v python3 &> /dev/null; then
    echo "✓ Using Python 3 web server"
    echo "  Server URL: http://localhost:8000"
    echo ""
    echo "📂 Serving from: $(pwd)"
    echo ""
    echo "🌐 Opening browser..."

    # Open browser after 2 seconds
    (sleep 2 && open "http://localhost:8000") &

    echo ""
    echo "================================================"
    echo "  Server is running!"
    echo "  Press Ctrl+C to stop the server"
    echo "================================================"
    echo ""

    # Start server
    python3 -m http.server 8000

elif command -v php &> /dev/null; then
    echo "✓ Using PHP web server"
    echo "  Server URL: http://localhost:8000"
    echo ""
    echo "📂 Serving from: $(pwd)"
    echo ""
    echo "🌐 Opening browser..."

    (sleep 2 && open "http://localhost:8000") &

    echo ""
    echo "================================================"
    echo "  Server is running!"
    echo "  Press Ctrl+C to stop the server"
    echo "================================================"
    echo ""

    php -S localhost:8000

elif command -v node &> /dev/null && command -v npx &> /dev/null; then
    echo "✓ Using Node.js web server"
    echo "  Server URL: http://localhost:8000"
    echo ""
    echo "📂 Serving from: $(pwd)"
    echo ""
    echo "🌐 Opening browser..."

    (sleep 2 && open "http://localhost:8000") &

    echo ""
    echo "================================================"
    echo "  Server is running!"
    echo "  Press Ctrl+C to stop the server"
    echo "================================================"
    echo ""

    npx --yes http-server -p 8000

else
    echo "❌ ERROR: No web server available"
    echo ""
    echo "Please install one of the following:"
    echo "  • Python 3: https://www.python.org/downloads/"
    echo "  • Node.js: https://nodejs.org/"
    echo "  • PHP: Should be pre-installed on macOS"
    echo ""
    echo "After installation, double-click this file again."
    echo ""
    read -n 1 -s -r -p "Press any key to exit..."
    exit 1
fi
