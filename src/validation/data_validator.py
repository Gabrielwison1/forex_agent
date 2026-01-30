"""
Data Validator Module - Ensures Data Quality
Validates market data from OANDA before use in trading decisions.
"""
from typing import Dict, Any, List, Tuple

class DataValidator:
    """Validates market data quality."""
    
    MAX_SPREAD_PIPS = 5.0  # Maximum acceptable spread
    MIN_CANDLES = 10  # Minimum number of candles required
    
    @staticmethod
    def validate_price(price_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate current price data."""
        if "error" in price_data:
            return False, f"Price error: {price_data['error']}"
        
        bid = price_data.get("bid", 0)
        ask = price_data.get("ask", 0)
        
        # Check for zero or negative prices
        if bid <= 0 or ask <= 0:
            return False, f"Invalid price: bid={bid}, ask={ask}"
        
        # Check for unreasonable spread
        spread_pips = abs(ask - bid) * 10000
        if spread_pips > DataValidator.MAX_SPREAD_PIPS:
            return False, f"Excessive spread: {spread_pips:.1f} pips (max: {DataValidator.MAX_SPREAD_PIPS})"
        
        # Check bid < ask
        if bid >= ask:
            return False, f"Invalid quote: bid ({bid}) >= ask ({ask})"
        
        return True, "Price data valid"
    
    @staticmethod
    def validate_candles(candles: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Validate historical candle data."""
        if not candles:
            return False, "No candles returned"
        
        if len(candles) < DataValidator.MIN_CANDLES:
            return False, f"Insufficient candles: {len(candles)} (min: {DataValidator.MIN_CANDLES})"
        
        # Check for corrupt candles
        for i, candle in enumerate(candles):
            try:
                o, h, l, c = candle['open'], candle['high'], candle['low'], candle['close']
                
                # Basic OHLC validation
                if not (l <= o <= h and l <= c <= h):
                    return False, f"Invalid OHLC at index {i}: O={o}, H={h}, L={l}, C={c}"
                
                # Check for zero prices
                if any(p <= 0 for p in [o, h, l, c]):
                    return False, f"Zero price detected at index {i}"
                    
            except (KeyError, TypeError) as e:
                return False, f"Malformed candle at index {i}: {str(e)}"
        
        return True, f"{len(candles)} candles valid"
    
    @staticmethod
    def validate_technical_indicators(tech_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate calculated technical indicators."""
        required_fields = ["Current_Price", "H1_Trend", "H1_Close"]
        
        for field in required_fields:
            if field not in tech_data:
                return False, f"Missing required field: {field}"
        
        # Check price is reasonable
        price = tech_data.get("Current_Price", 0)
        if price <= 0 or price > 10.0:  # EUR/USD should be between 0 and 10
            return False, f"Unreasonable price: {price}"
        
        return True, "Technical indicators valid"

# Singleton instance
validator = DataValidator()
