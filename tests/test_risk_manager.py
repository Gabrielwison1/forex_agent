import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.nodes.risk_manager import calculate_position_size, calculate_risk_reward_ratio, risk_manager_node
from src.config import risk_config

def test_position_sizing():
    """Test position size calculation."""
    print("TEST 1: Position Sizing Calculation")
    
    # Scenario: $10,000 account, 1% risk, 20 pip SL
    account_balance = 10000
    risk_percentage = 0.01
    entry_price = 1.1000
    stop_loss = 1.0980  # 20 pips
    
    lot_size = calculate_position_size(account_balance, risk_percentage, entry_price, stop_loss)
    
    # Expected: $100 risk / (20 pips * $10/pip) = 0.5 lots
    print(f"  Account: ${account_balance}, Risk: {risk_percentage*100}%")
    print(f"  Entry: {entry_price}, SL: {stop_loss} (20 pips)")
    print(f"  Calculated Lot Size: {lot_size}")
    
    assert 0.4 <= lot_size <= 0.6, f"Expected ~0.5 lots, got {lot_size}"
    print("  PASS\n")

def test_risk_reward_ratio():
    """Test R/R ratio calculation."""
    print("TEST 2: Risk/Reward Ratio Calculation")
    
    # Scenario: BUY at 1.1000, SL at 1.0980, TP at 1.1040
    entry = 1.1000
    sl = 1.0980
    tp = 1.1040
    
    rr_ratio = calculate_risk_reward_ratio(entry, sl, tp, "BUY")
    
    # Expected: 40 pips reward / 20 pips risk = 2.0
    print(f"  BUY Entry: {entry}, SL: {sl}, TP: {tp}")
    print(f"  Calculated R/R: {rr_ratio:.2f}")
    
    assert rr_ratio == 2.0, f"Expected 2.0, got {rr_ratio}"
    print("  PASS\n")

def test_trade_approval():
    """Test Risk Manager approves good trade."""
    print("TEST 3: Trade Approval (Good Setup)")
    
    state = {
        "trade_decision": "EXECUTE",
        "order_details": {
            "action": "BUY",
            "entry_price": 1.1000,
            "stop_loss": 1.0980,
            "take_profit": 1.1040
        },
        "reasoning_trace": []
    }
    
    result = risk_manager_node(state)
    
    print(f"  Trade Decision: {state['trade_decision']}")
    print(f"  R/R Ratio: {result['risk_assessment']['reward_risk_ratio']:.2f}")
    print(f"  Approved: {result['risk_assessment']['approved']}")
    print(f"  Reasoning: {result['reasoning_trace'][0]}")
    
    assert result['risk_assessment']['approved'] == True, "Trade should be approved"
    print("  PASS\n")

def test_trade_rejection_low_rr():
    """Test Risk Manager rejects trade with low R/R."""
    print("TEST 4: Trade Rejection (Low R/R)")
    
    state = {
        "trade_decision": "EXECUTE",
        "order_details": {
            "action": "BUY",
            "entry_price": 1.1000,
            "stop_loss": 1.0980,
            "take_profit": 1.1020  # Only 1:1 R/R
        },
        "reasoning_trace": []
    }
    
    result = risk_manager_node(state)
    
    print(f"  Trade Decision: {state['trade_decision']}")
    print(f"  R/R Ratio: {result['risk_assessment']['reward_risk_ratio']:.2f}")
    print(f"  Approved: {result['risk_assessment']['approved']}")
    print(f"  Rejection Reason: {result['risk_assessment']['rejection_reason']}")
    
    assert result['risk_assessment']['approved'] == False, "Trade should be rejected"
    assert "R/R ratio" in result['risk_assessment']['rejection_reason'], "Should mention R/R ratio"
    print("  PASS\n")

def test_tactical_wait_passthrough():
    """Test Risk Manager passes through WAIT decision."""
    print("TEST 5: Tactical WAIT Passthrough")
    
    state = {
        "trade_decision": "WAIT",
        "order_details": {},
        "reasoning_trace": []
    }
    
    result = risk_manager_node(state)
    
    print(f"  Trade Decision: {state['trade_decision']}")
    print(f"  Approved: {result['risk_assessment']['approved']}")
    print(f"  Reasoning: {result['reasoning_trace'][0]}")
    
    assert result['risk_assessment']['approved'] == False, "Should not approve WAIT"
    print("  PASS\n")

if __name__ == "__main__":
    print("=" * 60)
    print("RISK MANAGER TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        test_position_sizing()
        test_risk_reward_ratio()
        test_trade_approval()
        test_trade_rejection_low_rr()
        test_tactical_wait_passthrough()
        
        print("=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nEXECUTION ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
