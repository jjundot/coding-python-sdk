"""Authentication modules for Coding API"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import base64
from datetime import datetime, timedelta
import httpx


class AuthBase(ABC):
    """Base authentication class"""

    def __init__(self, team: str):
        self.team = team

    @abstractmethod
    def get_auth_header(self) -> Dict[str, str]:
        """Get authorization header"""
        pass

    def get_base_url(self) -> str:
        """Get base URL for API requests"""
        return f"https://{self.team}.coding.net/open-api"


class OAuth2Auth(AuthBase):
    """OAuth 2.0 Authentication

    Args:
        team: Team name (domain prefix)
        client_id: OAuth client ID
        client_secret: OAuth client secret
        access_token: Access token (optional, can be obtained via authorization flow)
        refresh_token: Refresh token for token refresh
    """

    def __init__(
        self,
        team: str,
        client_id: str,
        client_secret: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ):
        super().__init__(team)
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry: Optional[datetime] = None

    def get_auth_header(self) -> Dict[str, str]:
        """Get authorization header for OAuth 2.0"""
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        return {"Authorization": f"Bearer {self.access_token}"}

    async def refresh_access_token(self):
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            raise ValueError("Refresh token not available")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://{self.team}.coding.net/api/oauth/access_token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token", self.refresh_token)
            self.token_expiry = datetime.now() + timedelta(seconds=int(data.get("expires_in", 7200)))

    def is_token_expired(self) -> bool:
        """Check if access token is expired"""
        if not self.token_expiry:
            return False
        return datetime.now() >= self.token_expiry


class TokenAuth(AuthBase):
    """Personal Access Token Authentication

    Args:
        team: Team name (domain prefix)
        token: Personal access token
    """

    def __init__(self, team: str, token: str):
        super().__init__(team)
        self.token = token

    def get_auth_header(self) -> Dict[str, str]:
        """Get authorization header for token authentication"""
        return {"Authorization": f"token {self.token}"}


class BasicAuth(AuthBase):
    """Basic Authentication (Project Token)

    Args:
        team: Team name (domain prefix)
        username: Username (project token username)
        password: Password (project token password)
    """

    def __init__(self, team: str, username: str, password: str):
        super().__init__(team)
        self.username = username
        self.password = password

    def get_auth_header(self) -> Dict[str, str]:
        """Get authorization header for basic authentication"""
        credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        return {"Authorization": f"Basic {credentials}"}
