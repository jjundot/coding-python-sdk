"""Tests for Coding API client"""

import pytest
from coding_sdk import CodingClient, TokenAuth


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization"""
    auth = TokenAuth(team="test-team", token="test-token")
    client = CodingClient(auth=auth)
    assert client.auth == auth
    assert client.base_url == "https://test-team.coding.net/open-api"
    await client.close()


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test client as context manager"""
    auth = TokenAuth(team="test-team", token="test-token")
    async with CodingClient(auth=auth) as client:
        assert client.auth == auth
