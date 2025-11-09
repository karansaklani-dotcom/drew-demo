"""Client for communicating with the main backend API."""

import logging
from typing import Optional, Dict, Any, List
import httpx
from config import config

logger = logging.getLogger(__name__)


class MainBackendClient:
    """Client for making requests to the main backend API."""
    
    def __init__(self, base_url: Optional[str] = None, api_prefix: Optional[str] = None):
        self.base_url = base_url or config.main_backend.base_url
        self.api_prefix = api_prefix or config.main_backend.api_prefix
        self.full_url = f"{self.base_url}{self.api_prefix}"
        self.client = httpx.AsyncClient(timeout=30.0)
        
    def _get_headers(self, auth_token: Optional[str] = None) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        return headers
    
    async def get_events(
        self,
        location: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get events from the main backend."""
        try:
            params = {}
            if location:
                params['location'] = location
            if category:
                params['category'] = category
            if search:
                params['search'] = search
            
            response = await self.client.get(
                f"{self.full_url}/events",
                params=params,
                headers=self._get_headers(auth_token)
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            raise
    
    async def get_event_details(
        self,
        event_id: str,
        auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed information about a specific event."""
        try:
            response = await self.client.get(
                f"{self.full_url}/events/{event_id}",
                headers=self._get_headers(auth_token)
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting event details: {e}")
            raise
    
    async def get_user_info(
        self,
        auth_token: str
    ) -> Dict[str, Any]:
        """Get current user information."""
        try:
            response = await self.client.get(
                f"{self.full_url}/auth/me",
                headers=self._get_headers(auth_token)
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("Main backend client closed")


# Global client instance
_client_instance: Optional[MainBackendClient] = None


def get_main_backend_client() -> MainBackendClient:
    """Get or create the global main backend client instance."""
    global _client_instance
    
    if _client_instance is None:
        _client_instance = MainBackendClient()
    
    return _client_instance
