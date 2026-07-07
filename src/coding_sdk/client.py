"""Main Coding API Client"""

from typing import Any, Dict, Optional
import httpx
from .auth import AuthBase
from .exceptions import APIError, NetworkError


class CodingClient:
    """Main client for interacting with CODING API

    Args:
        auth: Authentication instance (OAuth2Auth, TokenAuth, or BasicAuth)
        timeout: Request timeout in seconds (default: 30)
        base_url: Custom base URL (optional)
    """

    def __init__(
        self,
        auth: AuthBase,
        timeout: float = 30.0,
        base_url: Optional[str] = None,
    ):
        self.auth = auth
        self.timeout = timeout
        self.base_url = base_url or auth.get_base_url()
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    async def _request(
        self,
        method: str,
        url: str,
        action: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make an API request

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Endpoint URL
            action: CODING API action name
            **kwargs: Additional parameters to pass to request

        Returns:
            Response data
        """
        try:
            headers = self.auth.get_auth_header()
            headers.update(kwargs.pop("headers", {}))

            # Add action to query params
            params = kwargs.pop("params", {})
            params["action"] = action

            response = await self.client.request(
                method,
                url,
                headers=headers,
                params=params,
                **kwargs,
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
            except Exception:
                error_data = {}
            raise APIError(
                message=str(e),
                status_code=e.response.status_code,
                response_data=error_data,
            )
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {str(e)}")

    async def describe_coding_current_user(self) -> Dict[str, Any]:
        """Get current user information

        Returns:
            Current user data
        """
        response = await self._request(
            "POST",
            "/",
            "DescribeCodingCurrentUser",
            json={},
        )
        return response.get("Response", {}).get("User", response)

    async def close(self):
        """Close the client connection"""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    def __del__(self):
        """Cleanup"""
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.client.aclose())
            else:
                loop.run_until_complete(self.client.aclose())
        except Exception:
            pass
