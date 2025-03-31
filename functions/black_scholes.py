import numpy as np
from scipy.stats import norm


def black_scholes(S, K, T, r, sigma, option_type="call"):
    """
    Calculate Black-Scholes option price for a call or put option.

    Parameters:
    -----------
    S : float
        Current stock price
    K : float
        Strike price
    T : float
        Time to maturity in years
    r : float
        Risk-free interest rate (annual)
    sigma : float
        Volatility of the underlying asset
    option_type : str
        Type of option - 'call' or 'put'

    Returns:
    --------
    float
        Option price
    """
    # Handle edge cases first
    option_type = option_type.lower()

    # For zero time to maturity, return intrinsic value
    if T <= 0:
        if option_type == "call":
            return max(0, S - K)
        elif option_type == "put":
            return max(0, K - S)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

    # For zero volatility, return deterministic value
    if sigma <= 0:
        if option_type == "call":
            return max(0, S - K * np.exp(-r * T))
        elif option_type == "put":
            return max(0, K * np.exp(-r * T) - S)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

    # Standard Black-Scholes calculation for normal cases
    # Calculate d1 and d2
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    # Calculate option price based on type
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    return price


def generate_price_matrix(
    min_spot,
    max_spot,
    min_vol,
    max_vol,
    K,
    T,
    r,
    current_call_price,
    current_put_price,
    spot_steps=10,
    vol_steps=10,
):
    """
    Generate matrices of call and put prices for a range of spot prices and volatilities.
    Also calculate P&L matrices based on current option prices and spot price changes.

    Parameters:
    -----------
    min_spot, max_spot : float
        Range of spot prices
    min_vol, max_vol : float
        Range of volatilities
    K : float
        Strike price
    T : float
        Time to maturity in years
    r : float
        Risk-free interest rate
    current_call_price : float
        Current price of the call option for P&L calculation
    current_put_price : float
        Current price of the put option for P&L calculation
    spot_steps, vol_steps : int
        Number of steps in the spot price and volatility grids

    Returns:
    --------
    tuple
        (spot_prices, volatilities, call_prices, put_prices, call_pnl_matrix, put_pnl_matrix)
    """
    # Create grids for spot prices and volatilities
    spot_prices = np.linspace(min_spot, max_spot, spot_steps)
    volatilities = np.linspace(min_vol, max_vol, vol_steps)

    # Initialize matrices for call and put prices
    call_prices = np.zeros((vol_steps, spot_steps))
    put_prices = np.zeros((vol_steps, spot_steps))

    # Initialize P&L matrices
    call_pnl_matrix = np.zeros((vol_steps, spot_steps))
    put_pnl_matrix = np.zeros((vol_steps, spot_steps))

    # Calculate option prices and P&L for each combination of spot price and volatility
    for i, vol in enumerate(volatilities):
        for j, spot in enumerate(spot_prices):
            # Calculate option prices
            call_price = black_scholes(spot, K, T, r, vol, "call")
            put_price = black_scholes(spot, K, T, r, vol, "put")

            call_prices[i, j] = call_price
            put_prices[i, j] = put_price

            # Calculate P&L for call option buyer at expiration:
            # If at expiration, a call option is worth max(0, spot - strike)
            # So P&L = max(0, spot - strike) - premium_paid
            call_pnl_matrix[i, j] = max(0, spot - K) - current_call_price

            # Calculate P&L for put option buyer at expiration:
            # If at expiration, a put option is worth max(0, strike - spot)
            # So P&L = max(0, strike - spot) - premium_paid
            put_pnl_matrix[i, j] = max(0, K - spot) - current_put_price

    return (
        spot_prices,
        volatilities,
        call_prices,
        put_prices,
        call_pnl_matrix,
        put_pnl_matrix,
    )
