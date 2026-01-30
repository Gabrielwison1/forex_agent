"""
Test Suite for Safety Modules
Validates kill switch, circuit breaker, and data validator functionality.
"""
import unittest
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.safety.kill_switch import is_trading_enabled, enable_trading, disable_trading
from src.safety.circuit_breaker import CircuitBreaker
from src.validation.data_validator import DataValidator

class TestKillSwitch(unittest.TestCase):
    """Test kill switch functionality."""
    
    def setUp(self):
        """Clean up before each test."""
        disable_trading()
    
    def tearDown(self):
        """Clean up after each test."""
        disable_trading()
    
    def test_initial_state(self):
        """Kill switch should be disabled initially."""
        self.assertFalse(is_trading_enabled())
    
    def test_enable_trading(self):
        """Should create flag file and enable trading."""
        enable_trading()
        self.assertTrue(is_trading_enabled())
        self.assertTrue(os.path.exists("TRADING_ENABLED.flag"))
    
    def test_disable_trading(self):
        """Should remove flag file and disable trading."""
        enable_trading()
        disable_trading()
        self.assertFalse(is_trading_enabled())
        self.assertFalse(os.path.exists("TRADING_ENABLED.flag"))

class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker functionality."""
    
    def setUp(self):
        """Create fresh circuit breaker for each test."""
        self.cb = CircuitBreaker(max_consecutive_failures=3, reset_window_minutes=1)
    
    def test_initial_state(self):
        """Circuit breaker should be closed initially."""
        self.assertTrue(self.cb.can_attempt())
        self.assertFalse(self.cb.is_open)
    
    def test_success_resets_counter(self):
        """Recording success should reset failure count."""
        self.cb.record_failure()
        self.cb.record_failure()
        self.cb.record_success()
        self.assertEqual(self.cb.failure_count, 0)
        self.assertTrue(self.cb.can_attempt())
    
    def test_opens_after_max_failures(self):
        """Circuit should open after max failures."""
        for _ in range(3):
            self.cb.record_failure()
        
        self.assertTrue(self.cb.is_open)
        self.assertFalse(self.cb.can_attempt())
    
    def test_status_reporting(self):
        """Should report accurate status."""
        self.cb.record_failure()
        status = self.cb.get_status()
        
        self.assertEqual(status['failure_count'], 1)
        self.assertEqual(status['max_failures'], 3)
        self.assertFalse(status['is_open'])

class TestDataValidator(unittest.TestCase):
    """Test data validation functionality."""
    
    def setUp(self):
        """Create validator instance."""
        self.validator = DataValidator()
    
    def test_valid_price_data(self):
        """Should accept valid price data."""
        price_data = {
            "bid": 1.0500,
            "ask": 1.0502,
            "timestamp": "2024-01-27T12:00:00Z"
        }
        
        is_valid, message = self.validator.validate_price(price_data)
        self.assertTrue(is_valid)
    
    def test_invalid_price_zero(self):
        """Should reject zero prices."""
        price_data = {
            "bid": 0.0,
            "ask": 1.0502
        }
        
        is_valid, message = self.validator.validate_price(price_data)
        self.assertFalse(is_valid)
        self.assertIn("Invalid price", message)
    
    def test_excessive_spread(self):
        """Should reject excessive spread."""
        price_data = {
            "bid": 1.0500,
            "ask": 1.0600  # 100 pips spread
        }
        
        is_valid, message = self.validator.validate_price(price_data)
        self.assertFalse(is_valid)
        self.assertIn("Excessive spread", message)
    
    def test_bid_ask_inversion(self):
        """Should reject inverted bid/ask."""
        price_data = {
            "bid": 1.0502,
            "ask": 1.0500
        }
        
        is_valid, message = self.validator.validate_price(price_data)
        self.assertFalse(is_valid)
        self.assertIn("Invalid quote", message)
    
    def test_valid_candles(self):
        """Should accept valid candle data."""
        candles = [
            {"open": 1.05, "high": 1.06, "low": 1.04, "close": 1.055, "time": "2024-01-27T12:00:00Z"},
            {"open": 1.055, "high": 1.058, "low": 1.053, "close": 1.057, "time": "2024-01-27T13:00:00Z"}
        ] * 10  # 20 candles
        
        is_valid, message = self.validator.validate_candles(candles)
        self.assertTrue(is_valid)
    
    def test_insufficient_candles(self):
        """Should reject insufficient candles."""
        candles = [
            {"open": 1.05, "high": 1.06, "low": 1.04, "close": 1.055}
        ]
        
        is_valid, message = self.validator.validate_candles(candles)
        self.assertFalse(is_valid)
        self.assertIn("Insufficient candles", message)
    
    def test_invalid_ohlc(self):
        """Should reject invalid OHLC relationships."""
        candles = [
            {"open": 1.05, "high": 1.04, "low": 1.06, "close": 1.055}  # High < Low
        ] * 10
        
        is_valid, message = self.validator.validate_candles(candles)
        self.assertFalse(is_valid)
        self.assertIn("Invalid OHLC", message)

if __name__ == '__main__':
    unittest.main()
