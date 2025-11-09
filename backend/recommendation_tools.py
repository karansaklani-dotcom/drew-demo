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

class GenerateConversationalResponseInput(BaseModel):
    """Input for generating conversational response"""
    user_request: str = Field(description="The original user request or question")
    recommendations_summary: str = Field(description="Summary of recommendations created (titles and reasons)")
    number_of_recommendations: int = Field(description="Number of recommendations created")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context about the user's needs")

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
    score: float,
    customized_title: Optional[str] = None,
    customized_description: Optional[str] = None
) -> str:
    """
    Create a recommendation for an activity and add it to the current project.
    
    IMPORTANT: Customize the activity for the user's specific use case!
    - customized_title: Rewrite the activity title to fit their needs
      Example: "Corporate Yoga Session" -> "Festive Holiday Yoga & Wellness for Your Team"
    - customized_description: Explain how this activity meets their specific requirements
      Example: "Perfect for your Christmas party with 15 people - we'll include holiday themes..."
    
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
    
    # Create recommendation with customization
    rec = await _agent_tools_instance.create_recommendation(
        project_id=project_id,
        user_id=user_id,
        activity=activity,
        reason_to_recommend=reason,
        score=score,
        customized_title=customized_title,
        customized_description=customized_description
    )
    
    title_used = customized_title if customized_title else rec['title']
    return f"✓ Created recommendation: {title_used} (ID: {rec.get('id', rec.get('_id'))})"

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

@tool("generate_conversational_response", args_schema=GenerateConversationalResponseInput, return_direct=False)
async def generate_conversational_response_tool(
    user_request: str,
    recommendations_summary: str,
    number_of_recommendations: int,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate a warm, conversational response to the user about the recommendations created.
    
    This tool creates engaging, friendly responses that:
    - Acknowledge the user's request naturally
    - Highlight the recommendations in an enthusiastic way
    - Use conversational language (not robotic)
    - Show personality and helpfulness
    - Keep it concise but warm (2-4 sentences)
    
    Use this tool after creating recommendations to provide a great user experience.
    """
    if not _agent_tools_instance:
        return "Error: Agent tools not initialized"
    
    # Use LLM to generate conversational response
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
    import os
    
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        # Fallback to simple response
        return f"I've found {number_of_recommendations} great activities for you! Check them out in your recommendations."
    
    llm = ChatOpenAI(
        api_key=openai_api_key,
        model="gpt-4o-mini",
        temperature=0.8  # Higher temperature for more conversational tone
    )
    
    system_prompt = """You are Drew, a friendly and enthusiastic activity recommendation assistant. 
Your job is to create warm, conversational responses that make users feel heard and excited about their recommendations.

Guidelines:
- Be conversational and natural (like talking to a friend)
- Show enthusiasm but don't overdo it
- Acknowledge what the user asked for
- Highlight 1-2 key recommendations naturally
- Keep it concise (2-4 sentences max)
- Use "I" and "you" to make it personal
- Don't be robotic or overly formal
- Show personality and helpfulness

Example good responses:
- "I found some great options for your team! I've added 4 activities that should work perfectly for your group size and location. The yoga session looks especially fun - it's customized for your holiday party theme!"
- "Perfect! I've curated 4 activities that match what you're looking for. Check out the recommendations - I think you'll love the team building workshop, it's designed exactly for groups your size."
- "Great request! I've added 4 recommendations to your project. They're all tailored to your needs - the cooking class is particularly popular for corporate events like yours."

Example bad responses (avoid):
- "I have successfully created 4 recommendations based on your criteria."
- "The system has generated the following recommendations: [list]"
- "Recommendations have been added to your project."
"""
    
    # Try to get actual recommendations from database for better summary
    context = get_current_context()
    project_id = context.get('project_id')
    
    recommendations_details = []
    if project_id and _agent_tools_instance:
        try:
            from bson import ObjectId
            # Get recent recommendations for this project
            recommendations = await _agent_tools_instance.db.recommendations.find({
                "projectId": project_id
            }).sort("createdAt", -1).limit(number_of_recommendations).to_list(number_of_recommendations)
            
            for rec in recommendations:
                title = rec.get('customizedTitle') or rec.get('title', 'Unknown')
                reason = rec.get('reasonToRecommend', 'Great activity')
                recommendations_details.append(f"- {title}: {reason}")
        except Exception as e:
            logger.error(f"Error fetching recommendations: {e}")
            # Fall back to provided summary
            recommendations_details = recommendations_summary.split('\n') if recommendations_summary else []
    else:
        # Use provided summary
        recommendations_details = recommendations_summary.split('\n') if recommendations_summary else []
    
    recommendations_text = '\n'.join(recommendations_details) if recommendations_details else recommendations_summary
    
    user_prompt = f"""User asked: "{user_request}"

I created {number_of_recommendations} recommendations:
{recommendations_text}

Generate a warm, conversational response that acknowledges their request and highlights the recommendations naturally."""
    
    try:
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        return response.content
    except Exception as e:
        logger.error(f"Error generating conversational response: {e}")
        # Fallback response
        return f"I've found {number_of_recommendations} great activities for you! Check them out in your recommendations - they're all tailored to what you're looking for."

# List of all tools
recommendation_tools = [
    search_activities_tool,
    create_recommendation_tool,
    reflect_on_activity_tool,
    generate_conversational_response_tool
]
