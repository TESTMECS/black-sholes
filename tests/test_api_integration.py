"""
Test the API integration with the database.
"""
import pytest
import requests
from database.db_storage import init_db, store_calculation

# API base URL - assuming the server is already running
API_URL = "http://localhost:8000"

# Test user credentials
USERNAME = "testuser"
PASSWORD = "testpassword"

# Global variables to store token and calculation IDs
token = None
calculation_id = None
new_calculation_id = None


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    """Setup for the test module."""
    # Initialize the database
    init_db()

    # Store a test calculation
    global calculation_id
    calculation_id = store_calculation(
        spot_price=100.0,
        strike_price=105.0,
        time_to_maturity=1.0,
        volatility=0.2,
        risk_free_rate=0.05,
        call_price=8.02,
        put_price=7.49,
    )

    # Register and login
    register_user()
    global token
    token = login_user()

    yield
    # No teardown needed as we're not cleaning up the database


def register_user():
    """Register a test user."""
    response = requests.post(
        f"{API_URL}/api/auth/register",
        json={"username": USERNAME, "password": PASSWORD, "role": "user"},
    )
    # If user already exists, that's fine
    assert response.status_code in [201, 409], f"Failed to register user: {response.text}"


def login_user():
    """Login and get token."""
    response = requests.post(
        f"{API_URL}/api/auth/login",
        data={"username": USERNAME, "password": PASSWORD},
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"
    return response.json()["token"]


def test_list_calculations():
    """Test listing calculations."""
    response = requests.get(
        f"{API_URL}/api/calculations/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data
    assert len(data["data"]) >= 1


def test_get_calculation():
    """Test getting a specific calculation."""
    response = requests.get(
        f"{API_URL}/api/calculations/{calculation_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == calculation_id
    assert data["spot_price"] == 100.0
    assert data["strike_price"] == 105.0


def test_create_calculation():
    """Test creating a new calculation."""
    calculation_data = {
        "spot_price": 110.0,
        "strike_price": 110.0,
        "time_to_maturity": 0.5,
        "volatility": 0.25,
        "risk_free_rate": 0.04,
        "call_price": 7.5,
        "put_price": 6.2,
    }
    response = requests.post(
        f"{API_URL}/api/calculations/",
        json=calculation_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["spot_price"] == 110.0
    assert data["strike_price"] == 110.0

    # Store the new calculation ID for the next test
    global new_calculation_id
    new_calculation_id = data["id"]


def test_get_new_calculation():
    """Test getting the newly created calculation."""
    response = requests.get(
        f"{API_URL}/api/calculations/{new_calculation_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == new_calculation_id
    assert data["spot_price"] == 110.0
    assert data["strike_price"] == 110.0
    assert data["time_to_maturity"] == 0.5
    assert data["volatility"] == 0.25
    assert data["risk_free_rate"] == 0.04
    assert data["call_price"] == 7.5
    assert data["put_price"] == 6.2


def test_invalid_calculation_id():
    """Test getting a calculation with an invalid ID."""
    invalid_id = 9999  # Assuming this ID doesn't exist
    response = requests.get(
        f"{API_URL}/api/calculations/{invalid_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_unauthorized_access():
    """Test accessing the API without authentication."""
    response = requests.get(f"{API_URL}/api/calculations/")
    assert response.status_code == 401  # Unauthorized


def test_get_heatmaps():
    """Test getting heatmaps for a calculation."""
    # First, check if the calculation has heatmaps
    response = requests.get(
        f"{API_URL}/api/calculation/{calculation_id}/heatmaps",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "calculation_id" in data
    assert data["calculation_id"] == calculation_id
    assert "heatmaps" in data


def test_create_heatmap():
    """Test creating a heatmap for a calculation."""
    # Create a simple heatmap
    heatmap_data = {
        "heatmap_type": "test_heatmap",
        "min_spot": 90.0,
        "max_spot": 110.0,
        "min_vol": 0.1,
        "max_vol": 0.3,
        "spot_steps": 5,
        "vol_steps": 5,
        "heatmap_data": [
            [1.0, 2.0, 3.0, 4.0, 5.0],
            [2.0, 3.0, 4.0, 5.0, 6.0],
            [3.0, 4.0, 5.0, 6.0, 7.0],
            [4.0, 5.0, 6.0, 7.0, 8.0],
            [5.0, 6.0, 7.0, 8.0, 9.0],
        ],
    }
    response = requests.post(
        f"{API_URL}/api/calculation/{new_calculation_id}/heatmaps",
        json=heatmap_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "heatmap_id" in data
    assert data["calculation_id"] == new_calculation_id

    # Now verify we can get the heatmap
    response = requests.get(
        f"{API_URL}/api/calculation/{new_calculation_id}/heatmaps",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "heatmaps" in data
    assert "test_heatmap" in data["heatmaps"]

