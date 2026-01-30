"""
Trade Exit Monitor - Background Worker
Monitors open positions on OANDA and updates database with exit data.
"""
import time
from datetime import datetime
from typing import List, Dict, Any
from src.database.models import Trade, SessionLocal
from src.execution.oanda_client import OandaClient
from src.config import risk_config

class TradeExitMonitor:
    """Monitors and updates trade exits."""
    
    def __init__(self, check_interval_seconds: int = 60):
        self.client = OandaClient()
        self.check_interval = check_interval_seconds
    
    def get_open_positions_from_oanda(self) -> Dict[str, Any]:
        """Fetch current open positions from OANDA."""
        try:
            response = self.client.client.position.list(self.client.account_id)
            if response.status != 200:
                print(f"[Exit Monitor] Error fetching positions: {response.status}")
                return {}
            
            positions = response.get("positions", 200)
            
            # Convert to dict keyed by instrument
            position_dict = {}
            for pos in positions:
                if hasattr(pos, 'long') and int(pos.long.units) != 0:
                    position_dict[pos.instrument] = {
                        'side': 'LONG',
                        'units': int(pos.long.units),
                        'averagePrice': float(pos.long.averagePrice) if hasattr(pos.long, 'averagePrice') else None
                    }
                elif hasattr(pos, 'short') and int(pos.short.units) != 0:
                    position_dict[pos.instrument] = {
                        'side': 'SHORT',
                        'units': abs(int(pos.short.units)),
                        'averagePrice': float(pos.short.averagePrice) if hasattr(pos.short, 'averagePrice') else None
                    }
            
            return position_dict
        except Exception as e:
            print(f"[Exit Monitor] Exception fetching positions: {e}")
            return {}
    
    def calculate_pnl(self, trade: Trade, exit_price: float) -> float:
        """Calculate P&L for a closed trade."""
        pip_distance = abs(exit_price - trade.entry_price) * 10000
        pip_value = risk_config.get_pip_value(trade.pair.replace('_', ''), trade.lot_size)
        
        if trade.action == "BUY":
            if exit_price > trade.entry_price:
                return pip_distance * pip_value  # Profit
            else:
                return -pip_distance * pip_value  # Loss
        else:  # SELL
            if exit_price < trade.entry_price:
                return pip_distance * pip_value  # Profit
            else:
                return -pip_distance * pip_value  # Loss
    
    def check_and_update_exits(self):
        """Main monitoring loop - checks for closed trades."""
        db = SessionLocal()
        
        try:
            # Get all open trades from database
            open_trades = db.query(Trade).filter(Trade.status == "OPEN").all()
            
            if not open_trades:
                print("[Exit Monitor] No open trades to monitor")
                return
            
            # Get current OANDA positions
            oanda_positions = self.get_open_positions_from_oanda()
            
            # Get current market price for each pair
            current_prices = {}
            for trade in open_trades:
                pair = trade.pair.replace('USD', '_USD').replace('EUR', 'EUR_')  # Format for OANDA
                if pair not in current_prices:
                    try:
                        price_data = self.client.get_current_price(pair)
                        if 'error' not in price_data:
                            current_prices[pair] = price_data
                    except:
                        pass
            
            # Check each open trade
            for trade in open_trades:
                pair = trade.pair.replace('USD', '_USD').replace('EUR', 'EUR_')
                
                # If trade is not in OANDA positions, it has been closed
                if pair not in oanda_positions:
                    print(f"[Exit Monitor] Trade {trade.id} closed on OANDA")
                    
                    # Determine exit price
                    if pair in current_prices:
                        exit_price = current_prices[pair]['bid']
                    else:
                        # Fallback: use SL or TP based on which was likely hit
                        exit_price = trade.stop_loss  # Conservative assumption
                    
                    # Calculate P&L
                    pnl = self.calculate_pnl(trade, exit_price)
                    
                    # Update trade record
                    trade.status = "CLOSED"
                    trade.exit_price = exit_price
                    trade.pnl = pnl
                    
                    print(f"  Trade ID: {trade.id}, Exit: {exit_price}, P&L: ${pnl:.2f}")
            
            db.commit()
            print(f"[Exit Monitor] Updated {len([t for t in open_trades if t.status == 'CLOSED'])} closed trades")
            
        except Exception as e:
            print(f"[Exit Monitor] Error: {e}")
            db.rollback()
        finally:
            db.close()
    
    def run_forever(self):
        """Continuous monitoring loop."""
        print(f"[Exit Monitor] Starting continuous monitoring (interval: {self.check_interval}s)")
        
        while True:
            try:
                self.check_and_update_exits()
            except Exception as e:
                print(f"[Exit Monitor] Fatal error: {e}")
            
            time.sleep(self.check_interval)

if __name__ == "__main__":
    monitor = TradeExitMonitor(check_interval_seconds=120)  # Check every 2 minutes
    monitor.run_forever()
