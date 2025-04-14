import unittest
import numpy as np
from functions.black_scholes import black_scholes
from functions.implied_volatility import (
    calculate_implied_volatility,
    generate_iv_surface,
    generate_theoretical_iv_surface,
)


class TestImpliedVolatility(unittest.TestCase):
    """Tests for implied volatility calculations."""

    def setUp(self):
        """Set up common test parameters."""
        self.S = 100.0  # Current stock price
        self.K = 100.0  # Strike price (at-the-money)
        self.T = 1.0  # Time to maturity in years
        self.r = 0.05  # Risk-free rate of 5%
        self.sigma = 0.2  # Volatility of 20%

    def test_calculate_implied_volatility(self):
        """Test that implied volatility calculation recovers the original volatility."""
        # Calculate option price using Black-Scholes with known volatility
        call_price = black_scholes(self.S, self.K, self.T, self.r, self.sigma, "call")
        put_price = black_scholes(self.S, self.K, self.T, self.r, self.sigma, "put")

        # Calculate implied volatility from these prices
        implied_vol_call = calculate_implied_volatility(
            call_price, self.S, self.K, self.T, self.r, "call"
        )
        implied_vol_put = calculate_implied_volatility(
            put_price, self.S, self.K, self.T, self.r, "put"
        )

        # Check that the implied volatility is close to the original volatility
        self.assertAlmostEqual(implied_vol_call, self.sigma, places=4)
        self.assertAlmostEqual(implied_vol_put, self.sigma, places=4)

    def test_generate_iv_surface(self):
        """Test generation of implied volatility surface from option prices."""
        # Create a grid of strikes and expirations
        strikes = np.linspace(90, 110, 5)
        expirations = np.linspace(0.5, 2.0, 4)

        # Generate option prices for each combination
        market_prices = np.zeros((len(expirations), len(strikes)))
        for i, T in enumerate(expirations):
            for j, K in enumerate(strikes):
                # Use a volatility that varies with strike and expiration
                # to create a more realistic surface
                vol = 0.2 + 0.05 * abs(K - self.S) / self.S + 0.02 * T
                market_prices[i, j] = black_scholes(self.S, K, T, self.r, vol, "call")

        # Generate implied volatility surface
        iv_surface = generate_iv_surface(
            market_prices, self.S, strikes, expirations, self.r, "call"
        )

        # Check that the surface has the expected shape
        self.assertEqual(iv_surface.shape, (len(expirations), len(strikes)))

        # Check that values are reasonable (between 0.1 and 0.5)
        self.assertTrue(np.all(iv_surface[~np.isnan(iv_surface)] >= 0.1))
        self.assertTrue(np.all(iv_surface[~np.isnan(iv_surface)] <= 0.5))

    def test_generate_theoretical_iv_surface(self):
        """Test generation of a theoretical implied volatility surface."""
        # Generate a theoretical IV surface
        strikes, expirations, iv_surface = generate_theoretical_iv_surface(
            self.S, 80, 120, 0.1, 2.0, self.r
        )

        # Check that the surface has the expected shape
        self.assertEqual(iv_surface.shape, (10, 20))  # Default steps

        # Check that values are reasonable
        self.assertTrue(np.all(iv_surface > 0))  # All values should be positive

        # Check that the volatility smile effect is present
        # (higher volatility for OTM and ITM options)
        middle_strike_idx = len(strikes) // 2
        for i in range(len(expirations)):
            self.assertTrue(
                iv_surface[i, 0] > iv_surface[i, middle_strike_idx]
            )  # ITM > ATM
            self.assertTrue(
                iv_surface[i, -1] > iv_surface[i, middle_strike_idx]
            )  # OTM > ATM


if __name__ == "__main__":
    unittest.main()
