import numpy as np
from scipy.optimize import brentq
from functions.black_scholes import black_scholes


def calculate_implied_volatility(
    option_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str = "call",
    precision: float = 0.00001,
    max_iterations: int = 100,
    min_vol: float = 0.001,
    max_vol: float = 5.0,
) -> float:
    """
    Calculate implied volatility using the Brent method.

    Parameters:
    -----------
    option_price : float
        Market price of the option
    S : float
        Current stock price
    K : float
        Strike price
    T : float
        Time to maturity in years
    r : float
        Risk-free interest rate (annual)
    option_type : str
        Type of option - 'call' or 'put'
    precision : float
        Desired precision for the result
    max_iterations : int
        Maximum number of iterations
    min_vol, max_vol : float
        Range for volatility search

    Returns:
    --------
    float
        Implied volatility
    """
    # Handle edge cases
    if T <= 0:
        return np.nan  # No implied volatility for expired options

    # For call options, check if price is below intrinsic value
    if option_type.lower() == "call" and option_price < max(0, S - K * np.exp(-r * T)):
        return np.nan

    # For put options, check if price is below intrinsic value
    if option_type.lower() == "put" and option_price < max(0, K * np.exp(-r * T) - S):
        return np.nan

    # Define the objective function: difference between BS price and market price
    def objective(sigma):
        return black_scholes(S, K, T, r, sigma, option_type) - option_price

    try:
        # Use Brent's method to find the implied volatility
        implied_vol = brentq(
            objective, min_vol, max_vol, rtol=precision, maxiter=max_iterations
        )
        return implied_vol
    except ValueError:
        # If the solution is not in the range, return NaN
        return np.nan


def generate_iv_surface(
    market_prices: np.ndarray,
    S: float,
    strikes: np.ndarray,
    expirations: np.ndarray,
    r: float,
    option_type: str = "call",
) -> np.ndarray:
    """
    Generate an implied volatility surface from a grid of option prices.

    Parameters:
    -----------
    market_prices : np.ndarray
        2D array of option prices with shape (len(expirations), len(strikes))
    S : float
        Current stock price
    strikes : np.ndarray
        Array of strike prices
    expirations : np.ndarray
        Array of expiration times in years
    r : float
        Risk-free interest rate (annual)
    option_type : str
        Type of option - 'call' or 'put'

    Returns:
    --------
    np.ndarray
        2D array of implied volatilities with shape (len(expirations), len(strikes))
    """
    # Initialize the implied volatility surface
    iv_surface = np.zeros_like(market_prices)

    # Calculate implied volatility for each combination of strike and expiration
    for i, T in enumerate(expirations):
        for j, K in enumerate(strikes):
            iv_surface[i, j] = calculate_implied_volatility(
                market_prices[i, j], S, K, T, r, option_type
            )

    return iv_surface


def generate_theoretical_iv_surface(
    S: float,
    min_strike: float,
    max_strike: float,
    min_expiry: float,
    max_expiry: float,
    r: float,
    base_volatility: float = 0.2,
    strike_steps: int = 20,
    expiry_steps: int = 10,
    smile_factor: float = 0.4,
    term_structure_factor: float = 0.1,
) -> tuple:
    """
    Generate a theoretical implied volatility surface with smile and term structure effects.

    Parameters:
    -----------
    S : float
        Current stock price
    min_strike, max_strike : float
        Range of strike prices
    min_expiry, max_expiry : float
        Range of expiration times in years
    r : float
        Risk-free interest rate (annual)
    base_volatility : float
        Base volatility level
    strike_steps, expiry_steps : int
        Number of steps in the strike and expiry grids
    smile_factor : float
        Factor controlling the strength of the volatility smile
    term_structure_factor : float
        Factor controlling the term structure effect

    Returns:
    --------
    tuple
        (strikes, expirations, iv_surface)
    """
    # Create grids for strikes and expirations
    strikes = np.linspace(min_strike, max_strike, strike_steps)
    expirations = np.linspace(min_expiry, max_expiry, expiry_steps)

    # Initialize the implied volatility surface
    iv_surface = np.zeros((expiry_steps, strike_steps))

    # Calculate moneyness for each strike
    moneyness = strikes / S

    # Generate a theoretical IV surface with smile and term structure
    for i, T in enumerate(expirations):
        for j, K in enumerate(strikes):
            # Volatility smile effect (U-shaped curve with minimum at ATM)
            smile = smile_factor * (moneyness[j] - 1) ** 2

            # Term structure effect (volatility increases with time to expiry)
            term = base_volatility * (1 + term_structure_factor * np.sqrt(T))

            # Combine effects
            iv_surface[i, j] = term + smile

    return strikes, expirations, iv_surface
