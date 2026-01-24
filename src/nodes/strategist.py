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
You are the **Senior Macro-Quantitative Strategist** for a premium algorithmic FX fund. Your goal is to determine the "Market Bias" for the next 1-4 hour window. You prioritize capital preservation over aggressive gains.

### INPUT DATA SCHEMA
You will receive a JSON object containing:
1. **Technical_Indicators:** {{1H_EMA_Cross, 1H_RSI, ATR, Key_Levels(S/R)}}
2. **Macro_Sentiment:** {{News_Headlines_Summary, AI_Sentiment_Score (0-100), Event_Calendar}}
3. **Risk_Environment:** {{VIX_Index, Average_Spread, DXY_Correlation}}

### OPERATIONAL STATES
Your output MUST transition the system into one of these states:
- `BIAS_LONG`: High-conviction bullish environment.
- `BIAS_SHORT`: High-conviction bearish environment.
- `RISK_OFF`: Neutral/Dangerous environment. Used for high-impact news, low conviction, or extreme volatility.

### REASONING PROTOCOL (Chain-of-Thought)
You must analyze the data in this specific order:
1. **Macro Filter:** Is there high-impact news (NFP, CPI, Central Bank rates) within 30 minutes? If YES -> Force `RISK_OFF`.
2. **Sentiment Alignment:** Does the AI Sentiment Score align with the Technical Trend? (e.g., Bullish News + Bullish EMA Cross).
3. **Volatility Check:** Is the current ATR or VIX indicating "unpredictable" expansion? If volatility is >2.5x the 24h average -> Force `RISK_OFF`.
4. **Structural Confirmation:** Is price sitting at a major 1H Support/Resistance? Avoid calling a bias directly into a brick wall.

### OUTPUT FORMAT
You must respond ONLY in a valid JSON format to be parsed by the State Machine:
{{
  "state": "BIAS_LONG" | "BIAS_SHORT" | "RISK_OFF",
  "confidence_score": 0.0 to 1.0,
  "reasoning_trace": "A 2-sentence technical/macro justification for the audit trail.",
  "hard_levels": {{"invalid_bias_level": price, "target_zone": price}}
}}
"""

def strategist_node(state: AgentState) -> Dict[str, Any]:
    """
    The Strategist Node (1H Layer).
    Analyzes macro and technical inputs to set the Daily Bias.
    """
    
    # Initialize LLM (Gemini 2.0 Flash is free, fast, and smarter)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    ) 
    
    parser = JsonOutputParser(pydantic_object=StrategistOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "Current Market Data:\nTechnical: {technical}\nMacro: {macro}\nRisk: {risk}\n\nAnalyst, what is your bias?")
    ])
    
    chain = prompt | llm | parser
    
    response = chain.invoke({
        "technical": state["technical_indicators"],
        "macro": state["macro_sentiment"],
        "risk": state["risk_environment"]
    })
    
    # Map response to AgentState updates
    return {
        "current_bias": response["state"],
        "reasoning_trace": [f"[Strategist]: {response['reasoning_trace']} (Confidence: {response['confidence_score']})"] 
    }
