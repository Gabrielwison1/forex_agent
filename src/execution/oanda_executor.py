from typing import Dict, Any
from datetime import datetime
from src.state import AgentState
from src.database.models import Trade, SessionLocal
from src.execution.oanda_client import OandaClient
import uuid

def oanda_executor_node(state: AgentState) -> Dict[str, Any]:
    """
    OANDA Executor Node - Places REAL trades in your Demo account.
    
    This replaces the mock executor. It:
    1. Checks if Risk Manager approved the trade
    2. Places a Market Order via OANDA v20 API
    3. Logs the trade to PostgreSQL
    4. Returns execution confirmation
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
            "reasoning_trace": ["[OANDA Executor]: Trade not executed (Risk Manager rejection)"]
        }
    
    # Extract order parameters
    action = order_details.get("action", "NONE")
    entry_price = order_details.get("entry_price", 0)
    stop_loss = order_details.get("stop_loss", 0)
    take_profit = order_details.get("take_profit", 0)
    lot_size = risk_assessment.get("lot_size", 0)
    
    # Convert action to OANDA units (positive = BUY, negative = SELL)
    # 1 lot = 100,000 units in forex
    units = int(lot_size * 100000) if action == "BUY" else int(-lot_size * 100000)
    
    # Initialize OANDA client
    try:
        client = OandaClient()
        
        # Place Market Order
        order_response = client.place_market_order(
            pair="EUR_USD",
            units=units,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        if "error" in order_response:
            # Order failed
            execution_result = {
                "executed": False,
                "reason": f"OANDA API Error: {order_response['error']}"
            }
            trace = f"[OANDA Executor]: ORDER FAILED - {order_response['error']}"
        else:
            # Order succeeded
            order_id = order_response.id
            actual_entry = float(order_response.price)
            
            # Log trade to database
            db = SessionLocal()
            try:
                new_trade = Trade(
                    pair="EUR_USD",
                    action=action,
                    entry_price=actual_entry,
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
                    "pair": "EUR_USD",
                    "action": action,
                    "entry_price": actual_entry,
                    "lot_size": lot_size,
                    "units": units
                }
                
                trace = (
                    f"[OANDA Executor]: TRADE EXECUTED - "
                    f"Order ID: {order_id}, DB ID: {trade_id}, "
                    f"{action} {lot_size} lots EUR/USD @ {actual_entry}"
                )
                
            except Exception as db_error:
                db.rollback()
                trace = f"[OANDA Executor]: Trade executed but DB logging failed - {str(db_error)}"
            finally:
                db.close()
                
    except Exception as e:
        execution_result = {
            "executed": False,
            "reason": f"Execution error: {str(e)}"
        }
        trace = f"[OANDA Executor]: EXECUTION FAILED - {str(e)}"
    
    return {
        "execution_result": execution_result,
        "reasoning_trace": [trace]
    }
