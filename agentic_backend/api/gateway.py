"""Server-to-server API gateway with cookie passthrough."""

import logging
from typing import Optional, Dict, Any
import httpx
from fastapi import Request, Response
from config import config

logger = logging.getLogger(__name__)


class APIGateway:
    """Gateway for proxying requests to main backend with cookie passthrough."""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or config.main_backend.base_url
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
    
    async def forward_request(
        self,
        request: Request,
        path: str,
        method: str = "GET",
        json_data: Optional[Dict[str, Any]] = None
    ) -> Response:
        """Forward a request to the main backend with cookie passthrough."""
        try:
            # Extract cookies from the original request
            cookies = request.cookies
            
            # Extract headers (excluding host and connection headers)
            headers = {}
            excluded_headers = {'host', 'connection', 'content-length'}
            for key, value in request.headers.items():
                if key.lower() not in excluded_headers:
                    headers[key] = value
            
            # Build the target URL
            target_url = f"{self.base_url}{path}"
            
            # Make the request to the main backend
            if method.upper() == "GET":
                response = await self.client.get(
                    target_url,
                    headers=headers,
                    cookies=cookies
                )
            elif method.upper() == "POST":
                response = await self.client.post(
                    target_url,
                    headers=headers,
                    cookies=cookies,
                    json=json_data
                )
            elif method.upper() == "PUT":
                response = await self.client.put(
                    target_url,
                    headers=headers,
                    cookies=cookies,
                    json=json_data
                )
            elif method.upper() == "DELETE":
                response = await self.client.delete(
                    target_url,
                    headers=headers,
                    cookies=cookies
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Create response with same status code and content
            fastapi_response = Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get('content-type', 'application/json')
            )
            
            # Copy response cookies
            for cookie_name, cookie_value in response.cookies.items():
                fastapi_response.set_cookie(cookie_name, cookie_value)
            
            # Copy relevant headers
            for key, value in response.headers.items():
                if key.lower() not in {'content-length', 'transfer-encoding', 'connection'}:
                    fastapi_response.headers[key] = value
            
            logger.info(f"Forwarded {method} request to {target_url} - Status: {response.status_code}")
            return fastapi_response
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error forwarding request: {e}")
            return Response(
                content=f'{{"error": "Failed to forward request: {str(e)}"}}',
                status_code=502,
                media_type='application/json'
            )
        except Exception as e:
            logger.error(f"Error forwarding request: {e}")
            return Response(
                content=f'{{"error": "Internal gateway error: {str(e)}"}}',
                status_code=500,
                media_type='application/json'
            )
    
    async def make_authenticated_request(
        self,
        path: str,
        method: str = "GET",
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        auth_token: Optional[str] = None
    ) -> httpx.Response:
        """Make an authenticated request to the main backend."""
        try:
            # Build headers
            request_headers = headers.copy() if headers else {}
            request_headers["Content-Type"] = "application/json"
            request_headers["Accept"] = "application/json"
            
            if auth_token:
                request_headers["Authorization"] = f"Bearer {auth_token}"
            
            # Build the target URL
            target_url = f"{self.base_url}{path}"
            
            # Make the request
            if method.upper() == "GET":
                response = await self.client.get(
                    target_url,
                    headers=request_headers,
                    cookies=cookies or {}
                )
            elif method.upper() == "POST":
                response = await self.client.post(
                    target_url,
                    headers=request_headers,
                    cookies=cookies or {},
                    json=json_data
                )
            elif method.upper() == "PUT":
                response = await self.client.put(
                    target_url,
                    headers=request_headers,
                    cookies=cookies or {},
                    json=json_data
                )
            elif method.upper() == "DELETE":
                response = await self.client.delete(
                    target_url,
                    headers=request_headers,
                    cookies=cookies or {}
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            logger.info(f"Made {method} request to {target_url} - Status: {response.status_code}")
            return response
            
        except Exception as e:
            logger.error(f"Error making authenticated request: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("API gateway client closed")


# Global gateway instance
_gateway_instance: Optional[APIGateway] = None


def get_api_gateway() -> APIGateway:
    """Get or create the global API gateway instance."""
    global _gateway_instance
    
    if _gateway_instance is None:
        _gateway_instance = APIGateway()
    
    return _gateway_instance
