import os
import time
from datetime import datetime
from src.graph.graph import create_graph
from src.execution.oanda_client import OandaClient
from dotenv import load_dotenv

load_dotenv()

# Safety imports
from src.safety.kill_switch import is_trading_enabled
from src.safety.circuit_breaker import api_circuit_breaker
from src.validation.data_validator import validator

# Configuration
RUN_INTERVAL_MINUTES = 15  # Increased to 15m to respect Gemini Free Tier limits
RUN_ONCE = False  # Set to False for continuous loop

def fetch_live_market_data():
    """Fetch real-time market data from OANDA (Deep History)."""
    client = OandaClient()
    
    # Fetch current price
    price = client.get_current_price("EUR_USD")
    
    # --- LIGHTWEIGHT MODE (Rate Limit Safe) ---
    # Fetch just enough for calculation
    h1_candles = client.get_candles("EUR_USD", granularity="H1", count=20)
    m15_candles = client.get_candles("EUR_USD", granularity="M15", count=20)
    
    # Calculate simple indicators locally to save tokens
    h1_closes = [c['close'] for c in h1_candles]
    current_close = h1_closes[-1]
    prev_close = h1_closes[-2]
    
    # Simple Trend Logic (Mock TA)
    trend = "BULLISH" if current_close > h1_closes[0] else "BEARISH"
    momentum = "UP" if current_close > prev_close else "DOWN"
    
    return {
        "technical_indicators": {
            "Mode": "Lightweight_calculated",
            "H1_Trend": trend,
            "H1_Momentum": momentum,
            "Current_Price": price.get('bid', 0.0),
            "H1_Close": current_close,
            "H1_Low": min(h1_closes),
            "H1_High": max(h1_closes)
        },
        "macro_sentiment": {
            "News_Summary": "Live market conditions",
            "Sentiment_Score": 60,
        },
        "risk_environment": {
            "VIX": 15,
            "Spread": abs(price.get('ask', 0.0) - price.get('bid', 0.0)),
        },
        "reasoning_trace": []
    }

def run_agent_cycle():
    """Single execution cycle of the trading agent."""
    graph = create_graph()
    
    # --- ADAPTIVE LEARNING: Self-Reflection ---
    from src.nodes.evaluator import get_learning_context
    learning_summary = "No learning data yet."
    try:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running self-reflection...")
        learning_summary = get_learning_context()
        print(f"  {learning_summary}")
    except Exception as e:
        print(f"  Self-reflection skipped: {e}")
    
    # === KILL SWITCH CHECK ===
    if not is_trading_enabled():
        print("[KILL SWITCH] Trading is DISABLED. Skipping cycle.")
        return False
    
    # === CIRCUIT BREAKER CHECK ===
    if not api_circuit_breaker.can_attempt():
        print(f"[CIRCUIT BREAKER] System halted. Status: {api_circuit_breaker.get_status()}")
        return False
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Fetching live market data from OANDA...")
    initial_state = fetch_live_market_data()
    
    # Inject learning context into the state
    initial_state["learning_context"] = learning_summary
    
    print("Running AI Analysis Chain...")
    
    # Smart Retry Logic for Free Tier Limits
    max_retries = 3
    retry_delay = 30 # Initial delay
    
    for attempt in range(max_retries):
        try:
            result = graph.invoke(initial_state)
            
            # --- SUCCESS PROCESSING ---
            print(f"\nBias: {result.get('current_bias')} | "
                  f"Structure: {result.get('market_structure')} | "
                  f"Decision: {result.get('trade_decision')}")
            
            if result.get('execution_result', {}).get('executed'):
                exec_result = result['execution_result']
                print(f"[OK] TRADE EXECUTED: {exec_result.get('action')} "
                      f"{exec_result.get('lot_size')} lots @ {exec_result.get('entry_price')}")
                print(f"  Order ID: {exec_result.get('order_id')}")
            else:
                # --- PROFESSIONAL OBSERVABILITY UPGRADE ---
                exec_res = result.get('execution_result', {})
                risk_res = result.get('risk_assessment', {})
                reason = exec_res.get('reason') or risk_res.get('rejection_reason') or 'Setup not met'
                
                print(f"[X] No trade: {reason}")
                
                # Log Architect's structure if available
                structure = result.get('market_structure', 'UNKNOWN')
                print(f"  Structure: {structure}")

                # Save Reasoning to DB even if no trade
                from src.database.models import Trade, SessionLocal
                
                try:
                    db = SessionLocal()
                    hard_levels = result.get('hard_levels', {})
                    wait_log = Trade(
                        pair="EURUSD",
                        action="WAIT",
                        entry_price=initial_state["technical_indicators"]["Current_Price"],
                        stop_loss=hard_levels.get('invalid_bias_level', 0.0),
                        take_profit=hard_levels.get('target_zone', 0.0),
                        lot_size=0.0,
                        status="NONE",
                        reasoning_trace=result.get("reasoning_trace", [])
                    )
                    db.add(wait_log)
                    db.commit()
                    db.close()
                    print(f"  (Reasoning saved to War Room: {len(result.get('reasoning_trace', []))} steps)")
                except Exception as e:
                    print(f"  (DB Log Error: {e})")
            
            
            # Record success for circuit breaker
            api_circuit_breaker.record_success()
            return True # Success
            
            
        except Exception as e:
            error_str = str(e)
            
            # Record failure for circuit breaker
            api_circuit_breaker.record_failure()
            
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                print(f"(!) Rate Limit Hit (Attempt {attempt+1}/{max_retries}). Waiting {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2 # Exponential backoff
            else:
                print(f"Error: {e}")
                return False
                
    print("❌ Failed after max retries. API Quota likely exhausted for the day.")
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
                # --- HEARTBEAT LOGGING ---
                from src.database.models import Heartbeat, SessionLocal
                try:
                    db = SessionLocal()
                    hb = Heartbeat(status="ACTIVE", last_message="Cycle starting for EURUSD")
                    db.add(hb)
                    db.commit()
                    db.close()
                except Exception as db_err:
                    print(f"Heartbeat Error: {db_err}")

                run_agent_cycle()
                print(f"\nNext check in {RUN_INTERVAL_MINUTES} minutes...")
                time.sleep(RUN_INTERVAL_MINUTES * 60)
            except KeyboardInterrupt:
                print("\n\nAgent stopped by user.")
                break
            except Exception as e:
                # Log crash to heartbeat
                try:
                    db = SessionLocal()
                    hb = Heartbeat(status="CRASHED", last_message=str(e)[:200])
                    db.add(hb)
                    db.commit()
                    db.close()
                except: pass
                print(f"\nError in main loop: {e}")
                print("Retrying in 1 minute...")
                time.sleep(60)

if __name__ == "__main__":
    from src.database.models import init_db
    init_db()
    main()
