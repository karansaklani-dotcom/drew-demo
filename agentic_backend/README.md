# Agentic Backend - LangGraph-Based Intelligent Agent System

A sophisticated agentic backend system built with LangGraph, featuring MongoDB checkpointing, thread management, sub-agents, and event discovery capabilities.

## 🚀 Features

### Core Capabilities
- **✅ Checkpointing & State Persistence**: Full state management with MongoDB persistence
- **✅ Thread Management**: Comprehensive thread and message management system
- **✅ Embedding-Based Search**: Semantic search on messages using OpenAI embeddings
- **✅ Automatic Summarization**: Thread summarization when token limits are reached
- **✅ Sub-Agent Support**: Hierarchical agent architecture with subthreads and subcheckpointing
- **✅ Tool Integration**: Extensible tool system for agent capabilities
- **✅ API Gateway**: Server-to-server communication with cookie passthrough
- **✅ Event Discovery Agent**: Specialized agent for event recommendations

### Technical Stack
- **LangGraph**: For agent workflow orchestration
- **MongoDB**: State persistence and checkpointing
- **FastAPI**: High-performance async API
- **Emergent LLM Key**: Universal key for OpenAI, Anthropic, and Google models
- **OpenAI Embeddings**: Semantic search capabilities

## 📁 Project Structure

```
agentic_backend/
├── __init__.py
├── config.py                 # Configuration management
├── server.py                 # FastAPI server with all endpoints
├── requirements.txt          # Python dependencies
├── .env                     # Environment configuration
│
├── checkpointing/           # State persistence
│   ├── __init__.py
│   └── mongodb_checkpoint.py
│
├── threads/                 # Thread management
│   ├── __init__.py
│   ├── manager.py           # Thread and message management
│   ├── models.py            # Data models
│   └── summarizer.py        # Thread summarization
│
├── agents/                  # Agent implementations
│   ├── __init__.py
│   ├── base_agent.py        # Base agent with LangGraph
│   ├── event_agent.py       # Event discovery agent
│   └── sub_agent.py         # Sub-agent with subthreads
│
├── tools/                   # Agent tools
│   ├── __init__.py
│   └── event_tools.py       # Event-related tools
│
└── api/                     # API integration
    ├── __init__.py
    ├── client.py            # Main backend client
    └── gateway.py           # API gateway with cookie passthrough
```

## 🔧 Installation

1. **Install dependencies**:
```bash
cd /app/agentic_backend
pip install -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

2. **Configure environment**:
Edit `.env` file with your settings:
```env
# LLM Configuration
EMERGENT_LLM_KEY=sk-emergent-b8aEeA8664171BdA14
DEFAULT_MODEL=gpt-4o-mini
DEFAULT_PROVIDER=openai

# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=agentic_backend

# Main Backend API Configuration
MAIN_BACKEND_URL=http://localhost:8001
MAIN_BACKEND_API_PREFIX=/api

# Server Configuration
AGENTIC_SERVER_HOST=0.0.0.0
AGENTIC_SERVER_PORT=8002
```

## 🚦 Running the Server

### Development Mode
```bash
cd /app/agentic_backend
python server.py
```

### Production Mode
```bash
cd /app/agentic_backend
uvicorn server:app --host 0.0.0.0 --port 8002 --workers 4
```

The server will be available at: `http://localhost:8002`

## 📚 API Documentation

### Thread Management

#### Create Thread
```http
POST /api/threads
Content-Type: application/json

{
  "user_id": "user123",
  "agent_type": "event_discovery",
  "title": "Finding weekend events",
  "metadata": {}
}
```

#### Get Thread
```http
GET /api/threads/{thread_id}
```

#### Get Thread Messages
```http
GET /api/threads/{thread_id}/messages?limit=10&skip=0
```

#### Add Message
```http
POST /api/threads/messages
Content-Type: application/json

{
  "thread_id": "thread123",
  "role": "user",
  "content": "Find me some concerts in San Francisco",
  "metadata": {}
}
```

#### Semantic Search
```http
POST /api/threads/search
Content-Type: application/json

{
  "query": "rock concerts",
  "thread_id": "thread123",
  "limit": 10,
  "similarity_threshold": 0.7
}
```

#### Get Thread Context
```http
GET /api/threads/{thread_id}/context?recent_message_count=10
```

#### Get Thread Summaries
```http
GET /api/threads/{thread_id}/summaries
```

### Agent Operations

#### Invoke Agent
```http
POST /api/agents/invoke
Content-Type: application/json

{
  "message": "Find me jazz concerts this weekend",
  "thread_id": "thread123",
  "user_preferences": {
    "interests": ["jazz", "blues"],
    "location": "San Francisco"
  },
  "stream": false
}
```

#### Event Discovery
```http
POST /api/agents/event-discovery
Content-Type: application/json

{
  "message": "I want to discover events near me",
  "thread_id": "thread123",
  "preferences": {
    "interests": ["music", "art"],
    "location": "New York",
    "price_range": [0, 100]
  }
}
```

#### Execute Sub-Agent
```http
POST /api/agents/sub-agent
Content-Type: application/json

{
  "parent_thread_id": "parent123",
  "agent_type": "event_filter",
  "task_description": "Filter events by price under $50",
  "system_message": "You are a price filtering specialist"
}
```

#### Get Agent State
```http
GET /api/agents/{thread_id}/state
```

### API Gateway

Forward requests to main backend with cookie passthrough:

```http
GET /gateway/api/events?location=SF
POST /gateway/api/auth/login
PUT /gateway/api/users/profile
DELETE /gateway/api/events/123
```

### Utility Endpoints

#### Health Check
```http
GET /health
```

#### Proxy Events
```http
GET /api/main-backend/events?location=SF&category=music
GET /api/main-backend/events/{event_id}
```

## 🏗️ Architecture

### 1. Checkpointing System

The checkpointing system uses MongoDB to persist agent state at each step:

```python
from checkpointing import get_checkpointer

# Get checkpointer instance
checkpointer = await get_checkpointer()

# Automatic state persistence in LangGraph
graph = workflow.compile(checkpointer=checkpointer)
```

**Features**:
- Automatic state snapshots after each super-step
- Thread-based state isolation
- Checkpoint history retrieval
- Automatic cleanup of old checkpoints

### 2. Thread Management

Comprehensive thread and message management with:

```python
from threads.manager import ThreadManager

manager = ThreadManager()
await manager.initialize()

# Create thread
thread = await manager.create_thread(
    user_id="user123",
    agent_type="event_discovery"
)

# Add message with embedding
message = await manager.add_message(
    thread_id=thread.id,
    role=MessageType.USER,
    content="Find concerts",
    generate_embedding=True
)

# Semantic search
results = await manager.semantic_search(
    ThreadSearchQuery(
        query="rock concerts",
        thread_id=thread.id,
        limit=5
    )
)
```

**Features**:
- Message storage with content and tool call info
- Automatic embedding generation for semantic search
- Thread summarization after token limits
- Context building from summaries and recent messages

### 3. Agent System

Base agent with LangGraph integration:

```python
from agents import EventDiscoveryAgent

agent = EventDiscoveryAgent()
await agent.initialize()

# Invoke agent
result = await agent.invoke(
    message="Find jazz concerts",
    thread_id=thread_id,
    user_preferences={"location": "SF"}
)

# Stream responses
async for chunk in agent.stream(message, thread_id):
    print(chunk)
```

**Features**:
- Automatic checkpointing
- Tool calling capabilities
- State management
- Context-aware responses

### 4. Sub-Agent System

Hierarchical agent architecture:

```python
from agents.sub_agent import create_sub_agent

# Create sub-agent
sub_agent = await create_sub_agent(
    agent_type="price_filter",
    parent_thread_id=parent_thread_id,
    system_message="Filter events by price"
)

# Execute subtask
result = await sub_agent.execute_subtask(
    task_description="Find events under $50",
    parent_message_id=parent_msg_id
)

# Merge results to parent
await sub_agent.merge_context_to_parent()
```

**Features**:
- Subthread creation and management
- Independent checkpointing
- Context merging to parent thread
- Hierarchical task delegation

### 5. Tool System

Extensible tool framework:

```python
from tools.event_tools import create_event_tools

# Create tools
tools = create_event_tools(auth_token=token)

# Tools available:
# - search_events: Search by location, category, keywords
# - get_event_details: Get detailed event info
# - filter_events_by_criteria: Filter by price, date
# - recommend_events_by_preferences: Personalized recommendations
```

### 6. API Gateway

Server-to-server communication with cookie passthrough:

```python
from api.gateway import get_api_gateway

gateway = get_api_gateway()

# Forward request with cookies
response = await gateway.forward_request(
    request=request,
    path="/api/events",
    method="GET"
)

# Make authenticated request
response = await gateway.make_authenticated_request(
    path="/api/events",
    method="GET",
    cookies=cookies,
    auth_token=token
)
```

## 🔄 Thread Summarization

Automatic summarization when threads exceed token limits:

1. **Token Tracking**: Each message tracks token count
2. **Threshold Detection**: Summarization triggers at `SUMMARIZATION_THRESHOLD` (default: 6000 tokens)
3. **Summary Creation**: LLM generates comprehensive summary
4. **Context Building**: Future invocations use summaries + recent messages

```python
# Configuration in .env
MAX_TOKENS_PER_THREAD=8000
SUMMARIZATION_THRESHOLD=6000
MAX_MESSAGES_PER_THREAD=100
```

## 🔍 Semantic Search

Messages are automatically embedded for semantic search:

```python
# Search across threads
results = await thread_manager.semantic_search(
    ThreadSearchQuery(
        query="rock concerts in SF",
        thread_id="thread123",  # Optional: search specific thread
        limit=10,
        similarity_threshold=0.7,
        filter_metadata={"category": "music"}
    )
)

# Results include similarity scores
for result in results:
    print(f"Score: {result['similarity_score']}")
    print(f"Content: {result['content']}")
```

## 🔐 Authentication & Security

### Cookie Passthrough

The API gateway automatically forwards cookies from requests to the main backend:

```python
# Cookies are preserved in gateway requests
response = await gateway.forward_request(request, path, method)
```

### Token-Based Auth

Use Bearer tokens for authentication:

```python
headers = {"Authorization": f"Bearer {token}"}
response = await client.get_events(auth_token=token)
```

## 🎯 Use Cases

### 1. Event Discovery Chatbot

```python
# User starts conversation
result = await agent.invoke(
    message="I want to find concerts this weekend",
    thread_id=new_thread_id
)

# Agent uses tools to search events
# Context is maintained across messages
# Recommendations improve with conversation
```

### 2. Multi-Step Event Planning

```python
# Main agent handles overall planning
result = await main_agent.invoke(
    message="Plan a music festival weekend",
    thread_id=thread_id
)

# Sub-agent handles specific tasks
venue_agent = await create_sub_agent(
    agent_type="venue_finder",
    parent_thread_id=thread_id
)

await venue_agent.execute_subtask(
    "Find venues with capacity > 500"
)
```

### 3. Personalized Recommendations

```python
# Agent learns from conversation
user_preferences = {
    "interests": ["jazz", "blues", "indie"],
    "location": "San Francisco",
    "price_range": [0, 75],
    "preferred_days": ["Friday", "Saturday"]
}

result = await agent.invoke(
    message="Recommend events for me",
    thread_id=thread_id,
    user_preferences=user_preferences
)
```

## 🧪 Testing

### Manual Testing

```bash
# Start the server
python server.py

# In another terminal, test endpoints
curl http://localhost:8002/health

# Create thread
curl -X POST http://localhost:8002/api/threads \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "event_discovery"}'

# Invoke agent
curl -X POST http://localhost:8002/api/agents/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find jazz concerts in SF",
    "user_preferences": {"location": "San Francisco"}
  }'
```

## 📊 Monitoring & Logging

All components use Python logging:

```python
# Configure logging level
logging.basicConfig(level=logging.INFO)

# Logs include:
# - Agent invocations
# - Tool calls
# - State updates
# - API requests
# - Errors and exceptions
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EMERGENT_LLM_KEY` | Universal LLM API key | Required |
| `DEFAULT_MODEL` | Default LLM model | `gpt-4o-mini` |
| `DEFAULT_PROVIDER` | Default LLM provider | `openai` |
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DB_NAME` | Database name | `agentic_backend` |
| `MAIN_BACKEND_URL` | Main backend URL | `http://localhost:8001` |
| `AGENTIC_SERVER_PORT` | Server port | `8002` |
| `MAX_TOKENS_PER_THREAD` | Max tokens before summarization | `8000` |
| `SUMMARIZATION_THRESHOLD` | Token count to trigger summary | `6000` |

## 🚀 Deployment

### Using Supervisor

Add to supervisor configuration:

```ini
[program:agentic_backend]
directory=/app/agentic_backend
command=python server.py
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/agentic_backend.err.log
stdout_logfile=/var/log/supervisor/agentic_backend.out.log
```

Then:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start agentic_backend
```

## 📝 Development

### Adding New Agents

1. Create agent class in `agents/`:
```python
from .base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type="custom",
            system_message="Custom agent prompt",
            tools=custom_tools
        )
```

2. Register in `agents/__init__.py`

3. Add endpoint in `server.py`

### Adding New Tools

1. Create tool in `tools/`:
```python
from langchain_core.tools import tool

@tool
async def my_custom_tool(param: str) -> Dict:
    \"\"\"Tool description.\"\"\"
    # Implementation
    return result
```

2. Add to tool list

3. Use in agent initialization

## 🤝 Integration with Main Backend

The agentic backend communicates with the main backend (port 8001) via:

1. **Direct API Client**: For programmatic access
2. **API Gateway**: For proxying requests with cookies
3. **Event Tools**: For event-specific operations

## 📖 Additional Resources

- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph)
- [MongoDB Checkpointing](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [Emergent Integrations](https://emergent.ai/docs)

## 🐛 Troubleshooting

### MongoDB Connection Issues
```bash
# Check MongoDB is running
mongosh --eval "db.version()"

# Check connection string in .env
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Conflicts
```bash
# Change port in .env
AGENTIC_SERVER_PORT=8003
```

## 📄 License

MIT License - See LICENSE file for details

## 👥 Support

For issues and questions:
- Check logs: `/var/log/supervisor/agentic_backend.*.log`
- Review API documentation above
- Test with health check endpoint

---

Built with ❤️ using LangGraph, MongoDB, and FastAPI
