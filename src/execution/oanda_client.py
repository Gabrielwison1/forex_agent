import os
import v20
from dotenv import load_dotenv

load_dotenv()

class OandaClient:
    """
    Premium OANDA v20 API Wrapper.
    Handles pricing, historical data, and order execution.
    """
    def __init__(self):
        self.api_key = os.getenv("OANDA_API_KEY")
        self.account_id = os.getenv("OANDA_ACCOUNT_ID")
        self.url = os.getenv("OANDA_URL")
        
        if not all([self.api_key, self.account_id, self.url]):
            raise ValueError("OANDA credentials missing in .env")
            
        self.client = v20.Context(
            self.url.replace("https://", ""),
            443,
            True,
            application="PremiumForexAgent",
            token=self.api_key,
            datetime_format="RFC3339"
        )

    def get_account_summary(self):
        """Fetch basic account details (Balance, NAV, etc.)"""
        response = self.client.account.summary(self.account_id)
        if response.status != 200:
            return {"error": response.body.get("errorMessage", "Unknown error")}
        return response.get("account", 200)

    def get_current_price(self, pair="EUR_USD"):
        """Fetch live Bid/Ask price for a pair."""
        response = self.client.pricing.get(self.account_id, instruments=pair)
        if response.status != 200:
            return {"error": response.body.get("errorMessage", "Price fetch failed")}
        
        prices = response.get("prices", 200)
        if not prices:
            return {"error": "No price data received"}
            
        return {
            "bid": float(prices[0].bids[0].price),
            "ask": float(prices[0].asks[0].price),
            "timestamp": prices[0].time
        }

    def get_candles(self, pair="EUR_USD", granularity="H1", count=20):
        """Fetch historical candle data for AI analysis."""
        params = {"granularity": granularity, "count": count}
        response = self.client.instrument.candles(pair, **params)
        
        if response.status != 200:
            return {"error": response.body.get("errorMessage", "Candle fetch failed")}
            
        candles = response.get("candles", 200)
        formatted_candles = []
        for c in candles:
            if c.complete:
                formatted_candles.append({
                    "time": c.time,
                    "close": float(c.mid.c),
                    "high": float(c.mid.h),
                    "low": float(c.mid.l),
                    "open": float(c.mid.o),
                    "volume": c.volume
                })
        return formatted_candles

    def place_market_order(self, pair, units, stop_loss=None, take_profit=None):
        """Execute a Market Order."""
        order_spec = {
            "type": "MARKET",
            "instrument": pair,
            "units": str(units),
            "timeInForce": "FOK"
        }
        
        if stop_loss:
            order_spec["stopLossOnFill"] = {"price": str(stop_loss)}
        if take_profit:
            order_spec["takeProfitOnFill"] = {"price": str(take_profit)}
            
        response = self.client.order.market(self.account_id, order=order_spec)
        
        if response.status != 201:
            return {"error": response.body.get("errorMessage", "Order failed")}
            
        return response.get("orderFillTransaction", 201)

if __name__ == "__main__":
    # Internal Test
    try:
        trading_client = OandaClient()
        print("Connecting to OANDA...")
        summary = trading_client.get_account_summary()
        print(f"Account Balance: ${summary.balance}")
        
        price = trading_client.get_current_price("EUR_USD")
        print(f"EUR/USD Live Price: {price['bid']} / {price['ask']}")
    except Exception as e:
        print(f"OANDA Client Error: {e}")
