# Environment Variables Setup Guide

## 📋 Current Configuration

Your agentic backend is configured with the following environment variables:

### ✅ LLM Configuration

```env
EMERGENT_LLM_KEY=sk-emergent-b8aEeA8664171BdA14
DEFAULT_MODEL=gpt-4o-mini
DEFAULT_PROVIDER=openai
```

**What it does**:
- Uses Emergent's universal LLM key (works with OpenAI, Anthropic, Google)
- Default model is GPT-4o-mini (fast and cost-effective)
- Default provider is OpenAI

**To change**:
- To use a different model: `DEFAULT_MODEL=gpt-5` or `DEFAULT_MODEL=claude-4-sonnet-20250514`
- To use a different provider: `DEFAULT_PROVIDER=anthropic` or `DEFAULT_PROVIDER=gemini`
- To use your own API key: Replace the EMERGENT_LLM_KEY value

**Available Models**:
- **OpenAI**: gpt-5, gpt-5-mini, gpt-4o, gpt-4o-mini, o1, o3-mini
- **Anthropic**: claude-3-7-sonnet-20250219, claude-4-sonnet-20250514
- **Google**: gemini-2.0-flash, gemini-2.5-pro

---

### ✅ MongoDB Configuration

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=agentic_backend
```

**What it does**:
- Connects to MongoDB on localhost (same server)
- Uses a separate database `agentic_backend` for agent data
- Your main backend uses `drew_events` database (no conflict)

**Collections created**:
- `checkpoints` - Agent state checkpoints
- `threads` - Conversation threads
- `messages` - Messages with embeddings
- `summaries` - Thread summaries

**To verify MongoDB is running**:
```bash
mongosh --eval "db.version()"
```

---

### ✅ Main Backend API Configuration

```env
MAIN_BACKEND_URL=http://localhost:8001
MAIN_BACKEND_API_PREFIX=/api
```

**What it does**:
- Connects to your main FastAPI backend on port 8001
- Uses the `/api` prefix for all backend calls
- This allows the agent to fetch events from your main backend

**Important**: This is for **internal communication** between services on the same server.

**Your main backend URL**: `https://drew-events-agent.preview.emergentagent.com`
- This is the **external** URL that frontend uses
- The agentic backend uses `localhost:8001` for **internal** communication
- Both are correct for their respective use cases!

---

### ✅ Server Configuration

```env
AGENTIC_SERVER_HOST=0.0.0.0
AGENTIC_SERVER_PORT=8002
```

**What it does**:
- Binds to all network interfaces (0.0.0.0) so it can be accessed externally
- Runs on port 8002 (different from main backend on 8001)

**Access URLs**:
- **Internal**: `http://localhost:8002`
- **External**: `https://drew-events-agent.preview.emergentagent.com:8002` (if port is exposed)
- **API Docs**: `http://localhost:8002/docs`

---

### ✅ Thread Management

```env
MAX_TOKENS_PER_THREAD=8000
SUMMARIZATION_THRESHOLD=6000
MAX_MESSAGES_PER_THREAD=100
```

**What it does**:
- **MAX_TOKENS_PER_THREAD**: Maximum tokens in a thread before cleanup
- **SUMMARIZATION_THRESHOLD**: When to create automatic summaries (at 6000 tokens)
- **MAX_MESSAGES_PER_THREAD**: Maximum number of messages to keep in a thread

**Why this matters**:
- Prevents context overflow errors with LLMs
- Keeps conversation history manageable
- Automatic summarization maintains context even in long conversations

**To adjust**:
- Increase if you need longer conversations: `SUMMARIZATION_THRESHOLD=10000`
- Decrease for more frequent summaries: `SUMMARIZATION_THRESHOLD=4000`

---

### ✅ Embeddings Configuration

```env
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
```

**What it does**:
- Uses OpenAI's text-embedding-3-small model for generating embeddings
- 1536 dimensions for vector search
- Powers semantic search on messages

**Cost consideration**:
- text-embedding-3-small is the most cost-effective
- Alternative: `text-embedding-3-large` (better quality, higher cost)

---

## 🔧 Common Configuration Scenarios

### Scenario 1: Using Your Own OpenAI Key

```env
# Replace the Emergent key with your OpenAI key
EMERGENT_LLM_KEY=sk-your-openai-key-here
DEFAULT_MODEL=gpt-4o
DEFAULT_PROVIDER=openai
```

### Scenario 2: Using Claude Models

```env
# Keep Emergent key (it works with Claude)
EMERGENT_LLM_KEY=sk-emergent-b8aEeA8664171BdA14
DEFAULT_MODEL=claude-4-sonnet-20250514
DEFAULT_PROVIDER=anthropic
```

### Scenario 3: Using Google Gemini

```env
# Keep Emergent key (it works with Gemini)
EMERGENT_LLM_KEY=sk-emergent-b8aEeA8664171BdA14
DEFAULT_MODEL=gemini-2.5-pro
DEFAULT_PROVIDER=gemini
```

### Scenario 4: Remote MongoDB

```env
# If using MongoDB Atlas or remote MongoDB
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=agentic_backend
```

### Scenario 5: Different Port

```env
# If port 8002 is already in use
AGENTIC_SERVER_PORT=8003
```

---

## 🚀 Quick Start

### 1. Verify Environment Variables

```bash
cd /app/agentic_backend
cat .env
```

### 2. Test MongoDB Connection

```bash
python -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path('/app/agentic_backend/.env'))
async def test():
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    result = await client.admin.command('ping')
    print('✅ MongoDB connection successful!', result)
    client.close()
asyncio.run(test())
"
```

### 3. Test Configuration Loading

```bash
cd /app/agentic_backend
python -c "from config import config; print('✅ LLM Key:', config.llm.api_key[:20]+'...'); print('✅ Model:', config.llm.default_model); print('✅ MongoDB:', config.mongodb.db_name); print('✅ Port:', config.server.port)"
```

### 4. Start the Server

```bash
cd /app/agentic_backend
python server.py
```

---

## 🔍 Troubleshooting

### Issue: "Cannot connect to MongoDB"

**Solution**: Check if MongoDB is running
```bash
sudo systemctl status mongod
# or
mongosh --eval "db.version()"
```

### Issue: "Port 8002 already in use"

**Solution**: Change the port in .env
```env
AGENTIC_SERVER_PORT=8003
```

Then restart the server.

### Issue: "Cannot reach main backend"

**Solution**: Verify main backend is running
```bash
curl http://localhost:8001/api/
```

### Issue: "Embedding generation failed"

**Solution**: Check your API key
```bash
python -c "from config import config; print('API Key:', config.llm.api_key[:20]+'...' if config.llm.api_key else 'NOT SET')"
```

---

## 📊 Environment Variables Priority

The system loads environment variables in this order:

1. **System environment variables** (highest priority)
2. **.env file** in `/app/agentic_backend/`
3. **Default values** in `config.py` (lowest priority)

To override .env values, set system environment variables:

```bash
export AGENTIC_SERVER_PORT=8003
python server.py
```

---

## 🔐 Security Best Practices

### ✅ Good Practices

- ✅ Keep `.env` file out of version control (it is)
- ✅ Use environment-specific values (dev, staging, prod)
- ✅ Rotate API keys regularly
- ✅ Use MongoDB authentication in production

### ⚠️ Things to Change in Production

```env
# Add MongoDB authentication
MONGO_URL=mongodb://username:password@localhost:27017/

# Use proper CORS origins
CORS_ORIGINS=https://your-domain.com,https://api.your-domain.com

# Use your own API keys
EMERGENT_LLM_KEY=your-production-key

# Add rate limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

---

## 📝 Full Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMERGENT_LLM_KEY` | Yes | - | Universal LLM API key |
| `DEFAULT_MODEL` | No | gpt-4o-mini | Default LLM model |
| `DEFAULT_PROVIDER` | No | openai | Default LLM provider |
| `MONGO_URL` | Yes | mongodb://localhost:27017 | MongoDB connection string |
| `DB_NAME` | No | agentic_backend | Database name |
| `MAIN_BACKEND_URL` | Yes | http://localhost:8001 | Main backend URL |
| `MAIN_BACKEND_API_PREFIX` | No | /api | API prefix |
| `AGENTIC_SERVER_HOST` | No | 0.0.0.0 | Server host |
| `AGENTIC_SERVER_PORT` | No | 8002 | Server port |
| `MAX_TOKENS_PER_THREAD` | No | 8000 | Max tokens per thread |
| `SUMMARIZATION_THRESHOLD` | No | 6000 | Summarization trigger |
| `MAX_MESSAGES_PER_THREAD` | No | 100 | Max messages |
| `EMBEDDING_MODEL` | No | text-embedding-3-small | Embedding model |
| `EMBEDDING_DIMENSIONS` | No | 1536 | Embedding dimensions |
| `CORS_ORIGINS` | No | * | CORS allowed origins |

---

## 🎯 Quick Commands

```bash
# View current configuration
cat /app/agentic_backend/.env

# Edit configuration
nano /app/agentic_backend/.env

# Test configuration
cd /app/agentic_backend && python -c "from config import config; print('Config OK')"

# Start server
cd /app/agentic_backend && python server.py

# Check if server is running
curl http://localhost:8002/health

# View logs (if using supervisor)
tail -f /var/log/supervisor/agentic_backend.*.log
```

---

## ✅ Your Current Setup is Correct!

Your environment variables are already properly configured for:
- ✅ Local development
- ✅ Integration with main backend
- ✅ MongoDB persistence
- ✅ Emergent LLM key usage
- ✅ Proper port separation (8001 for main, 8002 for agentic)

No changes needed unless you want to:
- Use a different LLM model
- Use your own API keys
- Adjust token limits
- Change ports

**Ready to start**: `cd /app/agentic_backend && python server.py` 🚀
