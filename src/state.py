from typing import TypedDict, Annotated, List, Dict, Any, Optional
from enum import Enum
import operator

class AgentState(TypedDict):
    """
    The shared state of the Forex Agent.
    """
    # Market Data Inputs
    technical_indicators: Dict[str, Any]
    macro_sentiment: Dict[str, Any]
    risk_environment: Dict[str, Any]
    
    # Decision States
    current_bias: str # "BIAS_LONG", "BIAS_SHORT", "RISK_OFF"
    market_structure: str # e.g. "TRENDING", "RANGING"
    
    # Reasoning Logs (Append-only)
    reasoning_trace: Annotated[List[str], operator.add]
    
    # Execution Details
    active_trade: Optional[Dict[str, Any]]
    trade_decision: str # EXECUTE, WAIT, CANCEL
    order_details: Dict[str, Any] # Entry, SL, TP
    risk_assessment: Dict[str, Any] # Risk Manager output
    execution_result: Dict[str, Any] # Executor output
