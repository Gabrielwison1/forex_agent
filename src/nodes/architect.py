from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from src.state import AgentState
import os

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
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    ) 
    
    parser = JsonOutputParser(pydantic_object=ArchitectOutput)
    
    # Inject the Strategist's bias into the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "Daily Bias: {bias}\n15M Data: {data}\n\nArchitect, define the structure.")
    ])
    
    chain = prompt | llm | parser
    
    # We assume '15M_Technicals' is passed in the state inputs (mocked for now)
    # In a real scenario, this comes from the raw data input
    
    response = chain.invoke({
        "bias": state.get("current_bias", "NEUTRAL"),
        "data": state.get("technical_indicators", {}).get("15M_Technicals", "No Data")
    })
    
    return {
        "market_structure": response["structure"],
        "reasoning_trace": [f"[Architect]: {response['reasoning']} (Plan: {response['action_plan']})"]
    }
