import sys
import os
import io

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph.graph import create_graph

def test_risk_off_scenario():
    """Test that High Impact News triggers RISK_OFF and skips Architect."""
    print("TEST 1: High Impact News -> Expect RISK_OFF (Graph Ends)")
    
    state = {
        "technical_indicators": {"1H_EMA_Cross": "BULLISH", "1H_RSI": 60, "ATR": 0.0020,},
        "macro_sentiment": {
            "News_Headlines_Summary": "CRITICAL: NFP RELEASED. NON-FARM PAYROLLS SURPRISE.", 
            "AI_Sentiment_Score": 50, 
            "Event_Calendar": "NFP NOW"
        },
        "risk_environment": {"VIX_Index": 25, "Average_Spread": 1.5, "DXY_Correlation": 0.1},
        "reasoning_trace": []
    }
    
    graph = create_graph()
    result = graph.invoke(state)
    
    print(f"Bias: {result.get('current_bias')}")
    print(f"Structure: {result.get('market_structure')}")
    
    assert result.get('current_bias') == "RISK_OFF", "Failed: Bias should be RISK_OFF"
    assert result.get('market_structure') is None, "Failed: Architect should NOT have run"
    print("PASS\n")

def test_bias_long_scenario():
    """Test that Bullish inputs trigger BIAS_LONG and execute Architect."""
    print("TEST 2: Bullish Inputs -> Expect BIAS_LONG + Architect Analysis")
    
    state = {
        "technical_indicators": {
            "1H_EMA_Cross": "BULLISH", 
            "1H_RSI": 55, 
            "ATR": 0.0015,
            "Key_Levels": {"Resistance": 1.1200},
            "15M_Technicals": {"Structure": "Higher Highs", "FVG": "Bullish Gap"}
        },
        "macro_sentiment": {
            "News_Headlines_Summary": "Economy stable, growth expected", 
            "AI_Sentiment_Score": 75, 
            "Event_Calendar": "Clear"
        },
        "risk_environment": {"VIX_Index": 12, "Average_Spread": 0.1, "DXY_Correlation": 0.9},
        "reasoning_trace": []
    }
    
    graph = create_graph()
    result = graph.invoke(state)
    
    print(f"Bias: {result.get('current_bias')}")
    print(f"Structure: {result.get('market_structure')}")
    print(f"Trace: {result.get('reasoning_trace')}")
    
    assert result.get('current_bias') == "BIAS_LONG", "Failed: Bias should be BIAS_LONG"
    assert result.get('market_structure') in ["TRENDING", "RANGING", "CHOPPY"], "Failed: Architect DID NOT run"
    print("PASS\n")

if __name__ == "__main__":
    try:
        test_risk_off_scenario()
        test_bias_long_scenario()
        print("ALL TESTS PASSED")
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
    except Exception as e:
        print(f"EXECUTION ERROR: {e}")
