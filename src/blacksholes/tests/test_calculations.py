from blacksholes.bs_client import BlackScholesClient
from blacksholes.bs_config import BlackScholesConfig
from blacksholes.schemas import CalculationCreate, CalculationResponse, HeatmapCreate, HeatmapList
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create a BlackScholesClient with mocked API calls."""
    config = BlackScholesConfig(bs_base_url="http://localhost:8000", backoff=False)
    client = BlackScholesClient(config)
    # Set a token to simulate being logged in
    client.token = "test_token"
    return client


@pytest.fixture
def calculation_create():
    """Create a sample CalculationCreate object."""
    return CalculationCreate(
        spot_price=100.0,
        strike_price=100.0,
        time_to_maturity=1.0,
        volatility=0.2,
        risk_free_rate=0.05,
        call_price=10.45,
        put_price=5.57
    )


@pytest.fixture
def calculation_response():
    """Create a sample calculation response data."""
    return {
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


@patch("blacksholes.bs_client.httpx.Client")
def test_get_calculation(mock_client, client, calculation_response):
    """Test getting a specific calculation by ID."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = calculation_response
    
    # Setup mock client
    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    # Call the method
    result = client.get_calculation(calculation_id=1)
    
    # Assertions
    assert isinstance(result, CalculationResponse)
    assert result.id == 1
    assert result.spot_price == 100.0
    assert result.strike_price == 100.0
    mock_client_instance.get.assert_called_once()


@patch("blacksholes.bs_client.httpx.Client")
def test_create_calculation(mock_client, client, calculation_create, calculation_response):
    """Test creating a new calculation."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = calculation_response
    
    # Setup mock client
    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    # Call the method
    result = client.create_calculation(calculation=calculation_create)
    
    # Assertions
    assert isinstance(result, CalculationResponse)
    assert result.id == 1
    assert result.spot_price == 100.0
    assert result.strike_price == 100.0
    mock_client_instance.post.assert_called_once()


@patch("blacksholes.bs_client.httpx.Client")
def test_get_heatmaps(mock_client, client):
    """Test getting heatmaps for a calculation."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "calculation_id": 1,
        "heatmaps": {
            "call_price": {
                "heatmap_type": "call_price",
                "min_spot": 80.0,
                "max_spot": 120.0,
                "min_vol": 0.1,
                "max_vol": 0.4,
                "spot_steps": 20,
                "vol_steps": 20,
                "heatmap_data": [[1.0, 2.0], [3.0, 4.0]]
            }
        }
    }
    
    # Setup mock client
    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    # Call the method
    result = client.get_heatmaps(calculation_id=1)
    
    # Assertions
    assert isinstance(result, HeatmapList)
    assert result.calculation_id == 1
    assert "call_price" in result.heatmaps
    mock_client_instance.get.assert_called_once()


@patch("blacksholes.bs_client.httpx.Client")
def test_add_heatmap(mock_client, client):
    """Test adding a heatmap to a calculation."""
    # Create a sample heatmap
    heatmap = HeatmapCreate(
        heatmap_type="call_price",
        min_spot=80.0,
        max_spot=120.0,
        min_vol=0.1,
        max_vol=0.4,
        spot_steps=20,
        vol_steps=20,
        heatmap_data=[[1.0, 2.0], [3.0, 4.0]]
    )
    
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "message": "Heatmap added successfully",
        "heatmap_id": 1,
        "calculation_id": 1
    }
    
    # Setup mock client
    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    # Call the method
    result = client.add_heatmap(calculation_id=1, heatmap=heatmap)
    
    # Assertions
    assert result["message"] == "Heatmap added successfully"
    assert result["heatmap_id"] == 1
    assert result["calculation_id"] == 1
    mock_client_instance.post.assert_called_once()
