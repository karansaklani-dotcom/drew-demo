# Agentic Backend - Quick Reference Card

## 🚀 Quick Start

```bash
# 1. Validate environment
cd /app/agentic_backend
python validate_env.py

# 2. Start the server
python server.py

# 3. Test it's working
curl http://localhost:8002/health
```

## 📝 Environment Files

| File | Purpose | Location |
|------|---------|----------|
| `.env` | Environment configuration | `/app/agentic_backend/.env` |
| `config.py` | Configuration loader | `/app/agentic_backend/config.py` |

## 🔑 Key Environment Variables

```env
# Most Important
EMERGENT_LLM_KEY=sk-emergent-b8aEeA8664171BdA14  # Universal LLM key
MONGO_URL=mongodb://localhost:27017              # MongoDB connection
MAIN_BACKEND_URL=http://localhost:8001           # Main backend
AGENTIC_SERVER_PORT=8002                         # This server port

# Tuning (Optional)
DEFAULT_MODEL=gpt-4o-mini                        # LLM model
SUMMARIZATION_THRESHOLD=6000                     # Token limit
```

## 🌐 Service URLs

| Service | Internal URL | External URL |
|---------|--------------|--------------|
| Main Backend | http://localhost:8001 | https://drew-auth-service.preview.emergentagent.com |
| Agentic Backend | http://localhost:8002 | (Configure if needed) |
| MongoDB | mongodb://localhost:27017 | N/A |

## 📊 Ports

- **8001**: Main FastAPI backend (existing)
- **8002**: Agentic backend (new)
- **27017**: MongoDB

## 🗄️ Database Collections

In MongoDB database `agentic_backend`:
- `checkpoints` - LangGraph state
- `threads` - Conversation threads  
- `messages` - Messages with embeddings
- `summaries` - Thread summaries

## 🛠️ Common Commands

```bash
# Check environment
cat /app/agentic_backend/.env

# Validate configuration
python /app/agentic_backend/validate_env.py

# Test integration
python /app/agentic_backend/test_integration.py

# Start server
cd /app/agentic_backend && python server.py

# Check health
curl http://localhost:8002/health

# View API docs
open http://localhost:8002/docs
```

## 🔍 Testing Endpoints

```bash
# Health check
curl http://localhost:8002/health

# Create thread
curl -X POST http://localhost:8002/api/threads \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "event_discovery"}'

# Invoke agent
curl -X POST http://localhost:8002/api/agents/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find concerts in SF",
    "user_preferences": {"location": "San Francisco"}
  }'
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port already in use | Change `AGENTIC_SERVER_PORT` in .env |
| MongoDB not connected | Check `mongosh` or restart MongoDB |
| Can't reach main backend | Verify main backend is running on 8001 |
| Module not found | Run `pip install -r requirements.txt` |

## 📚 Documentation

- Full Guide: `/app/agentic_backend/README.md`
- Environment Setup: `/app/agentic_backend/ENV_SETUP_GUIDE.md`
- Summary: `/app/AGENTIC_BACKEND_SUMMARY.md`
- Examples: `/app/agentic_backend/examples/`

## 🔄 Quick Changes

### Change LLM Model
```bash
# Edit .env
nano /app/agentic_backend/.env

# Change this line:
DEFAULT_MODEL=gpt-5  # or claude-4-sonnet-20250514, gemini-2.5-pro

# Restart server
```

### Change Port
```bash
# Edit .env
nano /app/agentic_backend/.env

# Change this line:
AGENTIC_SERVER_PORT=8003

# Restart server
```

### Use Your Own API Key
```bash
# Edit .env
nano /app/agentic_backend/.env

# Replace:
EMERGENT_LLM_KEY=your-actual-openai-key

# Restart server
```

## ✅ Current Configuration Status

Your environment is **VALIDATED** and ready ✅

- ✅ LLM: OpenAI GPT-4o-mini with Emergent key
- ✅ MongoDB: Connected to localhost:27017
- ✅ Main Backend: Connected to localhost:8001
- ✅ Port: 8002 (available)
- ✅ Dependencies: All installed

## 🎯 Next Steps

1. **Start the server**: `cd /app/agentic_backend && python server.py`
2. **Test basic functionality**: Run examples in `/app/agentic_backend/examples/`
3. **Integrate with your app**: Use API endpoints from your frontend
4. **Monitor**: Check logs for any issues

## 💡 Pro Tips

- Use `validate_env.py` before starting server
- Check health endpoint after any configuration change
- API docs at `/docs` show all endpoints
- Examples folder has working code samples
- MongoDB can be inspected with `mongosh`

---

**Need help?** See full documentation in `/app/agentic_backend/README.md` or run `python validate_env.py`
