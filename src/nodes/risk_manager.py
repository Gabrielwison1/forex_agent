from typing import Dict, Any
from src.state import AgentState
from src.config import risk_config
from src.database.models import Trade, SessionLocal
from datetime import datetime, timedelta

def calculate_position_size(
    account_balance: float,
    risk_percentage: float,
    entry_price: float,
    stop_loss: float,
    pair: str = "EURUSD"
) -> float:
    """
    Calculate position size based on account risk.
    
    Formula: Lot Size = (Account Risk $) / (SL Distance in Pips × Pip Value)
    """
    # Calculate risk amount in dollars
    risk_amount = account_balance * risk_percentage
    
    # Calculate SL distance in pips (assuming 4-digit broker)
    sl_distance_pips = abs(entry_price - stop_loss) * 10000
    
    # Get pip value for the pair
    pip_value_per_lot = risk_config.get_pip_value(pair, 1.0)
    
    # Calculate lot size
    lot_size = risk_amount / (sl_distance_pips * pip_value_per_lot)
    
    # Round to nearest step and enforce limits
    lot_size = round(lot_size / risk_config.LOT_SIZE_STEP) * risk_config.LOT_SIZE_STEP
    lot_size = max(risk_config.MIN_LOT_SIZE, min(lot_size, risk_config.MAX_LOT_SIZE))
    
    return lot_size

def calculate_risk_reward_ratio(entry: float, sl: float, tp: float, action: str) -> float:
    """Calculate the Risk/Reward ratio."""
    if action == "BUY":
        risk = entry - sl
        reward = tp - entry
    else:  # SELL
        risk = sl - entry
        reward = entry - tp
    
    if risk <= 0:
        return 0
    
    return reward / risk

def risk_manager_node(state: AgentState) -> Dict[str, Any]:
    """
    Risk Management Node - Final validation before execution.
    
    This is a RULE-BASED node (no LLM). It validates:
    1. Position sizing based on account risk
    2. Stop Loss distance is reasonable
    3. Risk/Reward ratio meets minimum threshold
    4. Daily drawdown limit not exceeded
    """
    
    # Extract order details from Tactical Node
    order_details = state.get("order_details", {})
    trade_decision = state.get("trade_decision", "WAIT")
    
    # If Tactical said WAIT or CANCEL, pass through
    if trade_decision != "EXECUTE":
        return {
            "risk_assessment": {
                "approved": False,
                "rejection_reason": f"Tactical Node decision: {trade_decision}"
            },
            "reasoning_trace": [f"[Risk Manager]: Trade not approved by Tactical Node ({trade_decision})"]
        }
    
    # Extract order parameters
    action = order_details.get("action", "NONE")
    entry_price = order_details.get("entry_price", 0)
    stop_loss = order_details.get("stop_loss", 0)
    take_profit = order_details.get("take_profit", 0)
    
    # === NEW SAFETY CHECKS ===
    
    # Check 0: Max Open Positions
    try:
        db = SessionLocal()
        open_positions = db.query(Trade).filter(Trade.status == "OPEN").count()
        db.close()
        
        if open_positions >= risk_config.MAX_OPEN_POSITIONS:
            return {
                "risk_assessment": {
                    "approved": False,
                    "rejection_reason": f"Max open positions reached ({open_positions}/{risk_config.MAX_OPEN_POSITIONS})"
                },
                "reasoning_trace": [f"[Risk Manager]: REJECTED - Max positions limit reached"]
            }
    except Exception as e:
        print(f"[Risk Manager] Warning: Could not check open positions: {e}")
    
    # Check 0.5: Daily Drawdown Limit
    try:
        db = SessionLocal()
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_trades = db.query(Trade).filter(
            Trade.timestamp >= today_start,
            Trade.pnl != None
        ).all()
        
        daily_pnl = sum(t.pnl for t in today_trades)
        db.close()
        
        max_loss = risk_config.ACCOUNT_BALANCE * risk_config.MAX_DAILY_DRAWDOWN
        
        if daily_pnl < -max_loss:
            return {
                "risk_assessment": {
                    "approved": False,
                    "rejection_reason": f"Daily drawdown limit hit: ${daily_pnl:.2f} (max: ${-max_loss:.2f})"
                },
                "reasoning_trace": [f"[Risk Manager]: REJECTED - Daily drawdown limit exceeded"]
            }
    except Exception as e:
        print(f"[Risk Manager] Warning: Could not check daily drawdown: {e}")
    
    # Validation checks
    rejection_reason = None
    
    # Check 1: Valid order details
    if action == "NONE" or entry_price == 0:
        rejection_reason = "Invalid order details from Tactical Node"
    
    # Check 2: Calculate R/R ratio
    if not rejection_reason:
        rr_ratio = calculate_risk_reward_ratio(entry_price, stop_loss, take_profit, action)
        if rr_ratio < risk_config.MIN_RISK_REWARD_RATIO:
            rejection_reason = f"R/R ratio {rr_ratio:.2f} below minimum {risk_config.MIN_RISK_REWARD_RATIO}"
    
    # Check 3: Calculate position size
    lot_size = 0
    risk_amount = 0
    if not rejection_reason:
        lot_size = calculate_position_size(
            account_balance=risk_config.ACCOUNT_BALANCE,
            risk_percentage=risk_config.MAX_RISK_PER_TRADE,
            entry_price=entry_price,
            stop_loss=stop_loss,
            pair="EURUSD"
        )
        
        # Calculate actual risk amount
        sl_distance_pips = abs(entry_price - stop_loss) * 10000
        pip_value = risk_config.get_pip_value("EURUSD", lot_size)
        risk_amount = sl_distance_pips * pip_value
        risk_percentage = (risk_amount / risk_config.ACCOUNT_BALANCE) * 100
    
    # Prepare assessment
    approved = rejection_reason is None
    
    risk_assessment = {
        "approved": approved,
        "lot_size": lot_size,
        "adjusted_sl": stop_loss,
        "adjusted_tp": take_profit,
        "risk_amount": risk_amount,
        "risk_percentage": risk_percentage if not rejection_reason else 0,
        "reward_risk_ratio": rr_ratio if not rejection_reason else 0,
        "rejection_reason": rejection_reason
    }
    
    # Create reasoning trace
    if approved:
        trace = (
            f"[Risk Manager]: APPROVED - "
            f"Lot Size: {lot_size}, Risk: ${risk_amount:.2f} ({risk_percentage:.2f}%), "
            f"R/R: {rr_ratio:.2f}"
        )
    else:
        trace = f"[Risk Manager]: REJECTED - {rejection_reason}"
    
    return {
        "risk_assessment": risk_assessment,
        "reasoning_trace": [trace]
    }
