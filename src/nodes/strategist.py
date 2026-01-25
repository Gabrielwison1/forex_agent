from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI # CHANGED: Switched to Google
from pydantic import BaseModel, Field
from src.state import AgentState
import os
from dotenv import load_dotenv

load_dotenv()

# --- Output Schema ---
class HardLevels(BaseModel):
    invalid_bias_level: float = Field(description="Price level where the bias is invalidated")
    target_zone: float = Field(description="Price target zone")

class StrategistOutput(BaseModel):
    state: str = Field(description="BIAS_LONG, BIAS_SHORT, or RISK_OFF")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0")
    reasoning_trace: str = Field(description="A 2-sentence technical/macro justification")
    hard_levels: HardLevels

# --- System Prompt ---
SYSTEM_PROMPT = """### ROLE
You are the **Senior Macro-Quantitative Strategist** for a premium algorithmic FX fund. 
Your goal is to determine the "Market Bias" by performing deep technical analysis on RAW historical price data (OHLC Candles).

### INPUT DATA SCHEMA
You will receive calculated Technical Indicators (Lightweight Mode):
1. **Trend:** H1 Trend Direction.
2. **Levels:** Highs/Lows.

### ANALYSIS PROTOCOL
1. **Trend Check:** If Trend is BULLISH, look for longs.
2. **Setup:** If Momentum aligns with Trend, confirm setup.
3. **Risk:** If Spread is high, force RISK_OFF.

### REASONING PROTOCOL
1. **Macro Check:** If there is high-impact news or D1 structure is unclear -> Force `RISK_OFF`.
2. **Setup Quality:** A setup is only Valid if D1 and H4 align (e.g., D1 Bullish + H4 Break of Structure Up).
3. **Volatility:** If recent candles are excessively large (wicks > 3x body), market is too volatile.

### OUTPUT FORMAT
You must respond ONLY in a valid JSON format:
{{
  "state": "BIAS_LONG" | "BIAS_SHORT" | "RISK_OFF",
  "confidence_score": 0.0 to 1.0,
  "reasoning_trace": "Brief synthesis of D1 Trend, H4 Structure, and H1 Pattern.",
  "hard_levels": {{"invalid_bias_level": price, "target_zone": price}}
}}
"""

def strategist_node(state: AgentState) -> Dict[str, Any]:
    """
    The Strategist Node (1H Layer).
    Analyzes macro and technical inputs to set the Daily Bias.
    """
    # Force reload environment to pick up API Key changes without restart
    load_dotenv(override=True)
    
    # Initialize LLM (Gemini Flash Stable)
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    ) 
    
    parser = JsonOutputParser(pydantic_object=StrategistOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "Market Data: {technical_indicators}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        # Fix: Pass dictionary matching prompt variable
        response = chain.invoke({"technical_indicators": state["technical_indicators"]})
        
        return {
            "current_bias": response["state"],
            "reasoning_trace": [f"[Strategist (Gemini)]: {response['reasoning_trace']} (Conf: {response['confidence_score']})"] 
        }
    except Exception as e:
        # --- FALLBACK LOGIC ("The Lizard Brain") ---
        # When AI fails/throttles, use robust mechanical logic
        print(f"⚠️ AI Error ({str(e)[:50]}...): Switching to Fallback Logic.")
        
        tech = state.get("technical_indicators", {})
        trend = tech.get("H1_Trend", "NEUTRAL")
        price = tech.get("Current_Price", 1.0500)
        
        fallback_bias = "RISK_OFF"
        if trend == "BULLISH":
            fallback_bias = "BIAS_LONG"
        elif trend == "BEARISH":
            fallback_bias = "BIAS_SHORT"
            
        return {
            "current_bias": fallback_bias,
            "reasoning_trace": [f"[Strategist (Fallback)]: AI unavailable. Mechanical Bias: {fallback_bias}"],
            # Ensure downstream nodes don't crash due to missing keys
            "hard_levels": {"invalid_bias_level": price, "target_zone": price} 
        }
