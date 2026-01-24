from src.execution.oanda_client import OandaClient
import pandas as pd

class DataFetcher:
    """
    Fetches and formats real market data from OANDA for the AI Brain.
    """
    def __init__(self):
        self.client = OandaClient()

    def get_market_state(self, pair="EUR_USD"):
        """
        Fetches all necessary timeframe data and account info.
        """
        print(f"Fetching live market data for {pair}...")
        
        # 1. Fetch Account Info
        account = self.client.get_account_summary()
        balance = float(account.balance) if hasattr(account, "balance") else 10000.0
        
        # 2. Fetch Timeframe Data
        h1_candles = self.client.get_candles(pair, granularity="H1", count=20)
        m15_candles = self.client.get_candles(pair, granularity="M15", count=20)
        m5_candles = self.client.get_candles(pair, granularity="M5", count=20)
        
        # 3. Simple Indicator Calculation for LLM context (Mocking technicals for now)
        # In a full premium system, we'd use TA-Lib here.
        current_price = self.client.get_current_price(pair)
        
        # Format strings for the AI Nodes
        h1_context = f"Last 5 H1 Closes: {[c['close'] for c in h1_candles[-5:]]}"
        m15_context = f"Last 5 M15 Closes: {[c['close'] for c in m15_candles[-5:]]}"
        m5_context = f"Current Price: {current_price['bid']} / {current_price['ask']}"

        return {
            "technical_indicators": {
                "1H_Data": h1_context,
                "15M_Data": m15_context,
                "5M_Data": m5_context,
                "1H_RSI": 50, # Placeholder
                "ATR": 0.0010, # Placeholder
            },
            "macro_sentiment": {
                "News_Headlines_Summary": "Fetching live news... (Mocked for now)",
                "AI_Sentiment_Score": 50
            },
            "risk_environment": {
                "Account_Balance": balance,
                "Average_Spread": 0.2
            }
        }

if __name__ == "__main__":
    fetcher = DataFetcher()
    state = fetcher.get_market_state()
    print(state)
