import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.database.models import Trade, Heartbeat, SessionLocal
from src.execution.oanda_client import OandaClient
from src.safety.kill_switch import is_trading_enabled, enable_trading, disable_trading
from src.safety.circuit_breaker import api_circuit_breaker

# Function Wrapper
def app():
    st.title("🦅 Live War Room")
    st.caption("Premium Intelligent Adaptive Trading Agent | Active Session")
    
    # Premium CSS
    st.markdown("""
    <style>
        .metric-container {
            background: linear-gradient(135deg, #1E1E1E 0%, #2A2A2A 100%);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #333;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s;
        }
        .metric-container:hover {
            transform: translateY(-2px);
            border-color: #4CAF50;
        }
        .metric-label {
            font-size: 12px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #FFF;
        }
        .trade-log {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            background-color: #000;
            padding: 15px;
            border-radius: 8px;
            height: 380px;
            overflow-y: scroll;
            border: 1px solid #333;
            line-height: 1.6;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .status-active { background: #4CAF50; color: #000; }
        .status-inactive { background: #FF5252; color: #FFF; }
        .status-warning { background: #FFC107; color: #000; }
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

    @st.cache_data(ttl=5)
    def get_daily_pnl():
        """Calculate today's P&L."""
        db = SessionLocal()
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_trades = db.query(Trade).filter(
            Trade.timestamp >= today_start,
            Trade.pnl != None
        ).all()
        db.close()
        
        total_pnl = sum(t.pnl for t in today_trades)
        return total_pnl, len(today_trades)

    bid, ask, balance = get_live_metrics()
    daily_pnl, trades_today = get_daily_pnl()

    # --- SYSTEM STATUS BANNER ---
    trading_enabled = is_trading_enabled()
    circuit_status = api_circuit_breaker.get_status()
    
    col_status1, col_status2, col_status3 = st.columns(3)
    
    with col_status1:
        status_class = "status-active" if trading_enabled else "status-inactive"
        status_text = "ACTIVE" if trading_enabled else "DISABLED"
        st.markdown(f'<span class="status-badge {status_class}">🔄 Trading: {status_text}</span>', unsafe_allow_html=True)
    
    with col_status2:
        circuit_class = "status-active" if not circuit_status['is_open'] else "status-warning"
        circuit_text = "HEALTHY" if not circuit_status['is_open'] else f"OPEN ({circuit_status['failure_count']}/5)"
        st.markdown(f'<span class="status-badge {circuit_class}">⚡ Circuit: {circuit_text}</span>', unsafe_allow_html=True)
    
    with col_status3:
        db = SessionLocal()
        open_count = db.query(Trade).filter(Trade.status == "OPEN").count()
        db.close()
        position_class = "status-active" if open_count < 3 else "status-warning"
        st.markdown(f'<span class="status-badge {position_class}">📊 Positions: {open_count}/3</span>', unsafe_allow_html=True)

    st.markdown("---")

    # --- TOP METRICS ROW ---
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Account Balance</div>
            <div class="metric-value" style="color: #4CAF50;">${balance:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        pnl_color = "#4CAF50" if daily_pnl >= 0 else "#FF5252"
        pnl_sign = "+" if daily_pnl >= 0 else ""
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Today's P&L</div>
            <div class="metric-value" style="color: {pnl_color};">{pnl_sign}${daily_pnl:.2f}</div>
            <div class="metric-label">{trades_today} trades</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">EUR/USD Bid</div>
            <div class="metric-value">{bid:.5f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">EUR/USD Ask</div>
            <div class="metric-value">{ask:.5f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        spread = (ask - bid) * 10000
        color = "#FF5252" if spread > 10 else "#4CAF50"
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Spread</div>
            <div class="metric-value" style="color: {color};">{spread:.1f} pips</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- MAIN CONTENT ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📊 Active Positions & History")
        
        db = SessionLocal()
        all_trades = db.query(Trade).order_by(Trade.timestamp.desc()).limit(20).all()
        db.close()
        
        if all_trades:
            # Filter for real trades
            real_trades = [t for t in all_trades if t.action in ["BUY", "SELL"]]
            
            if real_trades:
                data = []
                for t in real_trades:
                    pnl_display = f"${t.pnl:.2f}" if t.pnl else "OPEN"
                    pnl_color = "🟢" if (t.pnl and t.pnl > 0) else ("🔴" if (t.pnl and t.pnl < 0) else "⚪")
                    
                    data.append({
                        "Time": t.timestamp.strftime("%H:%M:%S"),
                        "Action": f"{t.action} {t.lot_size}",
                        "Entry": f"{t.entry_price:.5f}",
                        "SL": f"{t.stop_loss:.5f}",
                        "TP": f"{t.take_profit:.5f}",
                        "Status": t.status,
                        "P&L": f"{pnl_color} {pnl_display}"
                    })
                
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, height=300)
            else:
                st.info("No trades executed yet. Agent is analyzing market...")
        else:
            st.info("No activity recorded.")

        # Quick actions
        st.markdown("### Quick Actions")
        col_act1, col_act2, col_act3 = st.columns(3)
        
        with col_act1:
            if trading_enabled:
                if st.button("🛑 Disable Trading", type="secondary"):
                    disable_trading()
                    st.success("Trading disabled via kill switch")
                    st.rerun()
            else:
                if st.button("✅ Enable Trading", type="primary"):
                    enable_trading()
                    st.success("Trading activated")
                    st.rerun()
        
        with col_act2:
            if st.button("🔄 Refresh Data"):
                st.cache_data.clear()
                st.rerun()
        
        with col_act3:
            if st.button("📊 Export Trades"):
                if all_trades:
                    df_export = pd.DataFrame([{
                        'Timestamp': t.timestamp,
                        'Pair': t.pair,
                        'Action': t.action,
                        'Entry': t.entry_price,
                        'Exit': t.exit_price,
                        'P&L': t.pnl,
                        'Status': t.status
                    } for t in all_trades])
                    csv = df_export.to_csv(index=False)
                    st.download_button("Download CSV", csv, "trades.csv", "text/csv")

    with col_right:
        st.subheader("🧠 Thought Stream")
        
        # --- HEARTBEAT MONITOR ---
        db = SessionLocal()
        last_hb = db.query(Heartbeat).order_by(Heartbeat.timestamp.desc()).first()
        db.close()
        
        if last_hb:
            time_diff = (datetime.utcnow() - last_hb.timestamp).total_seconds()
            if time_diff < 120:  # Less than 2 minutes
                status_color = "#4CAF50"
                status_text = "ACTIVE"
                status_emoji = "🟢"
            elif time_diff < 600:  # Less than 10 minutes
                status_color = "#FFC107"
                status_text = "IDLE"
                status_emoji = "🟡"
            else:
                status_color = "#FF5252"
                status_text = "OFFLINE"
                status_emoji = "🔴"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1E1E1E 0%, #2A2A2A 100%); padding: 15px; border-radius: 8px; border-left: 5px solid {status_color}; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                <b style="color: {status_color}; font-size: 16px;">{status_emoji} AGENT: {status_text}</b><br>
                <small style="color: #888;">Last Heartbeat: {last_hb.timestamp.strftime('%H:%M:%S')} ({int(time_diff)}s ago)</small><br>
                <small style="color: #666;">Message: {last_hb.last_message or 'No message'}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No heartbeat detected. Agent may not be running.")

        # Latest reasoning trace
        if all_trades and all_trades[0].reasoning_trace:
            latest_log = all_trades[0]
            ts = latest_log.timestamp.strftime("%H:%M:%S")
            header = f"[{ts}] DECISION: {latest_log.action}"
            trace = "\n > ".join(latest_log.reasoning_trace)
            content = f"{header}\n\n > {trace}"
        else:
            content = "Waiting for AI reasoning..."
            
        st.markdown(f'<div class="trade-log">{content}</div>', unsafe_allow_html=True)

    # Auto-refresh every 15 seconds
    import time
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    if time.time() - st.session_state.last_refresh > 15:
        st.session_state.last_refresh = time.time()
        st.rerun()
