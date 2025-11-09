"""
LangChain Tools for Recommendation Agent
Defines callable tools that the recommendation agent can use
"""
from typing import Dict, Any, List, Optional
from langchain.tools import tool
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

# Tool input schemas
class SearchActivitiesInput(BaseModel):
    """Input for searching activities"""
    query: str = Field(description="Natural language search query describing desired activities including location, group size, preferences, and any other requirements")
    limit: int = Field(5, description="Maximum number of results to return")

class CreateRecommendationInput(BaseModel):
    """Input for creating a recommendation"""
    activity_id: str = Field(description="ID of the activity to recommend")
    reason: str = Field(description="Why this activity is recommended for the user")
    score: float = Field(description="Match score between 0 and 1")
    customized_title: Optional[str] = Field(None, description="Customized title that fits the user's specific use case (optional)")
    customized_description: Optional[str] = Field(None, description="Customized description explaining how this activity meets their needs (optional)")

class ReflectOnActivityInput(BaseModel):
    """Input for reflecting on activity match"""
    activity_id: str = Field(description="ID of the activity to evaluate")
    user_requirements: Dict[str, Any] = Field(description="User's requirements and preferences")

# Global storage for agent tools instance (injected from server.py)
_agent_tools_instance = None
_current_context = {}

def set_agent_tools(tools_instance):
    """Set the AgentTools instance for tools to use"""
    global _agent_tools_instance
    _agent_tools_instance = tools_instance

def set_current_context(context: Dict[str, Any]):
    """Set the current execution context (project_id, user_id, etc.)"""
    global _current_context
    _current_context = context

def get_current_context() -> Dict[str, Any]:
    """Get the current execution context"""
    return _current_context

# Tool definitions
@tool("search_activities", args_schema=SearchActivitiesInput, return_direct=False)
async def search_activities_tool(
    query: str,
    limit: int = 5
) -> str:
    """
    Search for activities using pure semantic search based on natural language query.
    The query should include all requirements: location, group size, budget, preferences, etc.
    
    Example queries:
    - "team building activities in San Francisco for 15 people"
    - "volunteer opportunities for small groups in Oakland"
    - "creative workshops for corporate teams in the Bay Area"
    
    Returns a list of matching activities ranked by semantic similarity.
    """
    if not _agent_tools_instance:
        return "Error: Agent tools not initialized"
    
    # Pure semantic search - no filters
    activities = await _agent_tools_instance.search_activities(
        query=query,
        filters=None,
        limit=limit
    )
    
    if not activities:
        return f"No activities found for query: {query}. Try broadening your search criteria."
    
    # Format results for LLM
    results = []
    for i, activity in enumerate(activities, 1):
        result = f"{i}. {activity.get('title', 'Unknown')}\n"
        result += f"   ID: {activity.get('_id')}\n"
        result += f"   Description: {activity.get('shortDescription', 'N/A')}\n"
        result += f"   Location: {activity.get('city', 'N/A')}, {activity.get('state', 'N/A')}\n"
        result += f"   Price: ${activity.get('price', 0)}\n"
        result += f"   Group Size: {activity.get('minParticipants', 0)}-{activity.get('maxParticipants', 0)} people\n"
        result += f"   Duration: {activity.get('preferredDuration', 0)//60} hours\n"
        if 'similarity' in activity:
            result += f"   Match Score: {activity['similarity']:.2f}\n"
        results.append(result)
    
    return f"Found {len(activities)} activities:\n\n" + "\n".join(results)

@tool("create_recommendation", args_schema=CreateRecommendationInput, return_direct=False)
async def create_recommendation_tool(
    activity_id: str,
    reason: str,
    score: float
) -> str:
    """
    Create a recommendation for an activity and add it to the current project.
    Returns confirmation of the created recommendation.
    """
    if not _agent_tools_instance:
        return "Error: Agent tools not initialized"
    
    context = get_current_context()
    project_id = context.get('project_id')
    user_id = context.get('user_id')
    
    if not project_id or not user_id:
        return "Error: Missing project or user context"
    
    # Get activity details
    from bson import ObjectId
    from motor.motor_asyncio import AsyncIOMotorClient
    
    # Access the database through tools instance
    activity = await _agent_tools_instance.db.activities.find_one({"_id": ObjectId(activity_id)})
    
    if not activity:
        return f"Error: Activity with ID {activity_id} not found"
    
    # Create recommendation
    rec = await _agent_tools_instance.create_recommendation(
        project_id=project_id,
        user_id=user_id,
        activity=activity,
        reason_to_recommend=reason,
        score=score
    )
    
    return f"✓ Created recommendation: {rec['title']} (ID: {rec.get('id', rec.get('_id'))})"

@tool("reflect_on_activity", args_schema=ReflectOnActivityInput, return_direct=False)
async def reflect_on_activity_tool(
    activity_id: str,
    user_requirements: Dict[str, Any]
) -> str:
    """
    Evaluate how well an activity matches user requirements.
    Returns a detailed assessment with match score and reasons.
    """
    if not _agent_tools_instance:
        return "Error: Agent tools not initialized"
    
    from bson import ObjectId
    
    # Get activity details
    activity = await _agent_tools_instance.db.activities.find_one({"_id": ObjectId(activity_id)})
    
    if not activity:
        return f"Error: Activity with ID {activity_id} not found"
    
    # Reflect on match
    reflection_result = await _agent_tools_instance.reflect_and_transform(activity, user_requirements)
    reflection = reflection_result['reflection']
    
    # Format response
    result = f"Activity: {activity.get('title')}\n"
    result += f"Match Score: {reflection['score']:.2f}\n"
    result += f"Is Good Fit: {reflection['isFit']}\n"
    
    if reflection['matchedCriteria']:
        result += f"\n✓ Strengths:\n"
        for criterion in reflection['matchedCriteria']:
            result += f"  - {criterion}\n"
    
    if reflection['concerns']:
        result += f"\n⚠ Concerns:\n"
        for concern in reflection['concerns']:
            result += f"  - {concern}\n"
    
    return result

# List of all tools
recommendation_tools = [
    search_activities_tool,
    create_recommendation_tool,
    reflect_on_activity_tool
]
