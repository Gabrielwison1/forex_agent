from src.database.models import SessionLocal, Trade
from sqlalchemy import text

print("--- DIAGNOSTIC DB INSPECTOR ---")
try:
    db = SessionLocal()
    # Check connection info (mask password)
    url = str(db.bind.url)
    print(f"Connected to: {url.split('@')[1] if '@' in url else url}")
    
    # Check Row Count
    count = db.query(Trade).count()
    print(f"Total Rows in Trade Table: {count}")
    
    # Fetch last 5
    trades = db.query(Trade).order_by(Trade.timestamp.desc()).limit(5).all()
    if trades:
        print("\nLatest Records:")
        for t in trades:
            print(f"- [{t.timestamp}] Action: {t.action} | ID: {t.order_id}")
            print(f"  Reasoning: {t.reasoning_trace[:1] if t.reasoning_trace else 'None'}")
    else:
        print("\nNO RECORDS FOUND.")
        
    db.close()
except Exception as e:
    print(f"\nCRITICAL CONNECTION ERROR: {e}")
