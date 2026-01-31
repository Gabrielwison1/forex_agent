import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.database.models import Trade, Heartbeat, SessionLocal
from src.config import risk_config

def app():
    st.header("🧠 Admin Deep Dive")
    st.caption("Advanced Analytics, Performance Metrics & System Health")
    
    db = SessionLocal()
    all_trades = db.query(Trade).all()
    heartbeats = db.query(Heartbeat).order_by(Heartbeat.timestamp.desc()).limit(100).all()
    db.close()
    
    #--- PERFORMANCE METRICS ---
    st.subheader("📈 Performance Dashboard")
    
    # Filter real trades
    real_trades = [t for t in all_trades if t.action in ["BUY", "SELL"]] if all_trades else []
    closed_trades = [t for t in real_trades if t.status == "CLOSED" and t.pnl is not None] if real_trades else []
    
    # Calculate metrics with defaults
    total_trades = len(real_trades)
    winning_trades = len([t for t in closed_trades if t.pnl > 0])
    losing_trades = len([t for t in closed_trades if t.pnl < 0])
    
    if closed_trades:
        win_rate = (winning_trades / len(closed_trades) * 100)
        total_pnl = sum(t.pnl for t in closed_trades)
        avg_win = sum(t.pnl for t in closed_trades if t.pnl > 0) / winning_trades if winning_trades else 0
        avg_loss = sum(t.pnl for t in closed_trades if t.pnl < 0) / losing_trades if losing_trades else 0
    else:
        win_rate = 0.0
        total_pnl = 0.0
        avg_win = 0.0
        avg_loss = 0.0
    
    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("Total Trades", total_trades)
    col2.metric("Win Rate", f"{win_rate:.1f}%", delta=f"{winning_trades}W / {losing_trades}L")
    col3.metric("Total P&L", f"${total_pnl:.2f}", delta=f"{'+' if total_pnl >= 0 else ''}{total_pnl:.2f}")
    col4.metric("Avg Win", f"${avg_win:.2f}")
    col5.metric("Avg Loss", f"${avg_loss:.2f}")
    
    st.markdown("---")
    
    # --- EQUITY CURVE ---
    st.subheader("💹 Equity Curve")
    
    balance = risk_config.ACCOUNT_BALANCE
    history = [{"Date": datetime.utcnow() - timedelta(days=30), "Balance": balance}]
    
    sorted_trades = sorted(all_trades, key=lambda x: x.timestamp) if all_trades else []
    
    for t in sorted_trades:
        # Only count consolidated PnL for closed trades to avoid volatility
        if t.status == "CLOSED" and t.pnl is not None:
             balance += t.pnl
             history.append({"Date": t.timestamp, "Balance": balance})
    
    # If no trades, append current time point to make a flat line
    if not sorted_trades:
        history.append({"Date": datetime.utcnow(), "Balance": balance})
    
    df_equity = pd.DataFrame(history)
    
    fig_equity = go.Figure()
    fig_equity.add_trace(go.Scatter(
        x=df_equity['Date'],
        y=df_equity['Balance'],
        mode='lines',
        name='Balance',
        line=dict(color='#4CAF50', width=3),
        fill='tozeroy',
        fillcolor='rgba(76, 175, 80, 0.1)'
    ))
    
    fig_equity.update_layout(
        template='plotly_dark',
        height=400,
        xaxis_title="Date",
        yaxis_title="Account Balance ($)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_equity, use_container_width=True)
    
    st.markdown("---")
    
    # --- P&L DISTRIBUTION ---
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 P&L Distribution")
        
        if closed_trades:
            pnl_data = [t.pnl for t in closed_trades]
            fig_pnl = go.Figure(data=[go.Histogram(
                x=pnl_data,
                nbinsx=20,
                marker_color='#4CAF50',
                opacity=0.7
            )])
            fig_pnl.update_layout(template='plotly_dark', height=300, showlegend=False)
            st.plotly_chart(fig_pnl, use_container_width=True)
        else:
            st.info("No closed trades yet")
    
    with col_chart2:
        st.subheader("🎯 Win/Loss Breakdown")
        
        if closed_trades:
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Wins', 'Losses'],
                values=[winning_trades, losing_trades],
                marker_colors=['#4CAF50', '#FF5252'],
                hole=0.4
            )])
            fig_pie.update_layout(template='plotly_dark', height=300, showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No closed trades yet")
    
    st.markdown("---")
    
    # --- TRADE ANALYSIS ---
    st.subheader("🔍 Trade Analysis")
    
    if real_trades:
        # Trade table with filters
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            filter_status = st.selectbox("Status", ["ALL", "OPEN", "CLOSED"])
        
        with col_filter2:
            filter_action = st.selectbox("Action", ["ALL", "BUY", "SELL"])
        
        with col_filter3:
            sort_by = st.selectbox("Sort By", ["Timestamp", "P&L", "Lot Size"])
        
        # Apply filters
        filtered_trades = real_trades
        if filter_status != "ALL":
            filtered_trades = [t for t in filtered_trades if t.status == filter_status]
        if filter_action != "ALL":
            filtered_trades = [t for t in filtered_trades if t.action == filter_action]
        
        # Parse data for table
        trade_data = []
        for t in filtered_trades:
            trade_data.append({
                "ID": t.id[:8],
                "Timestamp": t.timestamp,
                "Pair": t.pair,
                "Action": t.action,
                "Size": t.size,
                "Entry": t.entry_price,
                "Exit": t.exit_price,
                "P&L": f"${t.pnl:.2f}" if t.pnl else "-",
                "Status": t.status
            })
        
        df_trades = pd.DataFrame(trade_data)
        st.dataframe(df_trades, use_container_width=True, height=400)
        
        # Export button
        csv = df_trades.to_csv(index=False)
        st.download_button(
            label="📥 Download Trade History (CSV)",
            data=csv,
            file_name='trade_history.csv',
            mime='text/csv',
        )
    else:
        st.info("No trades match the selected filters")

    st.markdown("---")
    
    # --- SYSTEM HEALTH ---
    st.subheader("❤️ System Health Monitor")
    
    # Health Timeline
    if heartbeats:
        hb_data = []
        for hb in heartbeats:
            status = 1 if "ACTIVE" in (hb.last_message or "") or "Cycle starting" in (hb.last_message or "") else 0.5
            if "CRASHED" in (hb.last_message or "") or "Error" in (hb.last_message or ""):
                status = 0
            
            hb_data.append({
                "Timestamp": hb.timestamp,
                "Status": status,
                "Message": hb.last_message
            })
            
        df_hb = pd.DataFrame(hb_data)
        
        fig_hb = px.scatter(df_hb, x="Timestamp", y="Status", 
                           color="Status", 
                           color_continuous_scale=["#FF5252", "#FFC107", "#4CAF50"],
                           title="Agent Activity Timeline")
        
        fig_hb.update_layout(
            template='plotly_dark',
            height=200,
            yaxis=dict(tickmode='array', tickvals=[0, 0.5, 1], ticktext=['Offline', 'Idle', 'Active']),
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=False
        )
        
        st.plotly_chart(fig_hb, use_container_width=True)
        
        # Recent heartbeats
        st.markdown("**Recent Heartbeats:**")
        for hb in heartbeats[:5]:
            ts = hb.timestamp.strftime("%H:%M:%S")
            msg = hb.last_message or "No message"
            msg_lower = msg.lower()
            
            if "crashed" in msg_lower or "error" in msg_lower or "invalid" in msg_lower or "failed" in msg_lower:
                icon = "🔴"
            elif "cycle starting" in msg_lower:
                 icon = "🟢"
            else:
                 icon = "⚪"  # Grey for neutral/info messages
                 
            st.markdown(f"{icon} **{ts}** - {msg}")
    else:
        st.warning("No heartbeat data available")

    st.markdown("---")

    # --- SQL INSPECTOR ---
    with st.expander("💾 Database Inspector"):
        st.warning("Read-only access to raw database tables")
        
        if st.checkbox("View Raw Trade Data"):
            raw_data = []
            for t in all_trades:
                # Convert object to dict safely
                raw_data.append({k: v for k, v in t.__dict__.items() if not k.startswith('_')})
            
            df_raw = pd.DataFrame(raw_data)
            st.dataframe(df_raw, use_container_width=True, height=300)
        else:
            st.info("Trade table is empty")
    
        if st.checkbox("Custom SQL Query (Read-Only)"):
            query = st.text_area("Enter SQL Query (SELECT only)", "SELECT * FROM trades LIMIT 5")
            if st.button("Run Query"):
                if "DROP" in query.upper() or "DELETE" in query.upper() or "UPDATE" in query.upper() or "INSERT" in query.upper():
                    st.error("❌ Only SELECT queries are allowed!")
                else:
                    try:
                        db = SessionLocal()
                        result = pd.read_sql(query, db.bind)
                        db.close()
                        st.dataframe(result, use_container_width=True)
                    except Exception as e:
                        st.error(f"Query error: {e}")
