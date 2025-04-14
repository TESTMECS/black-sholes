from blacksholes.bs_client import BlackScholesClient
from blacksholes.bs_config import BlackScholesConfig
from blacksholes.schemas import UserResponse, Token
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create a BlackScholesClient with mocked API calls."""
    config = BlackScholesConfig(bs_base_url="http://localhost:8000", backoff=False)
    return BlackScholesClient(config)


@patch("blacksholes.bs_client.httpx.Client")
def test_register(mock_client, client):
    """Test user registration."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"username": "testuser", "role": "user"}
    
    # Setup mock client
    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    # Call the method
    result = client.register(username="testuser", password="password123", role="user")
    
    # Assertions
    assert isinstance(result, UserResponse)
    assert result.username == "testuser"
    assert result.role == "user"
    mock_client_instance.post.assert_called_once()


@patch("blacksholes.bs_client.httpx.Client")
def test_login(mock_client, client):
    """Test user login."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "expires": "2023-01-01T00:00:00"
    }
    
    # Setup mock client
    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    # Call the method
    result = client.login(username="testuser", password="password123")
    
    # Assertions
    assert isinstance(result, Token)
    assert result.token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    assert result.expires == "2023-01-01T00:00:00"
    assert client.token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    assert client.token_expires == "2023-01-01T00:00:00"
    mock_client_instance.post.assert_called_once()


@patch("blacksholes.bs_client.httpx.Client")
def test_auth_header(mock_client, client):
    """Test that auth header is added to requests after login."""
    # Setup login mock
    login_response = MagicMock()
    login_response.status_code = 200
    login_response.json.return_value = {
        "token": "test_token",
        "expires": "2023-01-01T00:00:00"
    }
    
    # Setup calculations mock
    calc_response = MagicMock()
    calc_response.status_code = 200
    calc_response.json.return_value = {
        "data": [],
        "meta": {"limit": 100, "offset": 0, "count": 0}
    }
    
    # Setup mock client
    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = login_response
    mock_client_instance.get.return_value = calc_response
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    # Login first
    client.login(username="testuser", password="password123")
    
    # Then make an authenticated request
    client.get_calculations()
    
    # Check that the auth header was included
    _, kwargs = mock_client_instance.get.call_args
    assert "headers" in kwargs
    assert kwargs["headers"]["Authorization"] == "Bearer test_token"
