import unittest
import numpy as np
from black_scholes import black_scholes, generate_price_matrix


class TestBlackScholes(unittest.TestCase):
    """Tests for Black-Scholes option pricing model implementation."""

    def setUp(self):
        """Set up common test parameters."""
        self.S = 100.0  # Current stock price
        self.K = 100.0  # Strike price (at-the-money)
        self.T = 1.0  # Time to maturity in years
        self.r = 0.05  # Risk-free rate of 5%
        self.sigma = 0.2  # Volatility of 20%

    def test_call_option_price(self):
        """Test calculation of call option price."""
        # Expected value calculated using known Black-Scholes solution
        expected_call_price = 10.45

        # Calculate call price using our implementation
        call_price = black_scholes(self.S, self.K, self.T, self.r, self.sigma, "call")

        # Assert the calculated price is close to the expected value
        self.assertAlmostEqual(call_price, expected_call_price, places=2)

    def test_put_option_price(self):
        """Test calculation of put option price."""
        # Expected value calculated using known Black-Scholes solution
        expected_put_price = 5.57

        # Calculate put price using our implementation
        put_price = black_scholes(self.S, self.K, self.T, self.r, self.sigma, "put")

        # Assert the calculated price is close to the expected value
        self.assertAlmostEqual(put_price, expected_put_price, places=2)

    def test_put_call_parity(self):
        """Test that put-call parity holds for our implementation."""
        # Calculate call and put prices
        call_price = black_scholes(self.S, self.K, self.T, self.r, self.sigma, "call")
        put_price = black_scholes(self.S, self.K, self.T, self.r, self.sigma, "put")

        # Put-Call Parity: C - P = S - K * e^(-r*T)
        # Rearranged: C - P - S + K * e^(-r*T) = 0
        parity_value = (
            call_price - put_price - self.S + self.K * np.exp(-self.r * self.T)
        )

        # The result should be very close to zero if parity holds
        self.assertAlmostEqual(parity_value, 0.0, places=6)

    def test_invalid_option_type(self):
        """Test that an invalid option type raises a ValueError."""
        with self.assertRaises(ValueError):
            black_scholes(self.S, self.K, self.T, self.r, self.sigma, "invalid_type")

    def test_zero_volatility(self):
        """Test pricing with zero volatility (deterministic case)."""
        # With zero volatility, call option value is max(0, S - K*e^(-r*T))
        no_vol_call = black_scholes(self.S, self.K, self.T, self.r, 0.0, "call")
        expected_no_vol_call = max(0, self.S - self.K * np.exp(-self.r * self.T))
        self.assertAlmostEqual(no_vol_call, expected_no_vol_call, places=6)

        # With zero volatility, put option value is max(0, K*e^(-r*T) - S)
        no_vol_put = black_scholes(self.S, self.K, self.T, self.r, 0.0, "put")
        expected_no_vol_put = max(0, self.K * np.exp(-self.r * self.T) - self.S)
        self.assertAlmostEqual(no_vol_put, expected_no_vol_put, places=6)

    def test_zero_time_to_maturity(self):
        """Test pricing with zero time to maturity (immediate expiration)."""
        # At expiration, call option value is max(0, S - K)
        expiration_call = black_scholes(self.S, self.K, 0.0, self.r, self.sigma, "call")
        expected_expiration_call = max(0, self.S - self.K)
        self.assertAlmostEqual(expiration_call, expected_expiration_call, places=6)

        # At expiration, put option value is max(0, K - S)
        expiration_put = black_scholes(self.S, self.K, 0.0, self.r, self.sigma, "put")
        expected_expiration_put = max(0, self.K - self.S)
        self.assertAlmostEqual(expiration_put, expected_expiration_put, places=6)

    def test_deep_in_the_money_call(self):
        """Test pricing of a deep in-the-money call option."""
        # Stock price much higher than strike price
        S_high = 150.0
        call_price = black_scholes(S_high, self.K, self.T, self.r, self.sigma, "call")

        # For deep in-the-money calls, price approaches S - K*e^(-r*T)
        intrinsic_value = S_high - self.K * np.exp(-self.r * self.T)

        # The call price should be greater than the intrinsic value
        self.assertGreater(call_price, intrinsic_value)

        # But not too much greater (time value diminishes for deep ITM options)
        self.assertLess(call_price - intrinsic_value, 5.0)

    def test_deep_in_the_money_put(self):
        """Test pricing of a deep in-the-money put option."""
        # Stock price much lower than strike price
        S_low = 50.0
        put_price = black_scholes(S_low, self.K, self.T, self.r, self.sigma, "put")

        # For deep in-the-money puts, price approaches K*e^(-r*T) - S
        intrinsic_value = self.K * np.exp(-self.r * self.T) - S_low

        # The put price should be greater than the intrinsic value
        self.assertGreater(put_price, intrinsic_value)

        # But not too much greater (time value diminishes for deep ITM options)
        self.assertLess(put_price - intrinsic_value, 5.0)

    def test_generate_price_matrix(self):
        """Test the generation of price matrices for varying spot prices and volatilities."""
        # Define the ranges for spot price and volatility
        min_spot = 90.0
        max_spot = 110.0
        min_vol = 0.15
        max_vol = 0.25
        spot_steps = 5
        vol_steps = 4

        # Current prices for P&L calculation
        current_call_price = 10.45
        current_put_price = 5.57

        # Generate the matrices
        result = generate_price_matrix(
            min_spot,
            max_spot,
            min_vol,
            max_vol,
            self.K,
            self.T,
            self.r,
            current_call_price,
            current_put_price,
            spot_steps,
            vol_steps,
        )

        # Unpack the returned values
        spot_prices, volatilities, call_prices, put_prices, call_pnl, put_pnl = result

        # Check dimensions of output arrays
        self.assertEqual(len(spot_prices), spot_steps)
        self.assertEqual(len(volatilities), vol_steps)
        self.assertEqual(call_prices.shape, (vol_steps, spot_steps))
        self.assertEqual(put_prices.shape, (vol_steps, spot_steps))
        self.assertEqual(call_pnl.shape, (vol_steps, spot_steps))
        self.assertEqual(put_pnl.shape, (vol_steps, spot_steps))

        # Check that spot prices and volatilities are in the expected ranges
        self.assertAlmostEqual(min(spot_prices), min_spot)
        self.assertAlmostEqual(max(spot_prices), max_spot)
        self.assertAlmostEqual(min(volatilities), min_vol)
        self.assertAlmostEqual(max(volatilities), max_vol)

        # Verify P&L calculations for specific spot prices
        # For an at-the-money option (spot = strike = 100)
        _spot_index = spot_steps // 2  # Middle index for spot price array
        vol_index = vol_steps // 2  # Middle index for volatility array

        # At expiration, if spot = strike, both options are worthless
        # So P&L is just negative premium paid
        _expected_call_pnl_at_100 = -current_call_price
        _expected_put_pnl_at_100 = -current_put_price

        # Find the closest spot price to 100
        closest_to_100_idx = np.abs(spot_prices - 100.0).argmin()

        # Verify P&L calculation at that spot price
        # P&L may not be exactly -premium if spot price isn't exactly K
        spot_at_idx = spot_prices[closest_to_100_idx]
        expected_call_pnl = max(0, spot_at_idx - self.K) - current_call_price
        expected_put_pnl = max(0, self.K - spot_at_idx) - current_put_price

        self.assertAlmostEqual(
            call_pnl[vol_index, closest_to_100_idx], expected_call_pnl, places=6
        )
        self.assertAlmostEqual(
            put_pnl[vol_index, closest_to_100_idx], expected_put_pnl, places=6
        )


if __name__ == "__main__":
    unittest.main()
