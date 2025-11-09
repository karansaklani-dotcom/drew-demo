"""Thread management with MongoDB persistence and embeddings."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import numpy as np
from openai import AsyncOpenAI

from config import config
from .models import Thread, Message, MessageType, Summary, ThreadSearchQuery
from .summarizer import ThreadSummarizer

logger = logging.getLogger(__name__)


class ThreadManager:
    """Manages threads, messages, and embeddings for semantic search."""
    
    def __init__(self, mongo_url: Optional[str] = None, db_name: Optional[str] = None):
        self.mongo_url = mongo_url or config.mongodb.url
        self.db_name = db_name or config.mongodb.db_name
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        
        # Collections
        self.threads = self.db[config.mongodb.threads_collection]
        self.messages = self.db[config.mongodb.messages_collection]
        self.summaries = self.db[config.mongodb.summaries_collection]
        
        # Embedding client
        self.embedding_client = AsyncOpenAI(api_key=config.llm.api_key)
        self.embedding_model = config.llm.embedding_model
        
        # Summarizer
        self.summarizer = ThreadSummarizer()
        
    async def initialize(self):
        """Initialize the thread manager and setup indexes."""
        try:
            # Create indexes for threads
            await self.threads.create_index("id", unique=True)
            await self.threads.create_index("user_id")
            await self.threads.create_index("parent_thread_id")
            await self.threads.create_index([("created_at", -1)])
            
            # Create indexes for messages
            await self.messages.create_index("id", unique=True)
            await self.messages.create_index("thread_id")
            await self.messages.create_index("parent_message_id")
            await self.messages.create_index([("thread_id", 1), ("created_at", 1)])
            
            # Create vector search index for embeddings (if using Atlas)
            # Note: This requires MongoDB Atlas with vector search enabled
            # await self._create_vector_index()
            
            # Create indexes for summaries
            await self.summaries.create_index("id", unique=True)
            await self.summaries.create_index("thread_id")
            await self.summaries.create_index([("thread_id", 1), ("created_at", -1)])
            
            logger.info("Thread manager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing thread manager: {e}")
            raise
    
    async def create_thread(
        self,
        user_id: Optional[str] = None,
        agent_type: str = "base",
        parent_thread_id: Optional[str] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Thread:
        """Create a new thread."""
        thread = Thread(
            user_id=user_id,
            agent_type=agent_type,
            parent_thread_id=parent_thread_id,
            title=title,
            is_subthread=parent_thread_id is not None,
            metadata=metadata or {}
        )
        
        await self.threads.insert_one(thread.dict())
        logger.info(f"Created thread: {thread.id}")
        return thread
    
    async def get_thread(self, thread_id: str) -> Optional[Thread]:
        """Get a thread by ID."""
        doc = await self.threads.find_one({"id": thread_id})
        if doc:
            doc.pop('_id', None)
            return Thread(**doc)
        return None
    
    async def update_thread(self, thread_id: str, updates: Dict[str, Any]) -> bool:
        """Update thread metadata."""
        updates['updated_at'] = datetime.utcnow()
        result = await self.threads.update_one(
            {"id": thread_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def add_message(
        self,
        thread_id: str,
        role: MessageType,
        content: str,
        parent_message_id: Optional[str] = None,
        tool_calls: Optional[List[Dict]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        generate_embedding: bool = True
    ) -> Message:
        """Add a message to a thread."""
        from .models import ToolCall
        
        # Create message
        message = Message(
            thread_id=thread_id,
            parent_message_id=parent_message_id,
            role=role,
            content=content,
            tool_calls=[ToolCall(**tc) for tc in (tool_calls or [])],
            metadata=metadata or {},
            token_count=self.summarizer.count_tokens(content)
        )
        
        # Generate embedding if requested
        if generate_embedding and content:
            try:
                message.embedding = await self._generate_embedding(content)
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
        
        # Save message
        await self.messages.insert_one(message.dict())
        
        # Update thread statistics
        await self.threads.update_one(
            {"id": thread_id},
            {
                "$inc": {
                    "message_count": 1,
                    "total_token_count": message.token_count or 0
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        # Check if summarization is needed
        await self._check_and_summarize(thread_id)
        
        logger.info(f"Added message to thread {thread_id}")
        return message
    
    async def get_messages(
        self,
        thread_id: str,
        limit: Optional[int] = None,
        skip: int = 0,
        include_subthread_messages: bool = False
    ) -> List[Message]:
        """Get messages from a thread."""
        query = {"thread_id": thread_id}
        
        # Optionally exclude subthread messages
        if not include_subthread_messages:
            query["parent_message_id"] = None
        
        cursor = self.messages.find(query).sort("created_at", 1).skip(skip)
        
        if limit:
            cursor = cursor.limit(limit)
        
        docs = await cursor.to_list(length=None)
        messages = []
        for doc in docs:
            doc.pop('_id', None)
            messages.append(Message(**doc))
        
        return messages
    
    async def get_recent_messages(self, thread_id: str, count: int = 10) -> List[Message]:
        """Get the most recent messages from a thread."""
        cursor = self.messages.find(
            {"thread_id": thread_id}
        ).sort("created_at", -1).limit(count)
        
        docs = await cursor.to_list(length=count)
        messages = []
        for doc in reversed(docs):  # Reverse to get chronological order
            doc.pop('_id', None)
            messages.append(Message(**doc))
        
        return messages
    
    async def semantic_search(
        self,
        query: ThreadSearchQuery
    ) -> List[Dict[str, Any]]:
        """Perform semantic search on messages using embeddings."""
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query.query)
            
            # Build search query
            match_query: Dict[str, Any] = {}
            if query.thread_id:
                match_query["thread_id"] = query.thread_id
            if query.filter_metadata:
                for key, value in query.filter_metadata.items():
                    match_query[f"metadata.{key}"] = value
            
            # Find all messages matching the filter
            cursor = self.messages.find(match_query)
            docs = await cursor.to_list(length=None)
            
            # Calculate cosine similarity for each message
            results = []
            for doc in docs:
                if doc.get('embedding'):
                    similarity = self._cosine_similarity(
                        query_embedding,
                        doc['embedding']
                    )
                    
                    if similarity >= query.similarity_threshold:
                        doc.pop('_id', None)
                        doc['similarity_score'] = similarity
                        results.append(doc)
            
            # Sort by similarity
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Return top results
            return results[:query.limit]
            
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            return []
    
    async def get_thread_summaries(self, thread_id: str) -> List[Summary]:
        """Get all summaries for a thread."""
        cursor = self.summaries.find(
            {"thread_id": thread_id}
        ).sort("created_at", 1)
        
        docs = await cursor.to_list(length=None)
        summaries = []
        for doc in docs:
            doc.pop('_id', None)
            summaries.append(Summary(**doc))
        
        return summaries
    
    async def get_context_for_agent(
        self,
        thread_id: str,
        recent_message_count: int = 10
    ) -> str:
        """Get context for agent including summaries and recent messages."""
        # Get summaries
        summaries = await self.get_thread_summaries(thread_id)
        
        # Get recent messages
        recent_messages = await self.get_recent_messages(thread_id, recent_message_count)
        
        # Build context
        context = await self.summarizer.get_context_with_summaries(
            summaries,
            recent_messages
        )
        
        return context
    
    async def _check_and_summarize(self, thread_id: str):
        """Check if thread needs summarization and create summary if needed."""
        try:
            # Get thread
            thread = await self.get_thread(thread_id)
            if not thread:
                return
            
            # Check if we need to summarize
            if thread.total_token_count < config.thread.summarization_threshold:
                return
            
            # Get messages since last summary
            summaries = await self.get_thread_summaries(thread_id)
            
            # Determine which messages to summarize
            if summaries:
                last_summary = summaries[-1]
                # Get messages after last summary
                messages = await self.messages.find(
                    {
                        "thread_id": thread_id,
                        "created_at": {"$gt": last_summary.created_at}
                    }
                ).sort("created_at", 1).to_list(length=None)
            else:
                # Get all messages
                messages = await self.get_messages(thread_id)
            
            if not messages:
                return
            
            # Convert to Message objects
            message_objs = []
            for doc in messages:
                doc.pop('_id', None)
                message_objs.append(Message(**doc))
            
            # Check if we should summarize
            if not self.summarizer.should_summarize(message_objs):
                return
            
            # Create summary
            summary = await self.summarizer.summarize_messages(
                message_objs,
                thread_id
            )
            
            # Save summary
            await self.summaries.insert_one(summary.dict())
            
            # Update thread
            await self.threads.update_one(
                {"id": thread_id},
                {
                    "$inc": {"summary_count": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            logger.info(f"Created summary for thread {thread_id}")
            
        except Exception as e:
            logger.error(f"Error in check_and_summarize: {e}")
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        try:
            response = await self.embedding_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    async def close(self):
        """Close the MongoDB connection."""
        self.client.close()
        logger.info("Thread manager connection closed")
