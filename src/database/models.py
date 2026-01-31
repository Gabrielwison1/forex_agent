from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Heartbeat(Base):
    """Heartbeat model for monitoring worker status."""
    __tablename__ = 'heartbeats'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="ALIVE")
    last_message = Column(String(200), nullable=True)

    def __repr__(self):
        return f"<Heartbeat(id={self.id}, timestamp={self.timestamp}, status={self.status})>"

class Trade(Base):
    """Trade model for storing executed trades."""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    pair = Column(String(10), nullable=False)  # e.g., "EURUSD"
    action = Column(String(10), nullable=False)  # "BUY" or "SELL"
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    lot_size = Column(Float, nullable=False)
    status = Column(String(10), default="OPEN")  # "OPEN" or "CLOSED"
    exit_price = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)  # Profit/Loss in USD
    reasoning_trace = Column(JSON, nullable=True)  # Full AI reasoning chain
    
    def __repr__(self):
        return f"<Trade(id={self.id}, pair={self.pair}, action={self.action}, status={self.status})>"

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

def create_retrying_engine(url, max_retries=5, delay=3):
    """Create an engine with retry logic for startup recovery."""
    last_err = None
    for i in range(max_retries):
        try:
            engine = create_engine(url)
            # Test connection
            with engine.connect() as conn:
                return engine
        except Exception as e:
            last_err = e
            if "starting up" in str(e).lower() or "connection refused" in str(e).lower():
                print(f"  [DB] Database is starting up... (Attempt {i+1}/{max_retries})")
                time.sleep(delay)
            else:
                raise e
    raise last_err

import time
engine = create_retrying_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables with retry logic."""
    max_retries = 3
    for i in range(max_retries):
        try:
            # create_all is idempotent - only creates if missing
            Base.metadata.create_all(bind=engine)
            return
        except Exception as e:
            if "starting up" in str(e).lower() and i < max_retries - 1:
                print(f"  [DB] System still starting up, retrying schema init... ({i+1}/{max_retries})")
                time.sleep(5)
            else:
                print(f"Error initializing database schema: {e}")
                raise e

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    # Create tables
    init_db()
