import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.execution.oanda_client import OandaClient

def test_oanda_connection():
    print("="*40)
    print("OANDA CONNECTIVITY TEST")
    print("="*40)
    
    try:
        client = OandaClient()
        
        print("\n0. Listing All Accounts...")
        response = client.client.account.list()
        if response.status == 200:
            accounts = response.get("accounts", 200)
            print(f"   SUCCESS: Found {len(accounts)} accounts.")
            for acc in accounts:
                print(f"   - {acc.id}")
        else:
            print(f"   FAILED to list accounts: {response.status} {response.body.get('errorMessage', '')}")
            return

        print(f"\n1. Fetching Account Summary for {os.getenv('OANDA_ACCOUNT_ID')}...")
        summary = client.get_account_summary()
        if hasattr(summary, "balance"):
            print(f"   SUCCESS: Account Balance is ${summary.balance}")
            print(f"   Account ID: {summary.id}")
        else:
            print(f"   FAILED: {summary.get('error')}")
            return
            
        print("\n2. Fetching Live Prices (EUR_USD)...")
        price = client.get_current_price("EUR_USD")
        if "error" not in price:
            print(f"   SUCCESS: EUR/USD Bid={price['bid']}, Ask={price['ask']}")
        else:
            print(f"   FAILED: {price['error']}")
            
        print("\n3. Fetching Candles (1H)...")
        candles = client.get_candles("EUR_USD", granularity="H1", count=5)
        if isinstance(candles, list) and len(candles) > 0:
            print(f"   SUCCESS: Received {len(candles)} 1H candles.")
        else:
            print(f"   FAILED: {candles.get('error') if isinstance(candles, dict) else 'Unknown'}")

        print("\n" + "="*40)
        print("ALL CONNECTIVITY TESTS PASSED")
        print("="*40)

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_oanda_connection()
