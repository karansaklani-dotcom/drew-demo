"""
Tools for Drew AI Agents
Provides functionality for recommendation, itinerary building, and offerings management
"""
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import logging

from semantic_search import SemanticSearchService

logger = logging.getLogger(__name__)

class AgentTools:
    """Collection of tools for AI agents"""
    
    def __init__(self, semantic_search_service: SemanticSearchService, db):
        self.semantic_search = semantic_search_service
        self.db = db
    
    # =========================================================================
    # RECOMMENDATION AGENT TOOLS
    # =========================================================================
    
    async def search_activities(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search activities using semantic search
        
        Args:
            query: Natural language search query
            filters: Optional filters (location, category, price, etc.)
            limit: Max number of results
            
        Returns:
            List of activity documents with similarity scores
        """
        try:
            results = await self.semantic_search.semantic_search_activities(
                query=query,
                limit=limit,
                filters=filters
            )
            
            logger.info(f"Found {len(results)} activities for query: {query}")
            return results
        
        except Exception as e:
            logger.error(f"Error searching activities: {e}")
            return []
    
    async def create_recommendation(
        self,
        project_id: str,
        user_id: str,
        activity: Dict[str, Any],
        reason_to_recommend: str,
        score: float = 0.0,
        customized_title: Optional[str] = None,
        customized_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create or update a recommendation for a project
        Acts as upsert - if recommendation for this activity exists, update it
        
        Args:
            project_id: Project ID
            user_id: User ID
            activity: Full activity document
            reason_to_recommend: Why this activity is recommended
            score: Recommendation score (0-1)
            customized_title: Optional customized title for the user's use case
            customized_description: Optional customized description for the user's use case
            
        Returns:
            Created/updated recommendation document
        """
        try:
            activity_id = str(activity.get('_id'))
            
            # Check if recommendation already exists
            existing = await self.db.recommendations.find_one({
                "projectId": project_id,
                "activityId": activity_id,
                "userId": user_id
            })
            
            # Prepare recommendation data
            rec_data = {
                "activityId": activity_id,
                "projectId": project_id,
                "userId": user_id,
                "title": activity.get('title'),
                "shortDescription": activity.get('shortDescription', activity.get('description', '')),
                "longDescription": activity.get('longDescription', ''),
                "thumbnailUrl": activity.get('thumbnailUrl'),
                "itinerary": activity.get('itineraries', []),
                "preRequisiteIds": activity.get('offerings', [])[:3],  # First 3 prerequisites
                "offeringIds": activity.get('offerings', [])[:3],  # First 3 offerings
                "reasonToRecommend": reason_to_recommend,
                "duration": activity.get('preferredDuration'),
                "score": score
            }
            
            if existing:
                # Update existing recommendation
                rec_data["updatedAt"] = activity.get('updatedAt')
                await self.db.recommendations.update_one(
                    {"_id": existing['_id']},
                    {"$set": rec_data}
                )
                rec_id = str(existing['_id'])
                logger.info(f"Updated recommendation {rec_id}")
            else:
                # Create new recommendation
                rec_data["createdAt"] = activity.get('createdAt')
                rec_data["updatedAt"] = activity.get('updatedAt')
                result = await self.db.recommendations.insert_one(rec_data)
                rec_id = str(result.inserted_id)
                
                # Add to project's recommendation list
                await self.db.projects.update_one(
                    {"_id": ObjectId(project_id)},
                    {"$addToSet": {"recommendationIds": rec_id}}
                )
                logger.info(f"Created recommendation {rec_id}")
            
            rec_data['_id'] = rec_id
            rec_data['id'] = rec_id
            return rec_data
        
        except Exception as e:
            logger.error(f"Error creating recommendation: {e}")
            raise
    
    async def reflect_and_transform(
        self,
        activity: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Reflect on whether activity fits user needs and transform data
        
        Args:
            activity: Activity document
            user_context: User requirements and preferences
            
        Returns:
            Transformed activity with reflection metadata
        """
        # This is a synchronous transformation
        # In a full implementation, this could call an LLM for deep reflection
        
        reflection = {
            "isFit": True,
            "matchedCriteria": [],
            "concerns": [],
            "score": 0.8
        }
        
        # Check participants
        if user_context.get('groupSize'):
            try:
                group_size = int(user_context['groupSize'])
                min_participants = int(activity.get('minParticipants', 0))
                max_participants = int(activity.get('maxParticipants', 999))
                
                if min_participants <= group_size <= max_participants:
                    reflection["matchedCriteria"].append(f"Suitable for {group_size} participants")
                    reflection["score"] += 0.1
                else:
                    reflection["concerns"].append(f"Activity designed for {min_participants}-{max_participants} people")
                    reflection["score"] -= 0.2
            except (ValueError, TypeError):
                # Skip if conversion fails
                pass
        
        # Check location
        if user_context.get('preferredLocation'):
            if user_context['preferredLocation'].lower() in activity.get('city', '').lower():
                reflection["matchedCriteria"].append("In preferred location")
                reflection["score"] += 0.1
        
        # Check budget
        if user_context.get('budget'):
            try:
                budget = float(user_context['budget'])
                price = float(activity.get('price', 0))
                
                if price <= budget:
                    reflection["matchedCriteria"].append("Within budget")
                    reflection["score"] += 0.1
                else:
                    reflection["concerns"].append(f"Price ${price} exceeds budget")
                    reflection["score"] -= 0.2
            except (ValueError, TypeError):
                # Skip if conversion fails
                pass
        
        reflection["score"] = max(0, min(1, reflection["score"]))
        
        return {
            "activity": activity,
            "reflection": reflection
        }
    
    # =========================================================================
    # ITINERARY BUILDER AGENT TOOLS
    # =========================================================================
    
    async def retrieve_recommendation_details(
        self,
        recommendation_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Retrieve full recommendation details including activity and itinerary
        
        Args:
            recommendation_id: Recommendation ID
            user_id: User ID for authorization
            
        Returns:
            Full recommendation with activity details
        """
        try:
            if not ObjectId.is_valid(recommendation_id):
                raise ValueError("Invalid recommendation ID")
            
            rec = await self.db.recommendations.find_one({
                "_id": ObjectId(recommendation_id),
                "userId": user_id
            })
            
            if not rec:
                raise ValueError("Recommendation not found")
            
            # Get full activity details
            if rec.get('activityId'):
                activity = await self.db.activities.find_one({
                    "_id": ObjectId(rec['activityId'])
                })
                if activity:
                    rec['activityDetails'] = activity
            
            return rec
        
        except Exception as e:
            logger.error(f"Error retrieving recommendation: {e}")
            raise
    
    async def reflect_on_itinerary(
        self,
        itinerary: List[Dict[str, Any]],
        user_expectations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Reflect on whether itinerary meets user expectations
        
        Args:
            itinerary: Current itinerary items
            user_expectations: User's expectations and preferences
            
        Returns:
            Reflection with suggestions
        """
        reflection = {
            "isGoodFit": True,
            "strengths": [],
            "suggestions": [],
            "confidence": 0.8
        }
        
        total_duration = sum(item.get('duration', 0) for item in itinerary if isinstance(item, dict))
        
        # Check duration
        if user_expectations.get('preferredDuration'):
            expected = user_expectations['preferredDuration']
            if abs(total_duration - expected) <= 30:  # Within 30 minutes
                reflection["strengths"].append("Duration matches expectations")
            else:
                reflection["suggestions"].append(f"Consider adjusting duration (current: {total_duration}min, expected: {expected}min)")
        
        # Check pace
        if user_expectations.get('pace'):
            pace = user_expectations['pace'].lower()
            if pace == 'relaxed' and total_duration > 180:
                reflection["suggestions"].append("Consider breaking into smaller segments for a more relaxed pace")
            elif pace == 'intensive' and total_duration < 120:
                reflection["suggestions"].append("Could add more activities for a more intensive experience")
        
        reflection["isGoodFit"] = len(reflection["suggestions"]) == 0
        
        return reflection
    
    async def update_recommendation_itinerary(
        self,
        recommendation_id: str,
        user_id: str,
        new_itinerary: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update the itinerary of a recommendation
        
        Args:
            recommendation_id: Recommendation ID
            user_id: User ID for authorization
            new_itinerary: Updated itinerary items
            
        Returns:
            Updated recommendation
        """
        try:
            if not ObjectId.is_valid(recommendation_id):
                raise ValueError("Invalid recommendation ID")
            
            result = await self.db.recommendations.update_one(
                {"_id": ObjectId(recommendation_id), "userId": user_id},
                {"$set": {"itinerary": new_itinerary}}
            )
            
            if result.matched_count == 0:
                raise ValueError("Recommendation not found")
            
            # Fetch updated recommendation
            updated = await self.db.recommendations.find_one({
                "_id": ObjectId(recommendation_id)
            })
            
            logger.info(f"Updated itinerary for recommendation {recommendation_id}")
            return updated
        
        except Exception as e:
            logger.error(f"Error updating itinerary: {e}")
            raise
    
    # =========================================================================
    # OFFERINGS AGENT TOOLS
    # =========================================================================
    
    async def search_offerings(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search available offerings
        
        Args:
            query: Search query for offerings
            limit: Max number of results
            
        Returns:
            List of offering documents
        """
        try:
            # Text search on offerings
            search_filter = {
                "$or": [
                    {"shortDescription": {"$regex": query, "$options": "i"}},
                    {"longDescription": {"$regex": query, "$options": "i"}}
                ]
            }
            
            offerings = await self.db.offerings.find(search_filter).limit(limit).to_list(limit)
            logger.info(f"Found {len(offerings)} offerings for query: {query}")
            return offerings
        
        except Exception as e:
            logger.error(f"Error searching offerings: {e}")
            return []
    
    async def reflect_on_offerings(
        self,
        current_offerings: List[str],
        user_needs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Reflect on whether current offerings meet user needs
        
        Args:
            current_offerings: List of current offering IDs
            user_needs: User requirements
            
        Returns:
            Reflection with suggestions
        """
        reflection = {
            "areSufficient": True,
            "needed": [],
            "optional": [],
            "confidence": 0.7
        }
        
        # Check common needs
        if user_needs.get('requiresFood'):
            reflection["needed"].append("Refreshments or catering")
        
        if user_needs.get('requiresCertificate'):
            reflection["needed"].append("Certificate of completion")
        
        if user_needs.get('requiresTransport'):
            reflection["needed"].append("Transportation service")
        
        if user_needs.get('requiresMaterials'):
            reflection["needed"].append("Materials and supplies")
        
        reflection["areSufficient"] = len(reflection["needed"]) == 0
        
        return reflection
    
    async def update_recommendation_offerings(
        self,
        recommendation_id: str,
        user_id: str,
        offering_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Update offerings for a recommendation
        
        Args:
            recommendation_id: Recommendation ID
            user_id: User ID for authorization
            offering_ids: List of offering IDs to add
            
        Returns:
            Updated recommendation
        """
        try:
            if not ObjectId.is_valid(recommendation_id):
                raise ValueError("Invalid recommendation ID")
            
            result = await self.db.recommendations.update_one(
                {"_id": ObjectId(recommendation_id), "userId": user_id},
                {"$set": {"offeringIds": offering_ids}}
            )
            
            if result.matched_count == 0:
                raise ValueError("Recommendation not found")
            
            # Fetch updated recommendation
            updated = await self.db.recommendations.find_one({
                "_id": ObjectId(recommendation_id)
            })
            
            logger.info(f"Updated offerings for recommendation {recommendation_id}")
            return updated
        
        except Exception as e:
            logger.error(f"Error updating offerings: {e}")
            raise
