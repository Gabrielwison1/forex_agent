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
            data = [{
                "Time": t.timestamp.strftime("%H:%M:%S"),
                "Action": t.action,
                "Entry": t.entry_price,
                "Lots": t.lot_size,
                "P/L": f"${t.pnl}" if t.pnl else "OPEN"
            } for t in trades]
            st.dataframe(data, use_container_width=True)
        else:
            st.info("No trades yet. Waiting for opportunities...")

    with col_right:
        st.subheader("🧠 Thought Stream")
        
        if trades and trades[0].reasoning_trace:
            content = "\n\n".join(trades[0].reasoning_trace)
        else:
            content = "Waiting for AI reasoning..."
            
        st.markdown(f'<div class="trade-log">{content}</div>', unsafe_allow_html=True)

    # Auto-refresh
    if st.button("Refresh Monitor"):
        st.rerun()
