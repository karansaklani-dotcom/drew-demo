"""Configuration management for agentic backend."""

import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


class LLMConfig(BaseModel):
    """LLM configuration."""
    api_key: str = Field(default_factory=lambda: os.getenv('EMERGENT_LLM_KEY', ''))
    default_model: str = Field(default_factory=lambda: os.getenv('DEFAULT_MODEL', 'gpt-4o-mini'))
    default_provider: str = Field(default_factory=lambda: os.getenv('DEFAULT_PROVIDER', 'openai'))
    embedding_model: str = Field(default_factory=lambda: os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small'))
    embedding_dimensions: int = Field(default_factory=lambda: int(os.getenv('EMBEDDING_DIMENSIONS', '1536')))


class MongoDBConfig(BaseModel):
    """MongoDB configuration."""
    url: str = Field(default_factory=lambda: os.getenv('MONGO_URL', 'mongodb://localhost:27017'))
    db_name: str = Field(default_factory=lambda: os.getenv('DB_NAME', 'agentic_backend'))
    
    # Collection names
    checkpoints_collection: str = 'checkpoints'
    threads_collection: str = 'threads'
    messages_collection: str = 'messages'
    summaries_collection: str = 'summaries'


class MainBackendConfig(BaseModel):
    """Main backend API configuration."""
    base_url: str = Field(default_factory=lambda: os.getenv('MAIN_BACKEND_URL', 'http://localhost:8001'))
    api_prefix: str = Field(default_factory=lambda: os.getenv('MAIN_BACKEND_API_PREFIX', '/api'))
    
    @property
    def full_url(self) -> str:
        """Get full API URL."""
        return f"{self.base_url}{self.api_prefix}"


class ServerConfig(BaseModel):
    """Server configuration."""
    host: str = Field(default_factory=lambda: os.getenv('AGENTIC_SERVER_HOST', '0.0.0.0'))
    port: int = Field(default_factory=lambda: int(os.getenv('AGENTIC_SERVER_PORT', '8002')))


class ThreadConfig(BaseModel):
    """Thread management configuration."""
    max_tokens_per_thread: int = Field(default_factory=lambda: int(os.getenv('MAX_TOKENS_PER_THREAD', '8000')))
    summarization_threshold: int = Field(default_factory=lambda: int(os.getenv('SUMMARIZATION_THRESHOLD', '6000')))
    max_messages_per_thread: int = Field(default_factory=lambda: int(os.getenv('MAX_MESSAGES_PER_THREAD', '100')))


class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.llm = LLMConfig()
        self.mongodb = MongoDBConfig()
        self.main_backend = MainBackendConfig()
        self.server = ServerConfig()
        self.thread = ThreadConfig()


# Global configuration instance
config = Config()
