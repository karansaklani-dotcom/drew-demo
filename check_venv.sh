#!/bin/bash
# Check virtual environment status

echo "🔍 Virtual Environment Status Check"
echo "===================================="
echo ""

# Check current Python
echo "1️⃣  Current Python:"
which python
python --version
echo ""

# Check if in virtual environment
echo "2️⃣  Virtual Environment:"
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Active: $VIRTUAL_ENV"
else
    echo "❌ Not active"
    echo "   To activate global: source /root/.venv/bin/activate"
fi
echo ""

# Check global venv
echo "3️⃣  Global Virtual Environment (/root/.venv/):"
if [ -d "/root/.venv" ]; then
    echo "✅ Exists"
    if [ -f "/root/.venv/bin/python" ]; then
        /root/.venv/bin/python --version
    fi
else
    echo "❌ Not found"
fi
echo ""

# Check main backend venv
echo "4️⃣  Main Backend Virtual Environment (/app/backend/venv/):"
if [ -d "/app/backend/venv" ]; then
    echo "✅ Exists"
    if [ -f "/app/backend/venv/bin/python" ]; then
        /app/backend/venv/bin/python --version
    fi
else
    echo "❌ Not found (using global)"
fi
echo ""

# Check agentic backend venv
echo "5️⃣  Agentic Backend Virtual Environment (/app/agentic_backend/venv/):"
if [ -d "/app/agentic_backend/venv" ]; then
    echo "✅ Exists"
    if [ -f "/app/agentic_backend/venv/bin/python" ]; then
        /app/agentic_backend/venv/bin/python --version
    fi
else
    echo "❌ Not found (using global)"
fi
echo ""

# Check key packages
echo "6️⃣  Key Packages (in current environment):"
if command -v pip &> /dev/null; then
    pip list 2>/dev/null | grep -E "(fastapi|langgraph|motor|pymongo)" || echo "No key packages found"
else
    echo "pip not available"
fi
echo ""

echo "===================================="
echo "📝 Recommendations:"
echo ""

if [ -d "/root/.venv" ]; then
    echo "✅ You have a working global virtual environment"
    echo "   This is RECOMMENDED for your setup"
    echo ""
    echo "   To use it:"
    echo "   source /root/.venv/bin/activate"
else
    echo "⚠️  No virtual environment detected"
    echo "   Create one with:"
    echo "   ./setup_backend_venv.sh"
    echo "   ./setup_agentic_venv.sh"
fi
echo ""
