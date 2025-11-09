#!/bin/bash
# Run main backend server with virtual environment

echo "🚀 Starting Main Backend Server..."
echo "==================================="

# Check if using global venv or local venv
if [ -d "/app/backend/venv" ]; then
    echo "📦 Using local virtual environment: /app/backend/venv"
    source /app/backend/venv/bin/activate
elif [ -d "/root/.venv" ]; then
    echo "📦 Using global virtual environment: /root/.venv"
    source /root/.venv/bin/activate
else
    echo "⚠️  No virtual environment found!"
    echo "Either:"
    echo "  1. Run: ./setup_backend_venv.sh"
    echo "  2. Or use global venv: source /root/.venv/bin/activate"
    exit 1
fi

# Verify Python and packages
echo "🐍 Python: $(which python)"
echo "📍 Virtual env: $VIRTUAL_ENV"

# Change to backend directory
cd /app/backend

# Check if server.py exists
if [ ! -f "server.py" ]; then
    echo "❌ server.py not found in /app/backend"
    exit 1
fi

echo "==================================="
echo "✅ Starting server on port 8001..."
echo "   API: http://localhost:8001/api"
echo "   Docs: http://localhost:8001/docs"
echo "==================================="
echo ""

# Run the server
python server.py
