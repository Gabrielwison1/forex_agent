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
    
    if all_trades:
        # Calculate metrics
        real_trades = [t for t in all_trades if t.action in ["BUY", "SELL"]]
        closed_trades = [t for t in real_trades if t.status == "CLOSED" and t.pnl is not None]
        
        total_trades = len(real_trades)
        winning_trades = len([t for t in closed_trades if t.pnl > 0])
        losing_trades = len([t for t in closed_trades if t.pnl < 0])
        win_rate = (winning_trades / len(closed_trades) * 100) if closed_trades else 0
        
        total_pnl = sum(t.pnl for t in closed_trades)
        avg_win = sum(t.pnl for t in closed_trades if t.pnl > 0) / winning_trades if winning_trades else 0
        avg_loss = sum(t.pnl for t in closed_trades if t.pnl < 0) / losing_trades if losing_trades else 0
        
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
        
        for t in sorted(all_trades, key=lambda x: x.timestamp):
            pnl = t.pnl if t.pnl else 0
            balance += pnl
            history.append({"Date": t.timestamp, "Balance": balance})
        
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
                
                fig_pnl.update_layout(
                    template='plotly_dark',
                    height=300,
                    xaxis_title="P&L ($)",
                    yaxis_title="Frequency",
                    showlegend=False
                )
                
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
                
                fig_pie.update_layout(
                    template='plotly_dark',
                    height=300,
                    showlegend=True
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No closed trades yet")
        
        st.markdown("---")
        
        # --- TRADE ANALYSIS ---
        st.subheader("🔍 Trade Analysis")
        
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
        
        # Create dataframe
        if filtered_trades:
            trade_data = []
            for t in filtered_trades:
                trade_data.append({
                    'ID': t.id,
                    'Timestamp': t.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    'Pair': t.pair,
                    'Action': t.action,
                    'Entry': f"{t.entry_price:.5f}",
                    'Exit': f"{t.exit_price:.5f}" if t.exit_price else "N/A",
                    'SL': f"{t.stop_loss:.5f}",
                    'TP': f"{t.take_profit:.5f}",
                    'Lots': t.lot_size,
                    'P&L': f"${t.pnl:.2f}" if t.pnl else "OPEN",
                    'Status': t.status
                })
            
            df_trades = pd.DataFrame(trade_data)
            st.dataframe(df_trades, use_container_width=True, height=400)
            
            # Export button
            csv = df_trades.to_csv(index=False)
            st.download_button(
                label="📥 Export to CSV",
                data=csv,
                file_name=f"trades_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No trades match the selected filters")
        
    else:
        st.info("No trading history available yet")
    
    st.markdown("---")
    
    # --- SYSTEM HEALTH ---
    st.subheader("💓 System Health Monitor")
    
    if heartbeats:
        # Heartbeat timeline
        hb_data = []
        for hb in reversed(heartbeats):
            hb_data.append({
                'Timestamp': hb.timestamp,
                'Status': 1 if hb.status == "ACTIVE" else 0,
                'Message': hb.last_message or "No message"
            })
        
        df_hb = pd.DataFrame(hb_data)
        
        fig_hb = px.scatter(
            df_hb,
            x='Timestamp',
            y='Status',
            color='Status',
            color_continuous_scale=['#FF5252', '#4CAF50'],
            title="Agent Activity Timeline",
            hover_data=['Message']
        )
        
        fig_hb.update_layout(
            template='plotly_dark',
            height=250,
            yaxis_title="Status",
            showlegend=False
        )
        
        st.plotly_chart(fig_hb, use_container_width=True)
        
        # Recent heartbeats
        st.markdown("**Recent Heartbeats:**")
        for hb in heartbeats[:5]:
            status_emoji = "🟢" if hb.status == "ACTIVE" else "🔴"
            st.text(f"{status_emoji} {hb.timestamp.strftime('%H:%M:%S')} - {hb.status} - {hb.last_message}")
    else:
        st.warning("No heartbeat data available")
    
    st.markdown("---")
    
    # --- DATABASE INSPECTOR ---
    st.subheader("🗄️ Database Inspector")
    
    with st.expander("📋 View Raw Trade Data"):
        if all_trades:
            # Convert to dict
            raw_data = []
            for t in all_trades[:50]:  # Limit to 50 most recent
                raw_data.append({k: v for k, v in t.__dict__.items() if not k.startswith('_')})
            
            df_raw = pd.DataFrame(raw_data)
            st.dataframe(df_raw, use_container_width=True, height=300)
        else:
            st.info("Trade table is empty")
    
    with st.expander("🔍 Custom SQL Query (Read-Only)"):
        st.warning("Advanced feature - Use with caution")
        query = st.text_area(
            "SQL Query",
            "SELECT * FROM trades WHERE status = 'OPEN' ORDER BY timestamp DESC LIMIT 10",
            height=100
        )
        
        if st.button("Execute Query"):
            try:
                db = SessionLocal()
                result = pd.read_sql(query, db.bind)
                db.close()
                st.dataframe(result, use_container_width=True)
            except Exception as e:
                st.error(f"Query error: {e}")
