"""
Evaluator Node - Self-Reflection & Adaptive Learning
Analyzes past WAIT decisions against actual market outcomes.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.database.models import SessionLocal, Trade
from src.execution.oanda_client import OandaClient


def evaluate_past_performance(lookback_hours: int = 24) -> str:
    """
    Analyze recent WAIT decisions to identify missed opportunities.
    
    Returns:
        A concise summary string for the Strategist's learning context.
    """
    try:
        db = SessionLocal()
        client = OandaClient()
        
        # Get WAIT records from the last 24-48 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=lookback_hours)
        wait_records = db.query(Trade).filter(
            Trade.action == "WAIT",
            Trade.timestamp >= cutoff_time,
            Trade.stop_loss != 0.0  # Only evaluate records with hard_levels set
        ).order_by(Trade.timestamp.desc()).limit(20).all()
        
        if not wait_records:
            return "No recent WAIT decisions with hard levels to evaluate."
        
        correct_waits = 0
        missed_winners = 0
        avoided_losses = 0
        
        for record in wait_records:
            # Determine bias direction from reasoning
            bias = "LONG" if "BIAS_LONG" in str(record.reasoning_trace) else "SHORT"
            
            # Fetch historical data from the decision timestamp
            # Get 4 hours of M15 candles (16 candles) to see what happened after
            try:
                # Note: OANDA's get_candles with count fetches the *latest* candles
                # For historical analysis, we'd need to use the 'from' and 'to' parameters
                # For now, we'll use a simplified heuristic
                
                current_price = client.get_current_price("EUR_USD")
                if "error" in current_price:
                    continue
                
                # Simplified evaluation (would be more sophisticated in production)
                target = record.take_profit
                invalidation = record.stop_loss
                entry = record.entry_price
                
                # Check if target or invalidation would have been hit
                # This is a simplified check - in production, we'd fetch actual historical candles
                if bias == "LONG":
                    if current_price['bid'] >= target:
                        missed_winners += 1
                    elif current_price['bid'] <= invalidation:
                        correct_waits += 1
                    else:
                        avoided_losses += 1
                else:  # SHORT
                    if current_price['bid'] <= target:
                        missed_winners += 1
                    elif current_price['bid'] >= invalidation:
                        correct_waits += 1
                    else:
                        avoided_losses += 1
                        
            except Exception as e:
                print(f"  [Evaluator] Error analyzing record {record.id}: {e}")
                continue
        
        db.close()
        
        # Generate learning summary
        total_analyzed = correct_waits + missed_winners + avoided_losses
        if total_analyzed == 0:
            return "Insufficient data for performance evaluation."
        
        miss_rate = (missed_winners / total_analyzed) * 100
        
        if missed_winners > 3:
            return (f"LEARNING INSIGHT: Over the last {lookback_hours}h, you missed {missed_winners} "
                   f"potential winners ({miss_rate:.0f}% miss rate). Consider being more aggressive "
                   f"when Trend + Structure align strongly, even if short-term momentum is weak.")
        elif correct_waits > missed_winners * 2:
            return (f"LEARNING INSIGHT: Your conservative approach is working well. "
                   f"{correct_waits} correct WAITs vs {missed_winners} missed opportunities. "
                   f"Maintain current bias sensitivity.")
        else:
            return (f"LEARNING INSIGHT: Performance is balanced. {missed_winners} missed vs "
                   f"{correct_waits} correct WAITs. Current strategy is appropriate.")
                   
    except Exception as e:
        return f"Performance evaluation failed: {str(e)[:100]}"


def get_learning_context() -> str:
    """
    Quick wrapper to get the learning context for the current cycle.
    """
    return evaluate_past_performance(lookback_hours=24)


if __name__ == "__main__":
    # Quick test
    print("=== PERFORMANCE EVALUATOR TEST ===")
    summary = get_learning_context()
    print(f"\nLearning Summary:\n{summary}")
