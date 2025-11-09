"""Data models for thread management."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class MessageType(str, Enum):
    """Message type enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    FUNCTION = "function"


class ToolCall(BaseModel):
    """Tool call information."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    status: str = "pending"  # pending, success, error
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class Message(BaseModel):
    """Message in a thread."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str
    parent_message_id: Optional[str] = None  # For sub-agent messages
    role: MessageType
    content: str
    tool_calls: List[ToolCall] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Embeddings for semantic search
    embedding: Optional[List[float]] = None
    
    # Token tracking
    token_count: Optional[int] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Summary(BaseModel):
    """Thread summary."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str
    summary_text: str
    message_count: int
    token_count: int
    start_message_id: str
    end_message_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Thread(BaseModel):
    """Thread for conversation management."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    parent_thread_id: Optional[str] = None  # For sub-agent threads
    
    # Thread metadata
    title: Optional[str] = None
    description: Optional[str] = None
    
    # Agent information
    agent_type: str = "base"  # base, event_discovery, etc.
    
    # State tracking
    is_active: bool = True
    is_subthread: bool = False
    
    # Statistics
    message_count: int = 0
    total_token_count: int = 0
    summary_count: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ThreadSearchQuery(BaseModel):
    """Query for semantic search in threads."""
    query: str
    thread_id: Optional[str] = None
    limit: int = 10
    similarity_threshold: float = 0.7
    filter_metadata: Optional[Dict[str, Any]] = None
