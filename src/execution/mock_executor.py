from typing import Dict, Any
from datetime import datetime
from src.state import AgentState
from src.database.models import Trade, SessionLocal
import uuid

def mock_executor_node(state: AgentState) -> Dict[str, Any]:
    """
    Mock Executor Node - Simulates trade execution and logs to database.
    
    In production, this would be replaced with real OANDA API calls.
    For now, it:
    1. Checks if Risk Manager approved the trade
    2. Logs the trade to PostgreSQL
    3. Returns execution confirmation
    """
    
    # Extract data from state
    risk_assessment = state.get("risk_assessment", {})
    approved = risk_assessment.get("approved", False)
    order_details = state.get("order_details", {})
    reasoning_trace = state.get("reasoning_trace", [])
    
    # If not approved, skip execution
    if not approved:
        return {
            "execution_result": {
                "executed": False,
                "reason": "Trade rejected by Risk Manager"
            },
            "reasoning_trace": ["[Executor]: Trade not executed (Risk Manager rejection)"]
        }
    
    # Extract order parameters
    action = order_details.get("action", "NONE")
    entry_price = order_details.get("entry_price", 0)
    stop_loss = order_details.get("stop_loss", 0)
    take_profit = order_details.get("take_profit", 0)
    lot_size = risk_assessment.get("lot_size", 0)
    
    # Generate mock order ID
    order_id = f"MOCK-{uuid.uuid4().hex[:8].upper()}"
    
    # Log trade to database
    db = SessionLocal()
    try:
        new_trade = Trade(
            pair="EURUSD",  # Hardcoded for now, would come from state in production
            action=action,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            lot_size=lot_size,
            status="OPEN",
            reasoning_trace=reasoning_trace
        )
        
        db.add(new_trade)
        db.commit()
        db.refresh(new_trade)
        
        trade_id = new_trade.id
        
        execution_result = {
            "executed": True,
            "order_id": order_id,
            "trade_id": trade_id,
            "timestamp": datetime.utcnow().isoformat(),
            "pair": "EURUSD",
            "action": action,
            "entry_price": entry_price,
            "lot_size": lot_size
        }
        
        trace = (
            f"[Executor]: TRADE EXECUTED - "
            f"Order ID: {order_id}, DB ID: {trade_id}, "
            f"{action} {lot_size} lots EURUSD @ {entry_price}"
        )
        
    except Exception as e:
        db.rollback()
        execution_result = {
            "executed": False,
            "reason": f"Database error: {str(e)}"
        }
        trace = f"[Executor]: EXECUTION FAILED - {str(e)}"
    finally:
        db.close()
    
    return {
        "execution_result": execution_result,
        "reasoning_trace": [trace]
    }
