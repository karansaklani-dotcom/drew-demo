"""Tools for event discovery and recommendation."""

import logging
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool
from api.client import get_main_backend_client

logger = logging.getLogger(__name__)


class EventTools:
    """Event-related tools for agents."""
    
    def __init__(self, auth_token: Optional[str] = None):
        self.auth_token = auth_token
        self.client = get_main_backend_client()
    
    @tool
    async def search_events(
        location: Optional[str] = None,
        category: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for events based on location, category, or search query.
        
        Args:
            location: City or state to search for events
            category: Event category to filter by
            search_query: Text to search in event titles and descriptions
            
        Returns:
            Dictionary containing list of events
        """
        try:
            client = get_main_backend_client()
            result = await client.get_events(
                location=location,
                category=category,
                search=search_query
            )
            return result
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return {"error": str(e), "events": []}
    
    @tool
    async def get_event_details(event_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific event.
        
        Args:
            event_id: The unique identifier of the event
            
        Returns:
            Dictionary containing detailed event information
        """
        try:
            client = get_main_backend_client()
            result = await client.get_event_details(event_id)
            return result
        except Exception as e:
            logger.error(f"Error getting event details: {e}")
            return {"error": str(e)}
    
    @tool
    async def filter_events_by_criteria(
        events: List[Dict[str, Any]],
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filter a list of events by various criteria.
        
        Args:
            events: List of event dictionaries to filter
            min_price: Minimum price filter
            max_price: Maximum price filter
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)
            
        Returns:
            Filtered list of events
        """
        try:
            filtered = events.copy()
            
            # Filter by price
            if min_price is not None:
                filtered = [e for e in filtered if e.get('price', 0) >= min_price]
            if max_price is not None:
                filtered = [e for e in filtered if e.get('price', float('inf')) <= max_price]
            
            # Filter by date
            if start_date:
                filtered = [e for e in filtered if e.get('date', '') >= start_date]
            if end_date:
                filtered = [e for e in filtered if e.get('date', '') <= end_date]
            
            return filtered
        except Exception as e:
            logger.error(f"Error filtering events: {e}")
            return events
    
    @tool
    async def recommend_events_by_preferences(
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recommend events based on user preferences.
        
        Args:
            user_preferences: Dictionary containing user preferences like:
                - interests: List of interest categories
                - location: Preferred location
                - price_range: Tuple of (min, max) price
                - date_range: Tuple of (start, end) dates
                
        Returns:
            Dictionary containing recommended events
        """
        try:
            client = get_main_backend_client()
            
            # Extract preferences
            interests = user_preferences.get('interests', [])
            location = user_preferences.get('location')
            
            # Search for events based on interests
            all_events = []
            
            if interests:
                for interest in interests:
                    result = await client.get_events(category=interest, location=location)
                    all_events.extend(result.get('events', []))
            else:
                result = await client.get_events(location=location)
                all_events = result.get('events', [])
            
            # Remove duplicates
            seen_ids = set()
            unique_events = []
            for event in all_events:
                event_id = event.get('_id')
                if event_id and event_id not in seen_ids:
                    seen_ids.add(event_id)
                    unique_events.append(event)
            
            # Apply additional filters
            price_range = user_preferences.get('price_range')
            if price_range:
                min_price, max_price = price_range
                unique_events = [e for e in unique_events 
                               if min_price <= e.get('price', 0) <= max_price]
            
            return {
                "recommended_events": unique_events[:20],  # Limit to top 20
                "count": len(unique_events)
            }
        except Exception as e:
            logger.error(f"Error recommending events: {e}")
            return {"error": str(e), "recommended_events": []}


def create_event_tools(auth_token: Optional[str] = None) -> List:
    """Create a list of event tools for use in agents."""
    tools_instance = EventTools(auth_token)
    
    return [
        EventTools.search_events,
        EventTools.get_event_details,
        EventTools.filter_events_by_criteria,
        EventTools.recommend_events_by_preferences
    ]
