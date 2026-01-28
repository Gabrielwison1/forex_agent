from src.database.models import SessionLocal, Trade, Heartbeat
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
    
    # Fetch last 20
    trades = db.query(Trade).order_by(Trade.timestamp.desc()).limit(20).all()
    if trades:
        print("\nLatest Records:")
        for t in trades:
            print(f"- [{t.timestamp}] Action: {t.action} | ID: {t.id}")
            print(f"  Reasoning: {t.reasoning_trace[0] if t.reasoning_trace else 'None'}")
    else:
        print("\nNO RECORDS FOUND.")
        
    # Check Heartbeats
    print("\n--- HEARTBEAT STATUS ---")
    hbs = db.query(Heartbeat).order_by(Heartbeat.timestamp.desc()).limit(3).all()
    for hb in hbs:
        print(f"- [{hb.timestamp}] Status: {hb.status} | Msg: {hb.last_message}")
        
    db.close()
except Exception as e:
    print(f"\nCRITICAL CONNECTION ERROR: {e}")
