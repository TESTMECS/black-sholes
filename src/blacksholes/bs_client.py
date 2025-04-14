from .schemas import *
from .bs_config import BlackScholesConfig
from logging import getLogger
from typing import Optional, List
import backoff
import httpx

logger = getLogger(__name__)


class BlackScholesClient:
    """Client for interacting with the Black-Scholes API."""
    # Endpoints
    HEALTH_CHECK_ENDPOINT = "/api"
    
    def __init__(self, config: BlackScholesConfig):
        logger.debug(f"Initializing BlackScholesClient with config: {config}")
        self.bs_base_url = config.bs_base_url
        self.backoff = config.backoff
        self.backoff_max_time = config.backoff_max_time
        if self.backoff:
            self.call_api = backoff.on_exception(
                backoff.expo,
                Exception,
                max_time=self.backoff_max_time,
            )(self.call_api)
    
    def call_api(self, endpoint: str, params: Optional[dict] = None):
        """Call the API with the given endpoint and method."""
        pass

    def get_health_check(self) -> dict:
        """Get the health check of the API."""
        logger.debug(f"Getting health check from {self.bs_base_url}{self.HEALTH_CHECK_ENDPOINT}")
        return self.call_api(endpoint=self.HEALTH_CHECK_ENDPOINT, params=None)
    
    def get_calculations(self, limit: int = 100, offset: int = 0):
        """Get a list of calculations."""
        logger.debug(f"Getting calculations from {self.bs_base_url}/api/calculations?limit={limit}&offset={offset}")
        return
        
        
