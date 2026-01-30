"""
Integration Test for Risk Manager Safety Features
Tests daily drawdown enforcement and max position limits.
"""
import unittest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.nodes.risk_manager import risk_manager_node
from src.database.models import Trade, SessionLocal, Base, create_engine
from src.config import risk_config

class TestRiskManagerSafety(unittest.TestCase):
    """Test Risk Manager safety enforcement."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        # Create test database engine
        cls.test_engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(cls.test_engine)
        
        # Create test session factory
        from sqlalchemy.orm import sessionmaker
        cls.TestSession = sessionmaker(bind=cls.test_engine)
        
        # Patch SessionLocal in models module
        import src.database.models as models
        cls.original_session = models.SessionLocal
        models.SessionLocal = cls.TestSession
    
    @classmethod
    def tearDownClass(cls):
        """Restore original SessionLocal."""
        import src.database.models as models
        models.SessionLocal = cls.original_session
    
    
    def setUp(self):
        """Clean database before each test."""
        db = self.TestSession()
        db.query(Trade).delete()
        db.commit()
        db.close()
    
    def test_max_positions_enforcement(self):
        """Should reject trade when max positions reached."""
        # Create 3 open positions
        db = self.TestSession()
        for i in range(3):
            trade = Trade(
                pair="EUR_USD",
                action="BUY",
                entry_price=1.0500 + (i * 0.0001),
                stop_loss=1.0480,
                take_profit=1.0550,
                lot_size=0.01,
                status="OPEN"
            )
            db.add(trade)
        db.commit()
        db.close()
        
        # Try to approve a 4th trade
        state = {
            "trade_decision": "EXECUTE",
            "order_details": {
                "action": "BUY",
                "entry_price": 1.0500,
                "stop_loss": 1.0480,
                "take_profit": 1.0550
            }
        }
        
        result = risk_manager_node(state)
        
        self.assertFalse(result["risk_assessment"]["approved"])
        self.assertIn("Max open positions", result["risk_assessment"]["rejection_reason"])
    
    def test_daily_drawdown_enforcement(self):
        """Should reject trade when daily drawdown limit hit."""
        # Create losing trades for today
        db = self.TestSession()
        max_loss = risk_config.ACCOUNT_BALANCE * risk_config.MAX_DAILY_DRAWDOWN
        
        trade = Trade(
            pair="EUR_USD",
            action="BUY",
            entry_price=1.0500,
            stop_loss=1.0480,
            take_profit=1.0550,
            lot_size=0.01,
            status="CLOSED",
            pnl=-(max_loss + 10)  # Exceed drawdown limit
        )
        db.add(trade)
        db.commit()
        db.close()
        
        # Try to approve new trade
        state = {
            "trade_decision": "EXECUTE",
            "order_details": {
                "action": "BUY",
                "entry_price": 1.0500,
                "stop_loss": 1.0480,
                "take_profit": 1.0550
            }
        }
        
        result = risk_manager_node(state)
        
        self.assertFalse(result["risk_assessment"]["approved"])
        self.assertIn("Daily drawdown", result["risk_assessment"]["rejection_reason"])
    
    def test_approval_when_within_limits(self):
        """Should approve trade when all safety checks pass."""
        state = {
            "trade_decision": "EXECUTE",
            "order_details": {
                "action": "BUY",
                "entry_price": 1.0500,
                "stop_loss": 1.0480,
                "take_profit": 1.0550
            }
        }
        
        result = risk_manager_node(state)
        
        self.assertTrue(result["risk_assessment"]["approved"])

if __name__ == '__main__':
    unittest.main()
