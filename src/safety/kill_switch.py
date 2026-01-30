"""
Kill Switch Module - Emergency Trading Halt
Checks for the presence of a flag file to determine if trading is enabled.
"""
import os

FLAG_FILE = "TRADING_ENABLED.flag"

def is_trading_enabled() -> bool:
    """
    Check if trading is currently enabled.
    Returns True if flag file exists, False otherwise.
    """
    return os.path.exists(FLAG_FILE)

def enable_trading():
    """Create the flag file to enable trading."""
    with open(FLAG_FILE, 'w') as f:
        f.write("Trading is ACTIVE. Delete this file to emergency stop.\n")
    print("[KILL SWITCH] Trading ENABLED")

def disable_trading():
    """Remove the flag file to disable trading."""
    if os.path.exists(FLAG_FILE):
        os.remove(FLAG_FILE)
    print("[KILL SWITCH] Trading DISABLED")

if __name__ == "__main__":
    # Quick test
    print("=== KILL SWITCH TEST ===")
    print(f"Trading enabled: {is_trading_enabled()}")
    enable_trading()
    print(f"After enable: {is_trading_enabled()}")
    disable_trading()
    print(f"After disable: {is_trading_enabled()}")
