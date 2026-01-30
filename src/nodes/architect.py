from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from src.state import AgentState
import os
import time

# --- Output Schema ---
class KeyZone(BaseModel):
    price: float = Field(description="Price level of the key zone")
    type: str = Field(description="e.g. ORDER_BLOCK, FVG, BREAK_BLOCK")

class ArchitectOutput(BaseModel):
    structure: str = Field(description="TRENDING, RANGING, or CHOPPY")
    key_zone: KeyZone
    action_plan: str = Field(description="Specific instructions for the 1M tactical layer")
    reasoning: str = Field(description="Brief structural analysis")

# --- System Prompt ---
SYSTEM_PROMPT = """### ROLE
You are the **Architect (15M Market Structure Analyst)**.
Your Supervisor (Strategist) has already defined the Daily Bias: **{bias}**.
Your job is to find the *best location* to execute this bias on the 15-Minute chart.

### INPUT DATA
1. **15M_Technicals**: Market Structure (HH/HL), Order Blocks, FVGs.
2. **Current_Price**: Live bid/ask.

### TASK
Analyze the 15M structure.
- If Bias is **LONG**, look for Discount/Oversold conditions + Bullish Order Blocks.
- If Bias is **SHORT**, look for Premium/Overbought conditions + Bearish Breakers.

### OUTPUT STATES
- `TRENDING`: Clear Break of Structure (BOS) in direction of Bias.
- `RANGING`: Price stuck between Swing High/Low. Trade boundaries.
- `CHOPPY`: No clear structure. Recommend caution.

### LEARNING CONTEXT
{learning_context}

### JSON OUTPUT FORMAT
{{
    "structure": "TRENDING" | "RANGING" | "CHOPPY",
    "key_zone": {{"price": 1.2345, "type": "ORDER_BLOCK"}},
    "action_plan": "Wait for retrace to 1.2345 OB then enter...",
    "reasoning": "Price broke structure to upside, leaving FVG..."
}}
"""

def architect_node(state: AgentState) -> Dict[str, Any]:
    """
    The Architect Node (15M Layer).
    Refines 1H Bias with 15M Structure.
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
    
    parser = JsonOutputParser(pydantic_object=ArchitectOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "Daily Bias: {bias}\n15M Data: {data}\n\nArchitect, define the structure.")
    ])
    
    chain = prompt | llm | parser
    
    technicals = state.get("technical_indicators", {})
    current_price = technicals.get("Current_Price", 1.0500)
    
    try:
        # Get learning context
        learning_context = state.get("learning_context", "No recent performance data available.")
        
        response = chain.invoke({
            "bias": state.get("current_bias", "NEUTRAL"),
            "data": technicals,
            "learning_context": learning_context
        })
        
        return {
            "market_structure": response["structure"],
            "reasoning_trace": [f"[Architect (Gemini)]: {response['reasoning']} (Plan: {response['action_plan']})"]
        }
    except Exception as e:
        error_msg = str(e)
        
        # Transient error retry
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            print(f"⚠️ Architect Rate Limit: Waiting 10s for retry...")
            import time
            time.sleep(10)
            try:
                response = chain.invoke({
                    "bias": state.get("current_bias", "NEUTRAL"),
                    "data": technicals,
                    "learning_context": learning_context
                })
                return {
                    "market_structure": response["structure"],
                    "reasoning_trace": [f"[Architect (Gemini - Retry)]: {response['reasoning']}"]
                }
            except Exception as retry_e:
                error_msg = f"Retry Failed: {str(retry_e)}"

        print(f"⚠️ Architect AI Fallback: {error_msg[:100]}")
        return {
            "market_structure": "RANGING", # Safe default
            "reasoning_trace": [f"Architect (Fallback): AI Error: {error_msg[:50]}. Treating as Ranging."],
        }
