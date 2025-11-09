#!/bin/bash
# Setup virtual environment for main backend

echo "🔧 Setting up virtual environment for main backend..."
echo "================================================"

cd /app/backend

# Check if venv already exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists at /app/backend/venv"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        echo "🗑️  Removed existing virtual environment"
    else
        echo "❌ Aborted"
        exit 1
    fi
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    echo "Try: sudo apt-get install python3-venv"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "================================================"
echo "✅ Main backend virtual environment ready!"
echo "================================================"
echo ""
echo "To activate this environment:"
echo "  source /app/backend/venv/bin/activate"
echo ""
echo "To run the server:"
echo "  cd /app/backend && python server.py"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
