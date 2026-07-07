"""Tests for authentication modules"""

import pytest
from coding_sdk.auth import OAuth2Auth, TokenAuth, BasicAuth


def test_token_auth():
    """Test token authentication"""
    auth = TokenAuth(team="test-team", token="test-token")
    assert auth.get_base_url() == "https://test-team.coding.net/open-api"
    assert auth.get_auth_header() == {"Authorization": "token test-token"}


def test_basic_auth():
    """Test basic authentication"""
    auth = BasicAuth(team="test-team", username="user", password="pass")
    assert auth.get_base_url() == "https://test-team.coding.net/open-api"
    assert "Authorization" in auth.get_auth_header()
    assert auth.get_auth_header()["Authorization"].startswith("Basic ")


def test_oauth2_auth():
    """Test OAuth2 authentication"""
    auth = OAuth2Auth(
        team="test-team",
        client_id="test-id",
        client_secret="test-secret",
        access_token="test-token",
    )
    assert auth.get_base_url() == "https://test-team.coding.net/open-api"
    assert auth.get_auth_header() == {"Authorization": "Bearer test-token"}


def test_oauth2_without_token():
    """Test OAuth2 authentication without token"""
    auth = OAuth2Auth(
        team="test-team",
        client_id="test-id",
        client_secret="test-secret",
    )
    with pytest.raises(ValueError):
        auth.get_auth_header()
