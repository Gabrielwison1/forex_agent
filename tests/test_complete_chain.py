import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph.graph import create_graph
from src.database.models import Trade, SessionLocal

def test_complete_chain():
    """Test the complete 5-node chain with database logging."""
    print("=" * 60)
    print("COMPLETE CHAIN INTEGRATION TEST")
    print("=" * 60 + "\n")
    
    # Create graph
    graph = create_graph()
    
    # Mock input data (bullish setup)
    initial_state = {
        "technical_indicators": {
            "1H_EMA_Cross": "BULLISH",
            "1H_RSI": 55,
            "ATR": 0.0015,
            "Key_Levels": {"Resistance": 1.1000, "Support": 1.0900},
            "15M_Technicals": {
                "Structure": "Higher Highs",
                "Order_Block": "Bullish OB at 1.0950",
                "FVG": "Gap at 1.0960"
            },
            "5M_Technicals": {
                "RSI": 28,
                "Candle_Pattern": "Bullish Engulfing",
                "Current_Price": 1.0950
            }
        },
        "macro_sentiment": {
            "News_Headlines_Summary": "Positive jobs data supports USD",
            "AI_Sentiment_Score": 65,
            "Event_Calendar": "No High Impact in 2hrs"
        },
        "risk_environment": {
            "VIX_Index": 15,
            "Average_Spread": 0.2,
            "DXY_Correlation": 0.85
        },
        "reasoning_trace": []
    }
    
    print("Running complete chain...")
    print("Strategist -> Architect -> Tactical -> Risk Manager -> Executor\n")
    
    try:
        # Execute the complete chain
        result = graph.invoke(initial_state)
        
        # Display results
        print("EXECUTION RESULTS:")
        print("-" * 60)
        print(f"Bias: {result.get('current_bias')}")
        print(f"Structure: {result.get('market_structure')}")
        print(f"Trade Decision: {result.get('trade_decision')}")
        print(f"Risk Approved: {result.get('risk_assessment', {}).get('approved')}")
        print(f"Execution Status: {result.get('execution_result', {}).get('executed')}")
        
        if result.get('execution_result', {}).get('executed'):
            exec_result = result['execution_result']
            print(f"\nTRADE DETAILS:")
            print(f"  Order ID: {exec_result.get('order_id')}")
            print(f"  Database ID: {exec_result.get('trade_id')}")
            print(f"  Pair: {exec_result.get('pair')}")
            print(f"  Action: {exec_result.get('action')}")
            print(f"  Entry: {exec_result.get('entry_price')}")
            print(f"  Lot Size: {exec_result.get('lot_size')}")
        
        print(f"\nREASONING TRACE:")
        for trace in result.get('reasoning_trace', []):
            print(f"  {trace}")
        
        # Verify database entry
        print(f"\nDATABASE VERIFICATION:")
        db = SessionLocal()
        try:
            trade_count = db.query(Trade).count()
            latest_trade = db.query(Trade).order_by(Trade.id.desc()).first()
            
            print(f"  Total trades in DB: {trade_count}")
            if latest_trade:
                print(f"  Latest trade: ID={latest_trade.id}, {latest_trade.action} {latest_trade.lot_size} lots @ {latest_trade.entry_price}")
                print(f"  Status: {latest_trade.status}")
        finally:
            db.close()
        
        print("\n" + "=" * 60)
        print("INTEGRATION TEST PASSED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_complete_chain()
