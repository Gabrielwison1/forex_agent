from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

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
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

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
