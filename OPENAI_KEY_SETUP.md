# OpenAI API Key Setup Guide

## Current Issue
The Emergent LLM key (`sk-emergent-*`) doesn't work with LangChain's OpenAI integration.

## Solution Options

### Option 1: Use Your Own OpenAI API Key (Recommended)

1. **Get an OpenAI API Key**:
   - Go to https://platform.openai.com/api-keys
   - Sign in or create an account
   - Click "Create new secret key"
   - Copy the key (starts with `sk-proj-` or `sk-`)

2. **Update Backend .env**:
   ```bash
   # Edit the file
   nano /app/backend/.env
   
   # Or use this command
   echo 'OPENAI_API_KEY="sk-proj-YOUR-KEY-HERE"' >> /app/backend/.env
   ```

3. **Restart Backend**:
   ```bash
   sudo supervisorctl restart backend
   ```

4. **Verify It Works**:
   ```bash
   tail -f /var/log/supervisor/backend.err.log
   # Should see: "AI services initialized successfully"
   ```

---

### Option 2: Use Emergent Integration (Alternative)

If you want to use the Emergent LLM key, you need to use the `emergentintegrations` library:

1. **Install Emergent Integrations**:
   ```bash
   cd /app/backend
   pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
   ```

2. **Update multi_agent_system.py**:
   Replace:
   ```python
   from langchain_openai import ChatOpenAI
   
   self.llm = ChatOpenAI(
       api_key=openai_api_key,
       model="gpt-4o-mini"
   )
   ```
   
   With:
   ```python
   from emergentintegrations.openai import ChatOpenAI as EmergentChatOpenAI
   
   self.llm = EmergentChatOpenAI(
       api_key=openai_api_key,
       model="gpt-4o-mini"
   )
   ```

3. **Restart Backend**:
   ```bash
   sudo supervisorctl restart backend
   ```

---

## Testing the Setup

Once you've added a valid key, test it:

1. **Go to the app**: https://your-app-url.com
2. **Click center search bar**
3. **Type**: "Find team building activities for 20 people"
4. **Press Enter**
5. **Watch the agent states appear on the right panel**:
   - "Searching for activities..."
   - "Analyzing X activities for best matches..."
   - "Created X recommendations"

---

## Current Configuration

**File**: `/app/backend/.env`

```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="drew_events"
CORS_ORIGINS="*"
JWT_SECRET="your-secret-key-change-in-production"
OPENAI_API_KEY="sk-emergent-b8aEeA8664171BdA14"  # ⚠️ Replace this
```

**What Needs the Key**:
- Multi-agent system (LangChain + OpenAI)
- Semantic search (OpenAI embeddings)
- Recommendation agent (GPT-4o-mini)
- Itinerary builder agent
- Offerings agent

---

## Troubleshooting

### Error: "invalid_api_key"
- Your key is incorrect or expired
- Get a new key from OpenAI dashboard

### Error: "insufficient_quota"
- Your OpenAI account has no credits
- Add billing at https://platform.openai.com/account/billing

### Error: "rate_limit_exceeded"
- You're making too many requests
- Wait a few seconds and try again
- Upgrade your OpenAI plan

### Logs Show No Errors But Agent Doesn't Work
```bash
# Check if AI services initialized
tail -n 50 /var/log/supervisor/backend.err.log | grep "AI services"

# Should see:
# INFO - AI services initialized successfully
```

---

## Quick Fix Command

```bash
# Replace YOUR_KEY with actual OpenAI key
echo 'OPENAI_API_KEY="sk-proj-YOUR_KEY_HERE"' > /tmp/new_env
cat /app/backend/.env | grep -v OPENAI_API_KEY >> /tmp/new_env
mv /tmp/new_env /app/backend/.env
sudo supervisorctl restart backend

# Verify
tail -f /var/log/supervisor/backend.err.log
```

---

## Cost Estimates

Using OpenAI API with this setup:

**Per Request**:
- GPT-4o-mini: ~$0.0001-0.001
- Text embeddings: ~$0.00001

**Expected Monthly Cost** (100 requests/day):
- ~$3-10/month

**Tips to Reduce Costs**:
1. Use `gpt-3.5-turbo` instead of `gpt-4o-mini`
2. Cache embeddings (already implemented)
3. Limit max tokens in responses
4. Use fewer agents for simple queries

---

## Next Steps

1. ✅ Get OpenAI API key
2. ✅ Update `.env` file
3. ✅ Restart backend
4. ✅ Test with a prompt
5. ✅ Watch agent states appear in real-time
