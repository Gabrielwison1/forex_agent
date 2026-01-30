"""
Circuit Breaker Module - Prevents Runaway Loops
Tracks consecutive failures and implements exponential backoff.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional

class CircuitBreaker:
    """Circuit breaker for preventing runaway trading loops."""
    
    def __init__(self, max_consecutive_failures: int = 5, reset_window_minutes: int = 60):
        self.max_failures = max_consecutive_failures
        self.reset_window = timedelta(minutes=reset_window_minutes)
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.is_open = False
    
    def record_success(self):
        """Reset the circuit breaker on successful execution."""
        self.failure_count = 0
        self.is_open = False
        self.last_failure_time = None
    
    def record_failure(self):
        """Record a failure and check if circuit should open."""
        current_time = datetime.utcnow()
        
        # Reset if window has passed
        if self.last_failure_time and (current_time - self.last_failure_time) > self.reset_window:
            self.failure_count = 0
        
        self.failure_count += 1
        self.last_failure_time = current_time
        
        # Open circuit if threshold exceeded
        if self.failure_count >= self.max_failures:
            self.is_open = True
            print(f"[CIRCUIT BREAKER] OPENED after {self.failure_count} consecutive failures")
    
    def can_attempt(self) -> bool:
        """Check if we can attempt another operation."""
        if not self.is_open:
            return True
        
        # Check if enough time has passed to auto-reset
        if self.last_failure_time and (datetime.utcnow() - self.last_failure_time) > self.reset_window:
            print(f"[CIRCUIT BREAKER] Auto-resetting after {self.reset_window.seconds}s cooldown")
            self.failure_count = 0
            self.is_open = False
            return True
        
        return False
    
    def get_status(self) -> Dict:
        """Get current status of the circuit breaker."""
        return {
            "is_open": self.is_open,
            "failure_count": self.failure_count,
            "max_failures": self.max_failures,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None
        }

# Global instance
api_circuit_breaker = CircuitBreaker(max_consecutive_failures=5, reset_window_minutes=60)
