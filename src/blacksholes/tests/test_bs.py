from blacksholes.bs_client import BlackScholesClient
from blacksholes.bs_config import BlackScholesConfig
import pytest 

def test_get_calculations():
    config = BlackScholesConfig(bs_base_url="http://localhost:8000", backoff=False)
    client = BlackScholesClient(config)
    response = client.get_calculations()
    assert response.status_code == 200
    
