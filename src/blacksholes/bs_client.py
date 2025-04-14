from .schemas import *
from .bs_config import BlackScholesConfig
from logging import getLogger
from typing import Optional, Dict, Any
import backoff
import httpx

logger = getLogger(__name__)


class BlackScholesClient:
    """Client for interacting with the Black-Scholes API."""

    # Endpoints
    HEALTH_CHECK_ENDPOINT = "/api"
    AUTH_REGISTER_ENDPOINT = "/api/auth/register"
    AUTH_LOGIN_ENDPOINT = "/api/auth/login"
    CALCULATIONS_ENDPOINT = "/api/calculations"
    CALCULATION_ENDPOINT = "/api/calculations/{calculation_id}"
    HEATMAPS_ENDPOINT = "/api/calculation/{calculation_id}/heatmaps"

    def __init__(self, config: BlackScholesConfig):
        logger.debug(f"Initializing BlackScholesClient with config: {config}")
        self.bs_base_url = config.bs_base_url
        self.backoff = config.backoff
        self.backoff_max_time = config.backoff_max_time
        self.token = None
        self.token_expires = None

        if self.backoff:
            self.call_api = backoff.on_exception(
                backoff.expo,
                Exception,
                max_time=self.backoff_max_time,
            )(self.call_api)

    def call_api(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        auth_required: bool = True
    ) -> httpx.Response:
        """Call the API with the given endpoint and method.

        Parameters
        ----------
        endpoint : str
            The API endpoint to call
        method : str
            The HTTP method to use (GET, POST, etc.)
        params : Optional[Dict[str, Any]]
            Query parameters for the request
        data : Optional[Dict[str, Any]]
            JSON data for the request body
        auth_required : bool
            Whether authentication is required for this endpoint

        Returns
        -------
        httpx.Response
            The HTTP response

        Raises
        ------
        Exception
            If the request fails
        """
        url = f"{self.bs_base_url}{endpoint}"
        headers = {}

        # Add authentication token if required and available
        if auth_required and self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        logger.debug(f"Calling {method} {url} with params={params}, data={data}")

        with httpx.Client() as client:
            if method.upper() == "GET":
                response = client.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = client.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = client.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        # Check for errors
        if response.status_code >= 400:
            logger.error(f"API error: {response.status_code} - {response.text}")
            response.raise_for_status()

        return response

    def register(self, username: str, password: str, role: str = "user") -> UserResponse:
        """Register a new user.

        Parameters
        ----------
        username : str
            Username for the new user
        password : str
            Password for the new user
        role : str
            Role for the new user (default: "user")

        Returns
        -------
        UserResponse
            The created user
        """
        logger.debug(f"Registering user {username}")
        data = {"username": username, "password": password, "role": role}
        response = self.call_api(
            endpoint=self.AUTH_REGISTER_ENDPOINT,
            method="POST",
            data=data,
            auth_required=False
        )
        return UserResponse.model_validate(response.json())

    def login(self, username: str, password: str) -> Token:
        """Login a user and store the token.

        Parameters
        ----------
        username : str
            Username for login
        password : str
            Password for login

        Returns
        -------
        Token
            The authentication token
        """
        logger.debug(f"Logging in user {username}")
        # FastAPI OAuth2 login expects form data, not JSON
        response = self.call_api(
            endpoint=self.AUTH_LOGIN_ENDPOINT,
            method="POST",
            data={"username": username, "password": password},
            auth_required=False
        )
        token_data = Token.model_validate(response.json())
        self.token = token_data.token
        self.token_expires = token_data.expires
        return token_data

    def get_health_check(self) -> Dict[str, Any]:
        """Get the health check of the API.

        Returns
        -------
        Dict[str, Any]
            API health information
        """
        logger.debug(
            f"Getting health check from {self.bs_base_url}{self.HEALTH_CHECK_ENDPOINT}"
        )
        response = self.call_api(
            endpoint=self.HEALTH_CHECK_ENDPOINT,
            auth_required=False
        )
        return response.json()

    def get_calculations(self, limit: int = 100, offset: int = 0) -> CalculationList:
        """Get a list of calculations.

        Parameters
        ----------
        limit : int
            Maximum number of results to return (default: 100)
        offset : int
            Number of results to skip (default: 0)

        Returns
        -------
        CalculationList
            List of calculations
        """
        logger.debug(
            f"Getting calculations from {self.bs_base_url}{self.CALCULATIONS_ENDPOINT}?limit={limit}&offset={offset}"
        )
        params = {"limit": limit, "offset": offset}
        response = self.call_api(
            endpoint=self.CALCULATIONS_ENDPOINT,
            params=params
        )
        return CalculationList.model_validate(response.json())

    def get_calculation(self, calculation_id: int) -> CalculationResponse:
        """Get a specific calculation by ID.

        Parameters
        ----------
        calculation_id : int
            ID of the calculation to retrieve

        Returns
        -------
        CalculationResponse
            Calculation data
        """
        logger.debug(f"Getting calculation {calculation_id}")
        endpoint = self.CALCULATION_ENDPOINT.format(calculation_id=calculation_id)
        response = self.call_api(endpoint=endpoint)
        return CalculationResponse.model_validate(response.json())

    def create_calculation(self, calculation: CalculationCreate) -> CalculationResponse:
        """Create a new calculation.

        Parameters
        ----------
        calculation : CalculationCreate
            Calculation data to create

        Returns
        -------
        CalculationResponse
            Created calculation data
        """
        logger.debug(f"Creating calculation: {calculation}")
        response = self.call_api(
            endpoint=self.CALCULATIONS_ENDPOINT,
            method="POST",
            data=calculation.model_dump()
        )
        return CalculationResponse.model_validate(response.json())

    def get_heatmaps(self, calculation_id: int) -> HeatmapList:
        """Get all heatmaps for a specific calculation.

        Parameters
        ----------
        calculation_id : int
            ID of the calculation

        Returns
        -------
        HeatmapList
            List of heatmaps for the calculation
        """
        logger.debug(f"Getting heatmaps for calculation {calculation_id}")
        endpoint = self.HEATMAPS_ENDPOINT.format(calculation_id=calculation_id)
        response = self.call_api(endpoint=endpoint)
        return HeatmapList.model_validate(response.json())

    def add_heatmap(self, calculation_id: int, heatmap: HeatmapCreate) -> Dict[str, Any]:
        """Add a new heatmap to a calculation.

        Parameters
        ----------
        calculation_id : int
            ID of the calculation
        heatmap : HeatmapCreate
            Heatmap data to add

        Returns
        -------
        Dict[str, Any]
            Response with success message and IDs
        """
        logger.debug(f"Adding heatmap to calculation {calculation_id}")
        endpoint = self.HEATMAPS_ENDPOINT.format(calculation_id=calculation_id)
        response = self.call_api(
            endpoint=endpoint,
            method="POST",
            data=heatmap.model_dump()
        )
        return response.json()
