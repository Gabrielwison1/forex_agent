"""
Risk Management Configuration
Defines the safety parameters for the trading agent.
"""

# Account Settings
ACCOUNT_BALANCE = 10000  # USD (Update this with your actual account size)
ACCOUNT_CURRENCY = "USD"

# Risk Parameters
MAX_RISK_PER_TRADE = 0.01  # 1% of account per trade
MIN_RISK_REWARD_RATIO = 2.0  # Minimum 1:2 R/R
MAX_DAILY_DRAWDOWN = 0.03  # 3% max daily loss
MAX_OPEN_POSITIONS = 3  # Maximum concurrent trades

# Position Sizing
MIN_LOT_SIZE = 0.01  # Micro lot
MAX_LOT_SIZE = 1.0  # Standard lot
LOT_SIZE_STEP = 0.01  # Increment size

# Stop Loss Rules
MIN_SL_DISTANCE_PIPS = 10  # Minimum 10 pips
MAX_SL_DISTANCE_PIPS = 100  # Maximum 100 pips

# Forex Specific
PIP_VALUE_PER_LOT = {
    "EURUSD": 10,  # $10 per pip for 1 standard lot
    "GBPUSD": 10,
    "USDJPY": 9.09,  # Approximate
    "AUDUSD": 10,
}

def get_pip_value(pair: str, lot_size: float = 1.0) -> float:
    """Get pip value for a currency pair."""
    base_value = PIP_VALUE_PER_LOT.get(pair, 10)
    return base_value * lot_size
