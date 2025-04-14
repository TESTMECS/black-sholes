# Black-Scholes Option Pricing Model

This application implements the Black-Scholes option pricing model with interactive visualizations using Streamlit and Flask.

## Features

- Calculate call and put option prices using the Black-Scholes model
- Interactive inputs for all parameters (current price, strike price, time to maturity, volatility, risk-free rate)
- Visualize option prices as heatmaps showing the relationship between spot price and volatility
- Profit & Loss heatmaps showing potential returns at different stock prices and premium levels
- Calculate button to explicitly trigger calculations and store results in SQLite database
- Historical calculation storage and retrieval
- Adjustable parameters for heatmap visualization
- Flask server to host the Streamlit application

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
source .venv/bin/activate && streamlit run app.py
```

This will start the Streamlit server and open the application on port 8501.

### Running with Flask

To run the application with Flask (which will automatically start Streamlit):

```bash
python flask_app.py
```

This will start the Flask server on port 5000 and the Streamlit application on port 8501. You can access the application by navigating to:

- Flask entry point: http://localhost:5000
- Streamlit direct access: http://localhost:8501

## API Endpoints

The Flask application provides the following API endpoints:

- `/`: Redirects to the Streamlit application
- `/status`: Returns the status of the Streamlit application
- `/start`: Starts the Streamlit application if it's not already running
- `/stop`: Stops the Streamlit application
- `/restart`: Restarts the Streamlit application

## Recent Enhancements

- **Implied Volatility Surface**: 3D visualization of implied volatility across strikes and expirations
  - Interactive 3D surface plots showing volatility smile and term structure
  - Theoretical surface generation with customizable parameters
  - Multiple visualization options (3D surface, heatmap, contour plot)
  - Support for uploading market data
- **Improved Profit & Loss Visualization**: Enhanced P&L heatmaps that show potential returns based on:
  - Stock price at expiration (x-axis)
  - Option premium paid (y-axis)
  - Visual reference lines for current premium and strike price
- **Database Integration**: Added SQLite storage for:
  - Storing heatmap data for later retrieval
  - Historical comparison of different option scenarios
- **UI Improvements**:
  - Explicit CALCULATE button for intentional calculations
  - Sidebar history panel showing past calculations
  - Improved color scales and data visualization
  - Better formatted annotations in heatmaps
  - Multi-page navigation for advanced features

## Black-Scholes Model

The Black-Scholes model is a mathematical model used to determine the theoretical price of European-style options. The model assumes that the price of the underlying asset follows a geometric Brownian motion with constant drift and volatility.

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

## Future Enhancements

The following features are planned for future development:

### Advanced Option Strategies

- **Option Spreads**: Implement bull/bear spreads, butterfly spreads, and iron condors
- **Multi-leg Strategies**: Support for creating and evaluating complex option strategies
- **Strategy Builder**: Drag-and-drop interface for building custom option strategies

### Enhanced Analytics

- **Greeks Visualization**: Interactive displays for delta, gamma, theta, vega, and rho
- ~~**Implied Volatility Surface**: 3D visualization of implied volatility across strikes and expirations~~ ✅ Implemented
- **Monte Carlo Simulation**: Probability distributions of future option values
- **Scenario Analysis**: Stress testing options under different market conditions

### User Experience

- **Portfolio Management**: Save and manage multiple option positions
- **Mobile Responsive Design**: Optimize UI for mobile devices
- **Export Functionality**: Download calculations and charts as CSV/PDF

### Market Integration

- **Real-time Data**: Connect to market APIs for live option chain data
- **Historical Analysis**: Backtest strategies against historical market data
- **Volatility Forecast**: Predict future volatility based on historical patterns
- **Earnings Impact Analysis**: Model effects of earnings announcements on option prices

### Advanced Models

- **Heston Model**: Support for stochastic volatility
- **Jump-Diffusion Models**: Account for price jumps in underlying assets
- **Binomial/Trinomial Trees**: Alternative pricing methods for American options
- **SABR Model**: Advanced volatility modeling for interest rate options

### Educational Features

- **Interactive Tutorials**: Step-by-step guides for option concepts
- **Strategy Templates**: Pre-built examples of common trading strategies
- **Risk Explainers**: Visual explanations of option risks and rewards
- **Quiz Module**: Test understanding of option concepts

## TODO: API Access
- Use Fastapi, pydantic, and SQLAlchemy to create a RESTful API for the Black-Scholes application and let users access their saved calculations and heatmaps.
### Routes:
- JWT Authentication.
- Access the Database saved models for an authenticated user from the streamlit app. 
- Access our functions. 
### Documentation. 
- Auto generated with pydantic and OpenAPI. 
### SDK
- Python SDK to access our API. 


### Features:

- JWT-based authentication
- Access to all calculations and heatmaps
- Complete CRUD operations
- Rate limiting and security best practices

See [API Documentation](api/README.md) for complete details on how to use the API.
