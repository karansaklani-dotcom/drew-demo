#!/bin/bash
# Run agentic backend server with virtual environment

echo "🚀 Starting Agentic Backend Server..."
echo "====================================="

# Check if using global venv or local venv
if [ -d "/app/agentic_backend/venv" ]; then
    echo "📦 Using local virtual environment: /app/agentic_backend/venv"
    source /app/agentic_backend/venv/bin/activate
elif [ -d "/root/.venv" ]; then
    echo "📦 Using global virtual environment: /root/.venv"
    source /root/.venv/bin/activate
else
    echo "⚠️  No virtual environment found!"
    echo "Either:"
    echo "  1. Run: ./setup_agentic_venv.sh"
    echo "  2. Or use global venv: source /root/.venv/bin/activate"
    exit 1
fi

# Verify Python and packages
echo "🐍 Python: $(which python)"
echo "📍 Virtual env: $VIRTUAL_ENV"

# Change to agentic backend directory
cd /app/agentic_backend

# Check if server.py exists
if [ ! -f "server.py" ]; then
    echo "❌ server.py not found in /app/agentic_backend"
    exit 1
fi

echo "====================================="
echo "✅ Starting server on port 8002..."
echo "   API: http://localhost:8002/api"
echo "   Docs: http://localhost:8002/docs"
echo "   Health: http://localhost:8002/health"
echo "====================================="
echo ""

# Run the server
python server.py
