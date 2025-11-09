# Virtual Environment Setup Guide

## 📋 Current Setup

You already have a **global virtual environment** at `/root/.venv/` that contains all your Python packages. This is currently being used by both your main backend and agentic backend.

## 🎯 Two Options for Virtual Environment Management

### **Option 1: Keep Using Global Virtual Environment (RECOMMENDED - Easiest)**

✅ **Pros:**
- Already set up and working
- All dependencies already installed
- No need to switch environments
- Simpler to manage

❌ **Cons:**
- Both backends share the same environment
- Potential version conflicts if backends need different package versions

**Current Status**: ✅ Active and working

---

### **Option 2: Separate Virtual Environments per Backend**

✅ **Pros:**
- Clean separation between projects
- No dependency conflicts
- Can use different Python versions if needed

❌ **Cons:**
- More complex to manage
- Need to switch environments
- Duplicate packages

---

## 🚀 Quick Start (Using Current Setup)

Your current setup is already working! Just activate the existing environment:

```bash
# Activate virtual environment (if not already active)
source /root/.venv/bin/activate

# Verify it's active (you should see (.venv) in your prompt)
which python
# Output: /root/.venv/bin/python

# Run your backends
cd /app/backend && python server.py          # Main backend
cd /app/agentic_backend && python server.py  # Agentic backend
```

---

## 🔧 Option 1: Keep Using Global Virtual Environment

### Current Setup
```bash
# Your virtual environment location
/root/.venv/

# Already contains packages for:
- Main backend (FastAPI, Motor, PyMongo, etc.)
- Agentic backend (LangGraph, LangChain, etc.)
```

### How to Use

```bash
# 1. Activate (usually done automatically)
source /root/.venv/bin/activate

# 2. Install new packages if needed
pip install package-name

# 3. Run your servers
python /app/backend/server.py
python /app/agentic_backend/server.py
```

### Adding New Packages

```bash
# For main backend
cd /app/backend
source /root/.venv/bin/activate
pip install new-package
pip freeze > requirements.txt  # Update requirements

# For agentic backend
cd /app/agentic_backend
source /root/.venv/bin/activate
pip install new-package
pip freeze > requirements.txt  # Update requirements
```

---

## 🔧 Option 2: Create Separate Virtual Environments

If you want separate environments for each backend:

### For Main Backend

```bash
# 1. Create virtual environment
cd /app/backend
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Verify installation
python -c "import fastapi; print('FastAPI installed')"

# 5. Run server
python server.py
```

### For Agentic Backend

```bash
# 1. Create virtual environment
cd /app/agentic_backend
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# 4. Verify installation
python -c "import langgraph; print('LangGraph installed')"

# 5. Run server
python server.py
```

---

## 📝 Virtual Environment Commands Cheat Sheet

```bash
# CREATE virtual environment
python3 -m venv venv                    # Creates 'venv' folder

# ACTIVATE virtual environment
source venv/bin/activate                # On Linux/Mac
# or
source /root/.venv/bin/activate         # Global venv

# DEACTIVATE virtual environment
deactivate

# CHECK if activated
which python                            # Should show venv path
echo $VIRTUAL_ENV                       # Should show venv path

# INSTALL packages
pip install package-name
pip install -r requirements.txt

# UPDATE requirements.txt
pip freeze > requirements.txt

# LIST installed packages
pip list
pip freeze

# UPGRADE pip
pip install --upgrade pip

# REMOVE virtual environment
deactivate                              # First deactivate
rm -rf venv                            # Then delete folder
```

---

## 🎯 Recommended Setup Scripts

I'll create helper scripts for you:

### 1. `setup_backend_venv.sh` - Main Backend
```bash
#!/bin/bash
cd /app/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Main backend virtual environment ready!"
echo "Activate with: source /app/backend/venv/bin/activate"
```

### 2. `setup_agentic_venv.sh` - Agentic Backend
```bash
#!/bin/bash
cd /app/agentic_backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
echo "✅ Agentic backend virtual environment ready!"
echo "Activate with: source /app/agentic_backend/venv/bin/activate"
```

### 3. `run_backend.sh` - Run Main Backend
```bash
#!/bin/bash
source /root/.venv/bin/activate  # or /app/backend/venv/bin/activate
cd /app/backend
python server.py
```

### 4. `run_agentic.sh` - Run Agentic Backend
```bash
#!/bin/bash
source /root/.venv/bin/activate  # or /app/agentic_backend/venv/bin/activate
cd /app/agentic_backend
python server.py
```

---

## 🔍 Checking Your Current Setup

Run this to see what's currently installed:

```bash
# Check active Python
which python
python --version

# Check if in virtual environment
echo $VIRTUAL_ENV

# List installed packages
pip list | grep -E "(fastapi|langgraph|motor|pymongo)"

# Check package locations
pip show fastapi
pip show langgraph
```

---

## 🐛 Troubleshooting

### Problem: "pip: command not found"
```bash
# Solution: Install pip
python -m ensurepip --upgrade
```

### Problem: "No module named 'venv'"
```bash
# Solution: Install venv module
apt-get update
apt-get install python3-venv
```

### Problem: "Permission denied"
```bash
# Solution: Use sudo or check permissions
sudo python3 -m venv venv
# or
chmod +x setup_backend_venv.sh
```

### Problem: Virtual environment not activating
```bash
# Solution: Source the activate script
source /path/to/venv/bin/activate

# Check activation
echo $VIRTUAL_ENV  # Should show path
which python       # Should show venv path
```

### Problem: Packages not found after installation
```bash
# Solution: Make sure venv is activated
source venv/bin/activate

# Then reinstall
pip install -r requirements.txt
```

### Problem: Different package versions needed
```bash
# Solution: Use separate virtual environments
# Follow "Option 2" above
```

---

## 📊 Virtual Environment Structure

```
venv/
├── bin/                    # Executables
│   ├── activate           # Activation script
│   ├── python             # Python binary (symlink)
│   ├── pip                # Pip (symlink)
│   └── ...
├── include/               # C headers
├── lib/                   # Installed packages
│   └── python3.11/
│       └── site-packages/ # Your packages here
└── pyvenv.cfg            # Config file
```

---

## 🎯 Best Practices

1. **Always activate** before installing packages
2. **Update requirements.txt** after installing new packages
3. **Use .gitignore** to exclude venv folder
4. **Document** which venv to use in README
5. **Pin versions** in requirements.txt for reproducibility

### Example .gitignore
```
venv/
.venv/
env/
*.pyc
__pycache__/
.env
```

### Pin Versions in requirements.txt
```
fastapi==0.110.1
motor==3.7.1
langgraph==0.2.0
```

---

## 💡 Recommended Approach for Your Setup

**I recommend continuing to use the global virtual environment** (`/root/.venv/`) because:

✅ It's already working
✅ Both backends are compatible
✅ Simpler to manage
✅ No need to switch environments

**Only create separate environments if:**
- You need different Python versions
- You have conflicting package versions
- You want strict isolation between projects

---

## 🚀 Quick Commands for Your Current Setup

```bash
# Check if venv is active
which python
# Should output: /root/.venv/bin/python

# Activate if needed (usually automatic)
source /root/.venv/bin/activate

# Install new package
pip install package-name

# Update requirements for main backend
cd /app/backend
pip freeze | grep -v "pkg-resources" > requirements.txt

# Update requirements for agentic backend  
cd /app/agentic_backend
pip freeze | grep -v "pkg-resources" > requirements.txt

# Run main backend
cd /app/backend && python server.py

# Run agentic backend (different terminal)
cd /app/agentic_backend && python server.py
```

---

## ✅ Your Current Status

- ✅ Global virtual environment: `/root/.venv/`
- ✅ Python version: 3.11.14
- ✅ All packages installed and working
- ✅ Both backends can use the same environment
- ✅ Ready to run without any changes

**Conclusion**: Your setup is already optimal! No changes needed unless you specifically want separate environments.
