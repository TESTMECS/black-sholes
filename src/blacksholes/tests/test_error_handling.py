from blacksholes.bs_client import BlackScholesClient
from blacksholes.bs_config import BlackScholesConfig
import pytest
from unittest.mock import patch, MagicMock
import httpx


@pytest.fixture
def client():
    """Create a BlackScholesClient with mocked API calls."""
    config = BlackScholesConfig(bs_base_url="http://localhost:8000", backoff=False)
    client = BlackScholesClient(config)
    # Set a token to simulate being logged in
    client.token = "test_token"
    return client


@patch("blacksholes.bs_client.httpx.Client")
def test_http_error_handling(mock_client, client):
    """Test that HTTP errors are properly handled."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found", request=MagicMock(), response=mock_response
    )
    
    # Setup mock client
    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    # Call the method and expect an exception
    with pytest.raises(httpx.HTTPStatusError):
        client.get_calculation(calculation_id=999)


@patch("blacksholes.bs_client.httpx.Client")
def test_connection_error_handling(mock_client, client):
    """Test that connection errors are properly handled."""
    # Setup mock client to raise a connection error
    mock_client_instance = MagicMock()
    mock_client_instance.get.side_effect = httpx.ConnectError("Connection refused")
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    # Call the method and expect an exception
    with pytest.raises(httpx.ConnectError):
        client.get_calculation(calculation_id=1)


@patch("blacksholes.bs_client.httpx.Client")
def test_timeout_error_handling(mock_client, client):
    """Test that timeout errors are properly handled."""
    # Setup mock client to raise a timeout error
    mock_client_instance = MagicMock()
    mock_client_instance.get.side_effect = httpx.TimeoutException("Request timed out")
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    # Call the method and expect an exception
    with pytest.raises(httpx.TimeoutException):
        client.get_calculation(calculation_id=1)


@patch("blacksholes.bs_client.httpx.Client")
def test_invalid_json_handling(mock_client, client):
    """Test handling of invalid JSON responses."""
    # Setup mock response with invalid JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    
    # Setup mock client
    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    # Call the method and expect an exception
    with pytest.raises(ValueError):
        client.get_calculation(calculation_id=1)
