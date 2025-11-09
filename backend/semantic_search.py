"""
Semantic Search Service for Drew Backend
Handles embeddings generation and vector similarity search
"""
import os
from typing import List, Dict, Any, Optional
import logging
from openai import OpenAI
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class SemanticSearchService:
    """Service for generating embeddings and performing semantic search"""
    
    def __init__(self, openai_api_key: str, mongo_client: AsyncIOMotorClient, db_name: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.mongo_client = mongo_client
        self.db = mongo_client[db_name]
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimensions = 1536
        
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for given text"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    async def generate_activity_embedding_text(self, activity: Dict[str, Any]) -> str:
        """Generate searchable text from activity data"""
        parts = []
        
        # Title and descriptions
        if activity.get('title'):
            parts.append(f"Title: {activity['title']}")
        if activity.get('shortDescription'):
            parts.append(f"Description: {activity['shortDescription']}")
        if activity.get('longDescription'):
            parts.append(f"Details: {activity['longDescription']}")
        
        # Location
        if activity.get('city') and activity.get('state'):
            parts.append(f"Location: {activity['city']}, {activity['state']}")
        elif activity.get('location'):
            parts.append(f"Location: {activity['location']}")
        
        # Category
        if activity.get('category'):
            parts.append(f"Category: {activity['category']}")
        
        # Host
        if activity.get('host'):
            host = activity['host']
            if host.get('name'):
                parts.append(f"Host: {host['name']}")
            if host.get('title'):
                parts.append(f"Host title: {host['title']}")
        
        # Offerings
        if activity.get('offerings'):
            offering_texts = []
            for offering in activity['offerings']:
                if isinstance(offering, dict):
                    if offering.get('shortDescription'):
                        offering_texts.append(offering['shortDescription'])
                    if offering.get('longDescription'):
                        offering_texts.append(offering['longDescription'])
            if offering_texts:
                parts.append(f"Includes: {', '.join(offering_texts)}")
        
        # Prerequisites
        if activity.get('preRequisites'):
            prereq_texts = []
            for prereq in activity['preRequisites']:
                if isinstance(prereq, dict) and prereq.get('name'):
                    prereq_texts.append(prereq['name'])
            if prereq_texts:
                parts.append(f"Requirements: {', '.join(prereq_texts)}")
        
        # Participants
        if activity.get('minParticipants') or activity.get('maxParticipants'):
            min_p = activity.get('minParticipants', 0)
            max_p = activity.get('maxParticipants', 0)
            if min_p and max_p:
                parts.append(f"Participants: {min_p}-{max_p} people")
            elif max_p:
                parts.append(f"Up to {max_p} participants")
        
        # Duration
        if activity.get('preferredDuration'):
            duration_hours = activity['preferredDuration'] / 60
            parts.append(f"Duration: {duration_hours:.1f} hours")
        
        return " | ".join(parts)
    
    async def update_activity_embedding(self, activity_id: str, activity: Dict[str, Any]):
        """Generate and store embedding for an activity"""
        embedding_text = await self.generate_activity_embedding_text(activity)
        embedding = await self.generate_embedding(embedding_text)
        
        if embedding:
            await self.db.activities.update_one(
                {"_id": activity_id},
                {"$set": {
                    "embedding": embedding,
                    "embeddingText": embedding_text,
                    "updatedAt": activity.get('updatedAt')
                }}
            )
            logger.info(f"Updated embedding for activity {activity_id}")
        
    async def semantic_search_activities(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search on activities using vector similarity
        Returns activities sorted by relevance
        """
        # Generate query embedding
        query_embedding = await self.generate_embedding(query)
        
        if not query_embedding:
            logger.warning("Failed to generate query embedding, falling back to text search")
            return await self._fallback_text_search(query, limit, filters)
        
        # Build aggregation pipeline
        pipeline = []
        
        # Add filters if provided
        if filters:
            pipeline.append({"$match": filters})
        
        # Vector search using $vectorSearch (if MongoDB Atlas)
        # Or cosine similarity calculation for local MongoDB
        pipeline.extend([
            {
                "$addFields": {
                    "similarity": {
                        "$let": {
                            "vars": {
                                "dotProduct": {
                                    "$reduce": {
                                        "input": {"$range": [0, len(query_embedding)]},
                                        "initialValue": 0,
                                        "in": {
                                            "$add": [
                                                "$$value",
                                                {
                                                    "$multiply": [
                                                        {"$arrayElemAt": ["$embedding", "$$this"]},
                                                        query_embedding["$$this"]
                                                    ]
                                                }
                                            ]
                                        }
                                    }
                                }
                            },
                            "in": "$$dotProduct"
                        }
                    }
                }
            },
            {"$sort": {"similarity": -1}},
            {"$limit": limit}
        ])
        
        try:
            results = await self.db.activities.aggregate(pipeline).to_list(limit)
            return results
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            # Fallback to text search
            return await self._fallback_text_search(query, limit, filters)
    
    async def _fallback_text_search(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Fallback to text-based search if semantic search fails"""
        search_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"shortDescription": {"$regex": query, "$options": "i"}},
                {"longDescription": {"$regex": query, "$options": "i"}},
                {"category": {"$regex": query, "$options": "i"}},
                {"city": {"$regex": query, "$options": "i"}},
            ]
        }
        
        if filters:
            search_query = {"$and": [search_query, filters]}
        
        cursor = self.db.activities.find(search_query).limit(limit)
        return await cursor.to_list(limit)
    
    async def ensure_indexes(self):
        """Create necessary indexes for semantic search"""
        # Create index on embedding field for faster similarity search
        await self.db.activities.create_index([("embedding", 1)])
        
        # Create text index for fallback search
        try:
            await self.db.activities.create_index([
                ("title", "text"),
                ("shortDescription", "text"),
                ("longDescription", "text"),
                ("category", "text")
            ])
        except Exception as e:
            logger.warning(f"Text index might already exist: {e}")
        
        logger.info("Semantic search indexes ensured")
    
    async def batch_generate_embeddings(self, collection_name: str = "activities"):
        """Generate embeddings for all activities that don't have them"""
        collection = self.db[collection_name]
        
        # Find documents without embeddings
        cursor = collection.find({"embedding": {"$exists": False}})
        count = 0
        
        async for doc in cursor:
            try:
                activity_id = doc['_id']
                await self.update_activity_embedding(activity_id, doc)
                count += 1
            except Exception as e:
                logger.error(f"Error generating embedding for {doc.get('_id')}: {e}")
        
        logger.info(f"Generated embeddings for {count} activities")
        return count
