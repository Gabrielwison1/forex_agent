import streamlit as st
import pandas as pd
from datetime import datetime
from src.database.models import Trade, SessionLocal
from src.execution.oanda_client import OandaClient

# Function Wrapper
def app():
    st.title("🦅 Live War Room")
    st.caption("Premium Intelligent Adaptive Trading Agent | Active Session")
    
    # Premium CSS (injected once in app.py usually, but can be here too)
    st.markdown("""
    <style>
        .metric-container {
            background-color: #1E1E1E; padding: 15px; border-radius: 8px; border: 1px solid #333;
            text-align: center;
        }
        .metric-label { font-size: 14px; color: #888; }
        .metric-value { font-size: 24px; font-weight: bold; color: #FFF; }
        .trade-log { font-family: 'Courier New', monospace; font-size: 12px; background-color: #000; padding: 10px; border-radius: 5px; height: 300px; overflow-y: scroll; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

    # --- DATA FETCHING ---
    @st.cache_data(ttl=5)
    def get_live_metrics():
        try:
            client = OandaClient()
            price = client.get_current_price("EUR_USD")
            summary = client.get_account_summary()
            balance = float(summary.balance) if hasattr(summary, 'balance') else 100000.0
            return price['bid'], price['ask'], balance
        except:
            return 0, 0, 0

    bid, ask, balance = get_live_metrics()

    # --- TOP METRICS ROW ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">ACCOUNT BALANCE</div>
            <div class="metric-value" style="color: #4CAF50;">${balance:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">EUR/USD BID</div>
            <div class="metric-value">{bid:.5f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">EUR/USD ASK</div>
            <div class="metric-value">{ask:.5f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        spread = (ask - bid) * 10000
        color = "#FF5252" if spread > 10 else "#4CAF50"
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">SPREAD (PIPS)</div>
            <div class="metric-value" style="color: {color};">{spread:.1f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- MAIN CONTENT ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📊 Active Positions & History")
        
        db = SessionLocal()
        trades = db.query(Trade).order_by(Trade.timestamp.desc()).limit(15).all()
        db.close()
        
        if trades:
            # Filter trades for the Table (Show only real trades, hide WAITs)
            real_trades = [t for t in trades if t.action in ["BUY", "SELL"]]
            
            if real_trades:
                data = [{
                    "Time": t.timestamp.strftime("%H:%M:%S"),
                    "Action": t.action,
                    "Entry": t.entry_price,
                    "Lots": t.lot_size,
                    "P/L": f"${t.pnl}" if t.pnl else "OPEN"
                } for t in real_trades]
                st.dataframe(data, use_container_width=True)
            else:
                st.info("No active positions.")
                
            # Show ALL logs (including WAIT) in the Thought Stream
            latest_log = trades[0] # Get absolute latest activity
        else:
            st.info("No activity recorded.")
            latest_log = None

    with col_right:
        st.subheader("🧠 Thought Stream")
        
        # --- HEARTBEAT MONITOR ---
        from src.database.models import Heartbeat
        db = SessionLocal()
        last_hb = db.query(Heartbeat).order_by(Heartbeat.timestamp.desc()).first()
        db.close()
        
        if last_hb:
            status_color = "#4CAF50" if last_hb.status == "ACTIVE" else "#FF5252"
            st.markdown(f"""
            <div style="background-color: #1E1E1E; padding: 10px; border-radius: 5px; border-left: 5px solid {status_color}; margin-bottom: 20px;">
                <b style="color: {status_color};">AGENT STATUS: {last_hb.status}</b><br>
                <small style="color: #888;">Last Seen: {last_hb.timestamp.strftime('%H:%M:%S')}</small><br>
                <small style="color: #666;">MSG: {last_hb.last_message}</small>
            </div>
            """, unsafe_allow_html=True)

        if latest_log and latest_log.reasoning_trace:
            # Format nicely
            ts = latest_log.timestamp.strftime("%H:%M:%S")
            header = f"[{ts}] DECISION: {latest_log.action}"
            trace = "\n > ".join(latest_log.reasoning_trace)
            content = f"{header}\n\n > {trace}"
        else:
            content = "Waiting for AI reasoning..."
            
        st.markdown(f'<div class="trade-log">{content}</div>', unsafe_allow_html=True)

    # Auto-refresh logic (Every 30 seconds)
    import time
    
    if st.button("Refresh Monitor"):
        st.rerun()
        
    # Simple auto-refresh ticker
    time.sleep(1) # Small delay to prevent CPU spinning
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    if time.time() - st.session_state.last_refresh > 30:
        st.session_state.last_refresh = time.time()
        st.rerun()
