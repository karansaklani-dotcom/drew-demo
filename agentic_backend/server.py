"""FastAPI server for agentic backend."""

import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json

from config import config
from agents import EventDiscoveryAgent
from agents.sub_agent import create_sub_agent
from threads.manager import ThreadManager
from threads.models import Thread, Message, ThreadSearchQuery, MessageType
from api.gateway import get_api_gateway
from api.client import get_main_backend_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global instances
thread_manager: Optional[ThreadManager] = None
event_agent: Optional[EventDiscoveryAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    global thread_manager, event_agent
    
    # Startup
    logger.info("Initializing agentic backend...")
    
    try:
        # Initialize thread manager
        thread_manager = ThreadManager()
        await thread_manager.initialize()
        logger.info("Thread manager initialized")
        
        # Initialize event discovery agent
        event_agent = EventDiscoveryAgent()
        await event_agent.initialize()
        logger.info("Event discovery agent initialized")
        
        logger.info("Agentic backend initialized successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down agentic backend...")
    
    if thread_manager:
        await thread_manager.close()
    
    logger.info("Agentic backend shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="Agentic Backend API",
    description="LangGraph-based agentic backend with checkpointing and thread management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class AgentInvokeRequest(BaseModel):
    """Request model for agent invocation."""
    message: str
    thread_id: Optional[str] = None
    user_id: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None
    stream: bool = False


class AgentInvokeResponse(BaseModel):
    """Response model for agent invocation."""
    response: str
    thread_id: str
    messages: Optional[List[Dict]] = None


class CreateThreadRequest(BaseModel):
    """Request model for creating a thread."""
    user_id: Optional[str] = None
    agent_type: str = "base"
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AddMessageRequest(BaseModel):
    """Request model for adding a message."""
    thread_id: str
    role: MessageType
    content: str
    parent_message_id: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    metadata: Optional[Dict[str, Any]] = None


class SubAgentRequest(BaseModel):
    """Request model for sub-agent execution."""
    parent_thread_id: str
    agent_type: str
    task_description: str
    system_message: Optional[str] = None
    parent_message_id: Optional[str] = None


class EventDiscoveryRequest(BaseModel):
    """Request model for event discovery."""
    message: str
    thread_id: Optional[str] = None
    user_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


# Health check
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Agentic Backend",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "thread_manager": thread_manager is not None,
            "event_agent": event_agent is not None
        }
    }


# Thread Management Endpoints
@app.post("/api/threads", response_model=Thread)
async def create_thread(request: CreateThreadRequest):
    """Create a new thread."""
    try:
        thread = await thread_manager.create_thread(
            user_id=request.user_id,
            agent_type=request.agent_type,
            title=request.title,
            metadata=request.metadata
        )
        return thread
    except Exception as e:
        logger.error(f"Error creating thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/threads/{thread_id}", response_model=Thread)
async def get_thread(thread_id: str):
    """Get a thread by ID."""
    try:
        thread = await thread_manager.get_thread(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        return thread
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/threads/{thread_id}/messages", response_model=List[Message])
async def get_thread_messages(
    thread_id: str,
    limit: Optional[int] = None,
    skip: int = 0
):
    """Get messages from a thread."""
    try:
        messages = await thread_manager.get_messages(
            thread_id=thread_id,
            limit=limit,
            skip=skip
        )
        return messages
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/threads/messages", response_model=Message)
async def add_message(request: AddMessageRequest):
    """Add a message to a thread."""
    try:
        message = await thread_manager.add_message(
            thread_id=request.thread_id,
            role=request.role,
            content=request.content,
            parent_message_id=request.parent_message_id,
            tool_calls=request.tool_calls,
            metadata=request.metadata
        )
        return message
    except Exception as e:
        logger.error(f"Error adding message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/threads/search")
async def search_messages(query: ThreadSearchQuery):
    """Perform semantic search on messages."""
    try:
        results = await thread_manager.semantic_search(query)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/threads/{thread_id}/context")
async def get_thread_context(thread_id: str, recent_message_count: int = 10):
    """Get context for a thread including summaries."""
    try:
        context = await thread_manager.get_context_for_agent(
            thread_id=thread_id,
            recent_message_count=recent_message_count
        )
        return {"context": context}
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/threads/{thread_id}/summaries")
async def get_thread_summaries(thread_id: str):
    """Get all summaries for a thread."""
    try:
        summaries = await thread_manager.get_thread_summaries(thread_id)
        return {"summaries": summaries}
    except Exception as e:
        logger.error(f"Error getting summaries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Agent Endpoints
@app.post("/api/agents/invoke")
async def invoke_agent(request: AgentInvokeRequest):
    """Invoke an agent with a message."""
    try:
        # Use event agent as default
        agent = event_agent
        
        # Create thread if not provided
        thread_id = request.thread_id
        if not thread_id:
            thread = await thread_manager.create_thread(
                user_id=request.user_id,
                agent_type="event_discovery"
            )
            thread_id = thread.id
        
        # Invoke agent
        if request.stream:
            # Return streaming response
            async def generate():
                async for chunk in agent.stream(
                    message=request.message,
                    thread_id=thread_id,
                    user_preferences=request.user_preferences
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream"
            )
        else:
            # Regular response
            result = await agent.invoke(
                message=request.message,
                thread_id=thread_id,
                user_preferences=request.user_preferences
            )
            
            return AgentInvokeResponse(
                response=result.get('response', ''),
                thread_id=thread_id,
                messages=result.get('messages')
            )
            
    except Exception as e:
        logger.error(f"Error invoking agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/event-discovery")
async def discover_events(request: EventDiscoveryRequest):
    """Discover events using the event discovery agent."""
    try:
        # Create thread if not provided
        thread_id = request.thread_id
        if not thread_id:
            thread = await thread_manager.create_thread(
                user_id=request.user_id,
                agent_type="event_discovery"
            )
            thread_id = thread.id
        
        # Discover events
        result = await event_agent.discover_events(
            user_message=request.message,
            thread_id=thread_id,
            user_preferences=request.preferences
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error discovering events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/sub-agent")
async def execute_sub_agent(request: SubAgentRequest):
    """Execute a sub-agent for a specific task."""
    try:
        # Create and initialize sub-agent
        sub_agent = await create_sub_agent(
            agent_type=request.agent_type,
            parent_thread_id=request.parent_thread_id,
            system_message=request.system_message
        )
        
        # Execute subtask
        result = await sub_agent.execute_subtask(
            task_description=request.task_description,
            parent_message_id=request.parent_message_id
        )
        
        # Merge context back to parent
        await sub_agent.merge_context_to_parent()
        
        return result
        
    except Exception as e:
        logger.error(f"Error executing sub-agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{thread_id}/state")
async def get_agent_state(thread_id: str):
    """Get the current state for an agent thread."""
    try:
        state = await event_agent.get_state(thread_id)
        return {"state": state}
    except Exception as e:
        logger.error(f"Error getting agent state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# API Gateway Endpoints
@app.api_route("/gateway/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def api_gateway(request: Request, path: str):
    """Gateway endpoint for proxying requests to main backend."""
    try:
        gateway = get_api_gateway()
        
        # Get request body if present
        json_data = None
        if request.method in ["POST", "PUT"]:
            try:
                json_data = await request.json()
            except:
                pass
        
        # Forward the request
        response = await gateway.forward_request(
            request=request,
            path=f"/{path}",
            method=request.method,
            json_data=json_data
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in API gateway: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Utility Endpoints
@app.get("/api/main-backend/events")
async def proxy_get_events(
    location: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Proxy endpoint to get events from main backend."""
    try:
        client = get_main_backend_client()
        result = await client.get_events(
            location=location,
            category=category,
            search=search
        )
        return result
    except Exception as e:
        logger.error(f"Error proxying events request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/main-backend/events/{event_id}")
async def proxy_get_event_details(event_id: str):
    """Proxy endpoint to get event details from main backend."""
    try:
        client = get_main_backend_client()
        result = await client.get_event_details(event_id)
        return result
    except Exception as e:
        logger.error(f"Error proxying event details request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.server.host,
        port=config.server.port,
        log_level="info"
    )
