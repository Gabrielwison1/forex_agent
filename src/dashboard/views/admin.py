import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.models import Trade, SessionLocal

def app():
    st.header("🧠 Admin Deep Dive")
    st.caption("Database Inspector & System Health")
    
    db = SessionLocal()
    trades = db.query(Trade).all()
    db.close()
    
    # --- PERFORMANCE CHART ---
    st.subheader("P/L Performance Curve")
    if trades:
        balance = 100000
        history = []
        for t in trades:
            pnl = t.pnl if t.pnl else 0
            balance += pnl
            history.append({"Date": t.timestamp, "Balance": balance})
            
        df = pd.DataFrame(history)
        fig = px.line(df, x="Date", y="Balance", title="Mock Equity Curve")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trading history available.")
        
    st.markdown("---")
    
    # --- DATABASE INSPECTOR ---
    st.subheader("Database Inspector (Raw Data)")
    
    query = st.text_area("SQL Query (Read-Only)", "SELECT * FROM trades ORDER BY id DESC LIMIT 50")
    
    if trades:
        data = [{k: v for k, v in t.__dict__.items() if not k.startswith('_')} for t in trades]
        df_raw = pd.DataFrame(data)
        st.dataframe(df_raw, use_container_width=True)
    else:
        st.text("Table is empty.")
