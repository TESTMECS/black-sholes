from blacksholes.bs_client import BlackScholesClient
from blacksholes.bs_config import BlackScholesConfig
from blacksholes.schemas import CalculationList
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create a BlackScholesClient with mocked API calls."""
    config = BlackScholesConfig(bs_base_url="http://localhost:8000", backoff=False)
    return BlackScholesClient(config)


@patch("blacksholes.bs_client.httpx.Client")
def test_get_health_check(mock_client, client):
    """Test getting API health check."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"name": "Black-Scholes API", "version": "1.0.0"}

    # Setup mock client
    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance

    # Call the method
    result = client.get_health_check()

    # Assertions
    assert result == {"name": "Black-Scholes API", "version": "1.0.0"}
    mock_client_instance.get.assert_called_once()


@patch("blacksholes.bs_client.httpx.Client")
def test_get_calculations(mock_client, client):
    """Test getting a list of calculations."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {
                "id": 1,
                "spot_price": 100.0,
                "strike_price": 100.0,
                "time_to_maturity": 1.0,
                "volatility": 0.2,
                "risk_free_rate": 0.05,
                "call_price": 10.45,
                "put_price": 5.57,
                "timestamp": "2023-01-01T00:00:00",
                "heatmaps": None
            }
        ],
        "meta": {"limit": 100, "offset": 0, "count": 1}
    }

    # Setup mock client
    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance

    # Call the method
    result = client.get_calculations(limit=100, offset=0)

    # Assertions
    assert isinstance(result, CalculationList)
    assert len(result.data) == 1
    assert result.data[0].id == 1
    assert result.data[0].spot_price == 100.0
    mock_client_instance.get.assert_called_once()
