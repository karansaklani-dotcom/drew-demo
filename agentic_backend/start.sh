#!/bin/bash

# Startup script for agentic backend

echo "Starting Agentic Backend..."
echo "======================================"

# Check if MongoDB is accessible
echo "Checking MongoDB connection..."
if mongosh --eval "db.version()" > /dev/null 2>&1; then
    echo "✓ MongoDB is accessible"
else
    echo "⚠ Warning: MongoDB might not be accessible"
fi

# Set Python path
export PYTHONPATH="/app/agentic_backend:$PYTHONPATH"

# Start the server
cd /app/agentic_backend
echo ""
echo "Starting FastAPI server on port 8002..."
echo "API Documentation: http://localhost:8002/docs"
echo "======================================"
echo ""

python server.py
