# Black-Scholes Option Pricing Model
[Project Idea From CJ](https://youtu.be/lY-NP4X455U?si=ixc8cO5N-SBil_F9)

This application implements the Black-Scholes option pricing model with interactive visualizations using Streamlit, a FastAPI backend, and a Python SDK.
## [Live Preview on Streamlit cloud](https://black-sholes-h4zchf4vphtx4pxce5vsjd.streamlit.app/)
## Features
- Calculate call and put option prices using the Black-Scholes model
- Interactive inputs for all parameters (current price, strike price, time to maturity, volatility, risk-free rate)
- Visualize option prices as heatmaps showing the relationship between spot price and volatility
- Profit & Loss heatmaps showing potential returns at different stock prices and premium levels
- Calculate button to explicitly trigger calculations and store results in SQLite database
- Historical calculation storage and retrieval
- Adjustable parameters for heatmap visualization
- FastAPI backend with JWT authentication and OpenAPI documentation
- Python SDK for programmatic access to the API
- Streamlit frontend for interactive visualization
## Installation
1. Clone this repository
2. Install the required dependencies [uv recommended](https://docs.astral.sh/uv):
```bash
# use the lockfile
uv sync
uv lock --check
# or install manually
uv pip install -r requirements.txt # uv add -r requirements.txt works too.
```
## Usage
### Running with Streamlit directly
To run the application directly with Streamlit:
```bash
# use the justfile!
just streamlit
# Or use the environment
source .venv/bin/activate && streamlit run streamlit_app.py
```
This will start the Streamlit server and open the application on port 8501.
### Running with FastAPI
To run the application with FastAPI to save calculations in the database under a login or to see the API documentation. 

```bash
# use the justfile!
just runapp
# Or use uvicorn directly
uvicorn api.fastapi_app:app --reload
```

This will start the FastAPI server on port 5000 and the Streamlit application on port 8501. You can access the application by navigating to:
- FastAPI entry point: http://localhost:5000
- Streamlit direct access: http://localhost:8501
- API documentation: http://localhost:5000/docs or http://localhost:5000/redoc
## API Endpoints
The FastAPI application provides the following API endpoints:
### Streamlit Management
- `/`: Redirects to the Streamlit application
- `/status`: Returns the status of the Streamlit application
- `/start`: Starts the Streamlit application if it's not already running
- `/stop`: Stops the Streamlit application
- `/restart`: Restarts the Streamlit application
### Authentication
- `/api/auth/register`: Register a new user
- `/api/auth/login`: Login and get a JWT token
### Calculations
- `/api/calculations`: List, create, and manage calculations
- `/api/calculations/{id}`: Get a specific calculation
### Heatmaps
- `/api/calculation/{id}/heatmaps`: Get or add heatmaps for a calculation
## Black-Scholes Model

The Black-Scholes model is a mathematical model used to determine the theoretical price of European-style options. The model assumes that the price of the underlying asset follows a geometric Brownian motion with some constant drift and volatility.
### Parameters
- **Current Price (S)**: The current price of the underlying asset
- **Strike Price (K)**: The price at which the option can be exercised
- **Time to Maturity (T)**: The time until the option expires (in years)
- **Volatility (σ)**: The standard deviation of the underlying asset's returns
- **Risk-Free Rate (r)**: The risk-free interest rate
### Formulas
The Black-Scholes formula for a call option is:
```
C = S * N(d1) - K * e^(-r * T) * N(d2)
```
The formula for a put option is:
```
P = K * e^(-r * T) * N(-d2) - S * N(-d1)
```
Where:
```
d1 = (ln(S/K) + (r + σ^2/2) * T) / (σ * √T)
d2 = d1 - σ * √T
```
And N(x) is the cumulative distribution function of the standard normal distribution.
### P&L Calculation at Expiration
For a call option buyer:
```
P&L = max(0, spot_price - strike_price) - premium_paid
```
For a put option buyer:
```
P&L = max(0, strike_price - spot_price) - premium_paid
```
### Implied Volatility
Implied volatility is the volatility value that, when plugged into the Black-Scholes model, yields a theoretical option price equal to the current market price of that option. It represents the market's expectation of future volatility.

The implied volatility surface shows how implied volatility varies with:
- **Strike Price**: The volatility smile/skew effect (higher implied volatility for out-of-the-money options)
- **Time to Expiration**: The term structure effect (how implied volatility changes with time to expiration)

This surface is crucial for understanding market dynamics and pricing options more accurately, especially for exotic derivatives.

## SDK Usage
The SDK provides a Python client for interacting with the API:

```python
from blacksholes.bs_client import BlackScholesClient
from blacksholes.bs_config import BlackScholesConfig
from blacksholes.schemas import CalculationCreate

# Initialize the client
config = BlackScholesConfig(bs_base_url="http://localhost:5000")
client = BlackScholesClient(config)

# Register and login
client.register(username="user", password="password")
token = client.login(username="user", password="password")

# Create a calculation
calculation = CalculationCreate(
    spot_price=100.0,
    strike_price=100.0,
    time_to_maturity=1.0,
    volatility=0.2,
    risk_free_rate=0.05,
    call_price=10.45,
    put_price=5.57
)
result = client.create_calculation(calculation)

# Get calculations
calculations = client.get_calculations(limit=10, offset=0)
```

## API Documentation

See [API Documentation](api/README.md) for complete details on how to use the API.

Interactive API documentation is available at:
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

## Testing

To run the tests:

```bash
# use the justfile!
just test
# Or use pytest directly
pytest src/blacksholes/tests/
```
The test suite includes unit tests for both the API and SDK components.
thanks for reading made with <3
