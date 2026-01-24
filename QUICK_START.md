# Premium Intelligent Adaptive Trading Agent

## Quick Start Guide

### ONE-COMMAND STARTUP (Recommended)

Simply double-click:

```
START_AGENT.bat
```

This will:

1. Start the trading agent in the background
2. Open the dashboard in your browser automatically
3. Everything runs from one window

### What You'll See

**Trading Agent Window (Background):**

- Live market analysis every 5 minutes
- Trade execution notifications
- AI reasoning output

**Dashboard (Browser):**

- http://localhost:8501
- Live account balance
- Real-time EUR/USD prices
- Trade history table
- AI reasoning trace
- Performance metrics

### Manual Controls (If Needed)

**Start Agent Only:**

```
python -m src.main
```

**Start Dashboard Only:**

```
run_dashboard.bat
```

### Configuration

Edit `src/main.py` to change:

- `RUN_ONCE = True` → Single execution
- `RUN_ONCE = False` → Continuous mode
- `RUN_INTERVAL_MINUTES = 5` → Check frequency

### Safety Features

✓ Demo account only (no real money)
✓ 1% risk per trade maximum
✓ Minimum 2:1 Risk/Reward ratio
✓ All trades logged to database
✓ Full AI reasoning transparency

### Support

Check the dashboard for live status.
All trades are logged to PostgreSQL for audit trail.
