"""Event discovery and recommendation agent."""

import logging
from typing import Optional, List, Dict, Any
from langchain_core.tools import BaseTool

from .base_agent import BaseAgent
from tools.event_tools import create_event_tools
from config import config

logger = logging.getLogger(__name__)


class EventDiscoveryAgent(BaseAgent):
    """Agent specialized in event discovery and recommendations."""
    
    def __init__(
        self,
        auth_token: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None
    ):
        # Create event tools
        tools = create_event_tools(auth_token)
        
        # System message for event agent
        system_message = """You are an intelligent event discovery and recommendation assistant.
        
Your role is to help users find and discover events that match their interests and preferences.

You have access to tools that can:
1. Search for events by location, category, or keywords
2. Get detailed information about specific events
3. Filter events based on various criteria (price, date, etc.)
4. Recommend events based on user preferences

When helping users:
- Ask clarifying questions to understand their preferences
- Provide relevant event recommendations
- Explain why certain events might be a good fit
- Help users refine their search criteria
- Be conversational and friendly

Remember user preferences throughout the conversation and use them to provide better recommendations.
"""
        
        super().__init__(
            agent_type="event_discovery",
            system_message=system_message,
            tools=tools,
            api_key=api_key,
            model=model,
            provider=provider
        )
        
        self.auth_token = auth_token
    
    async def discover_events(
        self,
        user_message: str,
        thread_id: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Discover events based on user message and preferences."""
        try:
            logger.info(f"Discovering events for thread {thread_id}")
            
            # Invoke the agent
            result = await self.invoke(
                message=user_message,
                thread_id=thread_id,
                user_preferences=user_preferences
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error discovering events: {e}")
            return {
                "error": str(e),
                "thread_id": thread_id
            }
    
    async def get_recommendations(
        self,
        thread_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get event recommendations based on preferences."""
        try:
            # Build a message asking for recommendations
            message = "Based on my preferences, can you recommend some events?"
            
            result = await self.invoke(
                message=message,
                thread_id=thread_id,
                user_preferences=preferences
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return {
                "error": str(e),
                "thread_id": thread_id
            }
