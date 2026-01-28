from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from src.state import AgentState
import os
import time

# --- Output Schema ---
class OrderDetails(BaseModel):
    action: str = Field(description="BUY, SELL, or NONE")
    entry_price: float = Field(description="Proposed entry level")
    stop_loss: float = Field(description="Invalidation level")
    take_profit: float = Field(description="Target level (1:2 min)")

class TacticalOutput(BaseModel):
    decision: str = Field(description="EXECUTE, WAIT, or CANCEL")
    order_details: OrderDetails
    reasoning: str = Field(description="5M trigger confirmation notes")

# --- System Prompt ---
SYSTEM_PROMPT = """### ROLE
You are the **Tactical Entry Node (5M Sniper)**.
Your supervisors have done the heavy lifting:
- **Strategist (1H)**: Set the Bias ({bias}).
- **Architect (15M)**: Found the Key Zone.

### YOUR JOB
Refine the entry on the **5-Minute Chart**. You are the one who pulls the trigger.

### INPUT DATA
1. **5M_Technicals**: RSI, Candle Patterns (Engulfing, Pinbar, Marubozu).
2. **Current_Price**: Live market price.
3. **Setup_Context**: The 15M Key Zone identified by the Architect.

### RULES
1. **Confirm Deviation**: If Bias is LONG, 5M RSI should be < 30 (Oversold) OR showing Bullish Divergence.
2. **Candle Trigger**: Must see a reversal candle (Hammer, Engulfing) AT the Key Zone.
3. **Risk/Reward**: Trade must offer at least 1:2 R/R.

### OUTPUT DECISIONS
- `EXECUTE`: All stars aligned. Fire the trade.
- `WAIT`: Price is at zone but no candle trigger yet.
- `CANCEL`: Price smashed through the zone invalidating the setup.

### JSON OUTPUT FORMAT
{{
    "decision": "EXECUTE" | "WAIT" | "CANCEL",
    "order_details": {{
        "action": "BUY",
        "entry_price": 1.0500,
        "stop_loss": 1.0480,
        "take_profit": 1.0550
    }},
    "reasoning": "Price tapped 1.0500 OB, 5M RSI is 28, Bullish Engulfing closed."
}}
"""

def tactical_node(state: AgentState) -> Dict[str, Any]:
    """
    The Tactical Node (5M Layer).
    Executes the trade based on granular confirmation.
    """
    
    # Force reload
    from dotenv import load_dotenv
    load_dotenv(override=True)

    # Initialize LLM (Stable Flash)
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    ) 
    
    parser = JsonOutputParser(pydantic_object=TacticalOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "Bias: {bias}\nStructure: {structure}\n5M Data: {data}\n\nSniper, report status.")
    ])
    
    chain = prompt | llm | parser
    
    # Extract 5M data
    technicals = state.get("technical_indicators", {})
    five_min_data = technicals.get("5M_Technicals", "No Data")
    current_price = technicals.get("Current_Price", 1.0500)
    
    try:
        response = chain.invoke({
            "bias": state.get("current_bias", "NEUTRAL"),
            "structure": state.get("market_structure", "UNKNOWN"),
            "data": five_min_data
        })
        
        # Format the reasoning for the trace
        trace_entry = f"[Tactical (Gemini)]: {response['decision']} - {response['reasoning']}"
        if response['decision'] == "EXECUTE":
            trace_entry += f" (Entry: {response['order_details']['entry_price']}, SL: {response['order_details']['stop_loss']})"
        
        return {
            "trade_decision": response["decision"],
            "order_details": response["order_details"],
            "reasoning_trace": [trace_entry]
        }
    except Exception as e:
        error_msg = str(e)
        
        # Transient error retry
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            print(f"⚠️ Tactical Rate Limit: Waiting 10s for retry...")
            import time
            time.sleep(10)
            try:
                response = chain.invoke({
                    "bias": state.get("current_bias", "NEUTRAL"),
                    "structure": state.get("market_structure", "UNKNOWN"),
                    "data": five_min_data
                })
                return {
                    "trade_decision": response["decision"],
                    "order_details": response["order_details"],
                    "reasoning_trace": [f"[Tactical (Gemini - Retry)]: {response['decision']} - {response['reasoning']}"]
                }
            except Exception as retry_e:
                error_msg = f"Retry Failed: {str(retry_e)}"

        print(f"⚠️ Tactical AI Fallback: {error_msg[:100]}")
        
        # Fallback: Safe WAIT
        fallback_decision = "WAIT"
        trace_entry = f"[Tactical (Fallback)]: AI Error: {error_msg[:50]}. Decision: {fallback_decision}"
        
        # Mock empty order details for safety
        fallback_order = {
            "action": "NONE",
            "entry_price": current_price,
            "stop_loss": current_price,
            "take_profit": current_price
        }
        
        return {
            "trade_decision": fallback_decision,
            "order_details": fallback_order,
            "reasoning_trace": [trace_entry]
        }
