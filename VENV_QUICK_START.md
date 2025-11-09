# Virtual Environment - Quick Start Guide

## ✅ Your Current Setup (RECOMMENDED)

You're already using a **global virtual environment** that works for both backends!

```
Location: /root/.venv/
Python: 3.11.14
Status: ✅ Active and working
```

**Key packages installed:**
- ✅ FastAPI (main backend)
- ✅ LangGraph (agentic backend)
- ✅ Motor & PyMongo (MongoDB)
- ✅ All other dependencies

## 🚀 Quick Commands

### Check Your Virtual Environment Status
```bash
./check_venv.sh
```

### Run Your Backends
```bash
# Main backend (port 8001)
./run_backend.sh

# Agentic backend (port 8002) - in another terminal
./run_agentic.sh
```

### Manual Activation (if needed)
```bash
# Activate virtual environment
source /root/.venv/bin/activate

# Check it's active (should show /root/.venv/bin/python)
which python

# Run backends manually
cd /app/backend && python server.py
cd /app/agentic_backend && python server.py
```

## 📦 Installing New Packages

```bash
# 1. Activate venv (if not already active)
source /root/.venv/bin/activate

# 2. Install package
pip install package-name

# 3. Update requirements (optional but recommended)
cd /app/backend
pip freeze | grep -v "pkg-resources" > requirements.txt

# Or for agentic backend
cd /app/agentic_backend
pip freeze | grep -v "pkg-resources" > requirements.txt
```

## 🔧 Optional: Create Separate Virtual Environments

Only do this if you need strict isolation between projects:

```bash
# For main backend
./setup_backend_venv.sh

# For agentic backend
./setup_agentic_venv.sh

# Then activate the one you need
source /app/backend/venv/bin/activate           # Main backend
# or
source /app/agentic_backend/venv/bin/activate   # Agentic backend
```

## 📝 Helper Scripts Created

| Script | Purpose |
|--------|---------|
| `check_venv.sh` | Check virtual environment status |
| `run_backend.sh` | Run main backend (auto-activates venv) |
| `run_agentic.sh` | Run agentic backend (auto-activates venv) |
| `setup_backend_venv.sh` | Create separate venv for main backend |
| `setup_agentic_venv.sh` | Create separate venv for agentic backend |

All scripts are in `/app/` directory.

## ✅ Recommended Workflow

### Daily Use (Keep it Simple)
```bash
# Check status
./check_venv.sh

# Run main backend
./run_backend.sh

# Run agentic backend (new terminal)
./run_agentic.sh
```

### Installing New Package
```bash
# Activate venv
source /root/.venv/bin/activate

# Install
pip install new-package

# Update requirements
cd /app/backend  # or /app/agentic_backend
pip freeze > requirements.txt
```

### If Something Goes Wrong
```bash
# Check what's active
which python
echo $VIRTUAL_ENV

# Deactivate
deactivate

# Reactivate
source /root/.venv/bin/activate

# Check packages
pip list
```

## 🎯 Key Points

✅ **Your current setup is optimal** - no changes needed!
✅ **Global venv** (`/root/.venv/`) works for both backends
✅ **All packages** are already installed
✅ **Helper scripts** make it even easier

❌ **Don't create separate venvs** unless you have specific conflicts
❌ **Don't deactivate** unless switching Python versions

## 📚 Full Documentation

- **Complete Guide**: `/app/VIRTUAL_ENV_SETUP.md`
- **Troubleshooting**: See "Troubleshooting" section in guide
- **Advanced Options**: See "Option 2" in guide

## 💡 Pro Tips

1. **Check before you run**: Use `./check_venv.sh` to verify setup
2. **Use helper scripts**: `./run_backend.sh` handles activation automatically
3. **Keep requirements updated**: Run `pip freeze > requirements.txt` after new installs
4. **Add to .gitignore**: Make sure `venv/` folders are ignored in git

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python not found" | `source /root/.venv/bin/activate` |
| "Module not found" | `pip install -r requirements.txt` |
| "Wrong Python version" | `which python` to check path |
| "Permission denied" | `chmod +x /app/*.sh` |

## ✨ Summary

**You're all set!** Your virtual environment is:
- ✅ Already created
- ✅ Already activated
- ✅ Has all packages installed
- ✅ Ready to use

Just run your backends:
```bash
./run_backend.sh        # Terminal 1
./run_agentic.sh        # Terminal 2
```

That's it! 🚀
