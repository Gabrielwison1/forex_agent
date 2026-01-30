import streamlit as st
import os
from dotenv import set_key, load_dotenv
from src.config import risk_config
from src.safety.kill_switch import is_trading_enabled, enable_trading, disable_trading
from src.safety.circuit_breaker import api_circuit_breaker

def app():
    st.header("⚙️ System Settings")
    st.caption("Secure Configuration Management & System Controls")
    
    st.markdown("---")
    
    # --- TRADING CONTROLS ---
    st.subheader ("🔧 Trading Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Kill Switch Status**")
        trading_status = is_trading_enabled()
        
        if trading_status:
            st.success("✅ Trading is ENABLED")
            if st.button("🛑 Disable Trading", type="secondary"):
                disable_trading()
                st.success("Trading disabled successfully")
                st.rerun()
        else:
            st.error("❌ Trading is DISABLED")
            if st.button("▶️ Enable Trading", type="primary"):
                enable_trading()
                st.success("Trading enabled successfully")
                st.rerun()
        
        st.caption("The kill switch provides emergency stop functionality. When disabled, the agent will skip all trading cycles.")
    
    with col2:
        st.markdown("**Circuit Breaker Status**")
        circuit_status = api_circuit_breaker.get_status()
        
        if circuit_status['is_open']:
            st.warning(f"⚠️ Circuit is OPEN ({circuit_status['failure_count']}/{circuit_status['max_failures']} failures)")
            st.caption("System has halted due to repeated failures. It will auto-reset after cooldown period.")
        else:
            st.success(f"✅ Circuit is HEALTHY ({circuit_status['failure_count']}/{circuit_status['max_failures']} failures)")
            st.caption("API calls are operating normally.")
        
        if st.button("🔄 Reset Circuit Breaker"):
            api_circuit_breaker.record_success()
            st.success("Circuit breaker reset")
            st.rerun()
    
    st.markdown("---")
    
    # --- OANDA SETTINGS ---
    st.subheader("🔌 Broker Connection (OANDA)")
    
    load_dotenv()
    current_key = os.getenv("OANDA_API_KEY", "")
    current_id = os.getenv("OANDA_ACCOUNT_ID", "")
    current_url = os.getenv("OANDA_URL", "https://api-fxpractice.oanda.com")
    
    masked_key = current_key[:8] + "..." + current_key[-4:] if len(current_key) > 12 else "Not Set"
    
    st.markdown(f"""
    **Current Configuration:**
    - API Key: `{masked_key}`
    - Account ID: `{current_id}`
    - Environment: `{'Demo' if 'practice' in current_url else 'Live'}`
    """)
    
    with st.expander("🔧 Update OANDA Credentials"):
        new_key = st.text_input("OANDA API Key", value="", type="password", help="Your personal access token", key="oanda_key_input")
        new_id = st.text_input("Account ID", value="", placeholder=current_id, key="oanda_id_input")
        
        env_type = st.radio("Environment", ["Demo (Practice)", "Live (Real Money)"], index=0, key="oanda_env")
        
        if st.button("💾 Save Broker Settings"):
            if new_key and new_id:
                try:
                    import os
                    env_file = os.path.join(os.getcwd(), '.env')
                    
                    # Update .env file
                    set_key(env_file, 'OANDA_API_KEY', new_key)
                    set_key(env_file, 'OANDA_ACCOUNT_ID', new_id)
                    
                    new_url = "https://api-fxpractice.oanda.com" if "Demo" in env_type else "https://api-fxtrade.oanda.com"
                    set_key(env_file, 'OANDA_URL', new_url)
                    
                    st.success("✅ OANDA credentials saved to .env file! Restart the agent to apply changes.")
                    st.info("💡 Run this command to restart: Close all windows and run START_ALL.bat")
                except Exception as e:
                    st.error(f"Error saving settings: {e}")
            else:
                st.warning("Please provide both API Key and Account ID")
    
    st.markdown("---")
    
    # --- RISK SETTINGS ---
    st.subheader("⚖️ Risk Parameters")
    
    st.markdown(f"""
    **Current Risk Configuration:**
    - Risk per trade: `{risk_config.MAX_RISK_PER_TRADE * 100}%`
    - Min R:R ratio: `1:{risk_config.MIN_RISK_REWARD_RATIO}`
    - Max daily drawdown: `{risk_config.MAX_DAILY_DRAWDOWN * 100}%`
    - Max open positions: `{risk_config.MAX_OPEN_POSITIONS}`
    - Account size: `${risk_config.ACCOUNT_BALANCE:,.2f}`
    """)
    
    with st.expander("🔧 Adjust Risk Parameters"):
        st.warning("⚠️ Changing risk parameters requires editing `src/config/risk_config.py` and restarting the agent.")
        
        risk_per_trade = st.slider("Risk Per Trade (%)", 0.1, 5.0, risk_config.MAX_RISK_PER_TRADE * 100, 0.1)
        min_rr = st.slider("Minimum R:R Ratio", 1.0, 5.0, risk_config.MIN_RISK_REWARD_RATIO, 0.5)
        max_drawdown = st.slider("Max Daily Drawdown (%)", 1.0, 10.0, risk_config.MAX_DAILY_DRAWDOWN * 100, 0.5)
        max_positions = st.slider("Max Open Positions", 1, 10, risk_config.MAX_OPEN_POSITIONS, 1)
        account_size = st.number_input("Account Balance ($)", min_value=100.0, value=float(risk_config.ACCOUNT_BALANCE), step=100.0)
        
        if st.button("Generate Risk Config"):
            config_code = f"""# Risk Management Configuration
# Auto-generated from Dashboard

# Account Settings
ACCOUNT_BALANCE = {account_size}
ACCOUNT_CURRENCY = "USD"

# Risk Parameters
MAX_RISK_PER_TRADE = {risk_per_trade / 100}
MIN_RISK_REWARD_RATIO = {min_rr}
MAX_DAILY_DRAWDOWN = {max_drawdown / 100}
MAX_OPEN_POSITIONS = {max_positions}

# Position Sizing
MIN_LOT_SIZE = 0.01
MAX_LOT_SIZE = 1.0
LOT_SIZE_STEP = 0.01

# Stop Loss Rules
MIN_SL_DISTANCE_PIPS = 10
MAX_SL_DISTANCE_PIPS = 100

# Forex Specific
PIP_VALUE_PER_LOT = {{
    "EURUSD": 10,
    "GBPUSD": 10,
    "USDJPY": 9.09,
    "AUDUSD": 10,
}}

def get_pip_value(pair: str, lot_size: float = 1.0) -> float:
    base_value = PIP_VALUE_PER_LOT.get(pair, 10)
    return base_value * lot_size
"""
            st.code(config_code, language="python")
            st.caption("Copy this code to `src/config/risk_config.py` and restart the agent")
    
    st.markdown("---")
    
    # --- GOOGLE AI  SETTINGS ---
    st.subheader("🤖 AI Configuration (Google Gemini)")
    
    current_google_key = os.getenv("GOOGLE_API_KEY", "")
    masked_google = current_google_key[:8] + "..." + current_google_key[-4:] if len(current_google_key) > 12 else "Not Set"
    
    st.markdown(f"**Current API Key:** `{masked_google}`")
    
    with st.expander("🔧 Update Google AI Key"):
        new_google_key = st.text_input("Google API Key", value="", type="password", help="From ai.google.dev", key="google_key_input")
        
        if st.button("💾 Save AI Key"):
            if new_google_key:
                try:
                    import os
                    env_file = os.path.join(os.getcwd(), '.env')
                    set_key(env_file, 'GOOGLE_API_KEY', new_google_key)
                    st.success("✅ Google API Key updated in .env file! Restart agent to apply.")
                    st.info("💡 Run this command to restart: Close all windows and run START_ALL.bat")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please provide an API key")
    
    st.markdown("---")
    
    # --- SECURITY & MASTER KEY ---
    st.subheader("🔐 Security & Authentication")
    
    with st.expander("🔒 Change Admin Password"):
        st.info("Change the dashboard login credentials")
        
        current_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm New Password", type="password")
        
        if st.button("Update Password"):
            if new_pw and new_pw == confirm_pw:
                if len(new_pw) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    import bcrypt
                    hashed = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    try:
                        set_key('.env', 'ADMIN_PASSWORD_HASH', hashed)
                        st.success("✅ Password updated successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error("Passwords do not match")

    st.markdown("---")
    
    # --- DANGER ZONE ---
    with st.expander("🚨 Danger Zone"):
        st.error("**WARNING:** These actions are IRREVERSIBLE")
        
        col_danger1, col_danger2 = st.columns(2)
        
        with col_danger1:
            if st.button("🗑️ Clear All Trades", type="secondary"):
                st.warning("Feature disabled in production. Use database admin tools.")
        
        with col_danger2:
            if st.button("♻️ Reset All Settings", type="secondary"):
                st.warning("Feature disabled. Manually edit .env file if needed.")
