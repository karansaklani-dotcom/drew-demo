"""MongoDB checkpointer for LangGraph state persistence."""

import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from config import config

logger = logging.getLogger(__name__)


class MongoDBCheckpointer:
    """Enhanced MongoDB checkpointer with custom features."""
    
    def __init__(self, mongo_url: Optional[str] = None, db_name: Optional[str] = None):
        self.mongo_url = mongo_url or config.mongodb.url
        self.db_name = db_name or config.mongodb.db_name
        self._checkpointer: Optional[AsyncMongoDBSaver] = None
        self._client: Optional[AsyncIOMotorClient] = None
        
    async def initialize(self) -> AsyncMongoDBSaver:
        """Initialize the MongoDB checkpointer."""
        if self._checkpointer is None:
            try:
                logger.info(f"Initializing MongoDB checkpointer: {self.mongo_url}/{self.db_name}")
                
                # Create MongoDB client and database
                self._client = AsyncIOMotorClient(self.mongo_url)
                db = self._client[self.db_name]
                
                # Create AsyncMongoDBSaver with database instance
                # Note: We use the async connection directly
                self._checkpointer = AsyncMongoDBSaver(self._client, self.db_name)
                
                # Setup indexes for better performance
                await self._setup_indexes()
                
                logger.info("MongoDB checkpointer initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize MongoDB checkpointer: {e}")
                raise
                
        return self._checkpointer
    
    async def _setup_indexes(self):
        """Setup MongoDB indexes for optimal performance."""
        try:
            db = self._client[self.db_name]
            checkpoints_collection = db[config.mongodb.checkpoints_collection]
            
            # Index on thread_id for fast lookups
            await checkpoints_collection.create_index("thread_id")
            
            # Index on checkpoint_id
            await checkpoints_collection.create_index("checkpoint_id")
            
            # Compound index for thread and timestamp
            await checkpoints_collection.create_index([("thread_id", 1), ("checkpoint_ns", 1)])
            
            logger.info("Checkpoint indexes created successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    async def get_thread_history(self, thread_id: str, limit: int = 10):
        """Get checkpoint history for a thread."""
        try:
            db = self._client[self.db_name]
            checkpoints = db[config.mongodb.checkpoints_collection]
            
            cursor = checkpoints.find(
                {"thread_id": thread_id}
            ).sort("checkpoint_ns", -1).limit(limit)
            
            history = await cursor.to_list(length=limit)
            return history
        except Exception as e:
            logger.error(f"Error getting thread history: {e}")
            return []
    
    async def cleanup_old_checkpoints(self, thread_id: str, keep_last: int = 50):
        """Cleanup old checkpoints to save space."""
        try:
            db = self._client[self.db_name]
            checkpoints = db[config.mongodb.checkpoints_collection]
            
            # Get all checkpoints for thread
            all_checkpoints = await checkpoints.find(
                {"thread_id": thread_id}
            ).sort("checkpoint_ns", -1).to_list(None)
            
            # Keep only the last N checkpoints
            if len(all_checkpoints) > keep_last:
                checkpoints_to_delete = all_checkpoints[keep_last:]
                ids_to_delete = [cp["_id"] for cp in checkpoints_to_delete]
                
                result = await checkpoints.delete_many({"_id": {"$in": ids_to_delete}})
                logger.info(f"Cleaned up {result.deleted_count} old checkpoints for thread {thread_id}")
                
        except Exception as e:
            logger.error(f"Error cleaning up checkpoints: {e}")
    
    async def close(self):
        """Close the MongoDB connection."""
        if self._client:
            self._client.close()
            logger.info("MongoDB checkpointer connection closed")


# Global checkpointer instance
_checkpointer_instance: Optional[MongoDBCheckpointer] = None


async def get_checkpointer() -> AsyncMongoDBSaver:
    """Get or create the global checkpointer instance."""
    global _checkpointer_instance
    
    if _checkpointer_instance is None:
        _checkpointer_instance = MongoDBCheckpointer()
    
    return await _checkpointer_instance.initialize()
