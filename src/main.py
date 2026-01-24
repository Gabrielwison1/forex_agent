import os
import time
from datetime import datetime
from src.graph.graph import create_graph
from src.execution.oanda_client import OandaClient
from dotenv import load_dotenv

load_dotenv()

# Configuration
RUN_INTERVAL_MINUTES = 15  # Increased to 15m to respect Gemini Free Tier limits
RUN_ONCE = False  # Set to False for continuous loop

def fetch_live_market_data():
    """Fetch real-time market data from OANDA."""
    client = OandaClient()
    
    # Fetch current price
    price = client.get_current_price("EUR_USD")
    
    # Fetch candles for different timeframes
    h1_candles = client.get_candles("EUR_USD", granularity="H1", count=20)
    m15_candles = client.get_candles("EUR_USD", granularity="M15", count=20)
    m5_candles = client.get_candles("EUR_USD", granularity="M5", count=10)
    
    # Simple technical indicators (placeholder - in production use TA-Lib)
    h1_closes = [c['close'] for c in h1_candles[-5:]]
    m15_closes = [c['close'] for c in m15_candles[-5:]]
    
    # Format for AI consumption
    return {
        "technical_indicators": {
            "1H_EMA_Cross": "BULLISH" if h1_closes[-1] > h1_closes[0] else "BEARISH",
            "1H_RSI": 55,  # Placeholder
            "ATR": 0.0015,
            "Key_Levels": {"Resistance": max(h1_closes), "Support": min(h1_closes)},
            "15M_Technicals": {
                "Structure": "Higher Highs" if m15_closes[-1] > m15_closes[0] else "Lower Lows",
                "Order_Block": f"Level at {m15_closes[-2]:.5f}",
                "FVG": "Gap detected" if abs(m15_closes[-1] - m15_closes[-2]) > 0.0010 else "No gap"
            },
            "5M_Technicals": {
                "RSI": 50,  # Placeholder
                "Candle_Pattern": "Analyzing...",
                "Current_Price": price['bid']
            }
        },
        "macro_sentiment": {
            "News_Headlines_Summary": "Live market conditions",
            "AI_Sentiment_Score": 60,
            "Event_Calendar": "No High Impact events"
        },
        "risk_environment": {
            "VIX_Index": 15,
            "Average_Spread": abs(price['ask'] - price['bid']),
            "DXY_Correlation": 0.85
        },
        "reasoning_trace": []
    }

def run_agent_cycle():
    """Single execution cycle of the trading agent."""
    graph = create_graph()
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Fetching live market data from OANDA...")
    initial_state = fetch_live_market_data()
    
    print("Running AI Analysis Chain...")
    
    try:
        result = graph.invoke(initial_state)
        
        print(f"\nBias: {result.get('current_bias')} | "
              f"Structure: {result.get('market_structure')} | "
              f"Decision: {result.get('trade_decision')}")
        
        if result.get('execution_result', {}).get('executed'):
            exec_result = result['execution_result']
            print(f"✓ TRADE EXECUTED: {exec_result.get('action')} "
                  f"{exec_result.get('lot_size')} lots @ {exec_result.get('entry_price')}")
            print(f"  Order ID: {exec_result.get('order_id')}")
        else:
            reason = result.get('execution_result', {}).get('reason', 'No setup found')
            print(f"✗ No trade: {reason}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main entry point for the trading agent."""
    print("="*60)
    print("  PREMIUM INTELLIGENT ADAPTIVE TRADING AGENT")
    print("="*60)
    print(f"Started: {datetime.now()}")
    print(f"Mode: {'SINGLE RUN' if RUN_ONCE else 'CONTINUOUS'}")
    print(f"Pair: EUR/USD")
    print("="*60)
    
    if RUN_ONCE:
        # Single execution
        run_agent_cycle()
        print("\n" + "="*60)
        print("Agent execution complete. Check dashboard for details.")
        print("="*60)
    else:
        # Continuous loop
        print(f"Running every {RUN_INTERVAL_MINUTES} minutes. Press Ctrl+C to stop.\n")
        
        while True:
            try:
                run_agent_cycle()
                print(f"\nNext check in {RUN_INTERVAL_MINUTES} minutes...")
                time.sleep(RUN_INTERVAL_MINUTES * 60)
            except KeyboardInterrupt:
                print("\n\nAgent stopped by user.")
                break
            except Exception as e:
                print(f"\nError in main loop: {e}")
                print("Retrying in 1 minute...")
                time.sleep(60)

if __name__ == "__main__":
    main()
