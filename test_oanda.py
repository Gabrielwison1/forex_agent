import os
import v20
from dotenv import load_dotenv

# Load env
load_dotenv()

api_key = os.getenv("OANDA_API_KEY")
account_id = os.getenv("OANDA_ACCOUNT_ID")
url = os.getenv("OANDA_URL")

print("--- OANDA CONNECTION TEST ---")
print(f"URL: {url}")
print(f"Account ID: {account_id}")
print(f"API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'None'}")

if not all([api_key, account_id, url]):
    print("ERROR: Missing credentials in .env")
    exit(1)

try:
    client = v20.Context(
        url.replace("https://", ""),
        443,
        True,
        application="TestConnection",
        token=api_key,
        datetime_format="RFC3339"
    )

    print("\n1. Testing Account Summary...")
    response = client.account.summary(account_id)
    print(f"Status: {response.status}")
    
    if response.status != 200:
        print(f"ERROR BODY: {response.body}")
    else:
        print(f"SUCCESS! Balance: {response.get('account', 200).balance}")

    print("\n2. Testing Pricing (EUR_USD)...")
    response = client.pricing.get(account_id, instruments="EUR_USD")
    print(f"Status: {response.status}")
    
    if response.status != 200:
        print(f"ERROR BODY: {response.body}")
    else:
        prices = response.get("prices", 200)
        if prices:
            print(f"SUCCESS! Bid: {prices[0].bids[0].price}")
        else:
            print("SUCCESS but no prices returned (market closed?)")

except Exception as e:
    print(f"\nCRITICAL EXCEPTION: {e}")
