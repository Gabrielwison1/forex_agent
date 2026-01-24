import streamlit as st
import os
from dotenv import set_key

def app():
    st.header("⚙️ System Settings")
    st.caption("Secure Configuration Management")
    
    st.markdown("---")
    
    # --- OANDA SETTINGS ---
    st.subheader("Broker Connection (OANDA)")
    
    current_key = os.getenv("OANDA_API_KEY", "")
    new_key = st.text_input("OANDA API Key", value=current_key, type="password", help="Your personal access token")
    
    current_id = os.getenv("OANDA_ACCOUNT_ID", "")
    new_id = st.text_input("Account ID", value=current_id)
    
    env_type = st.radio("Environment", ["Demo", "Live"], index=0)
    
    if st.button("Save Broker Settings"):
        # In a real app, use .env or secure vault
        # set_key('.env', 'OANDA_API_KEY', new_key)
        # set_key('.env', 'OANDA_ACCOUNT_ID', new_id)
        st.success("Configuration saved! Restart agent to apply.")
        
    st.markdown("---")
    
    # --- RISK SETTINGS ---
    st.subheader("Risk Parameters")
    
    risk_per_trade = st.slider("Risk Per Trade (%)", 0.1, 5.0, 1.0, 0.1)
    max_drawdown = st.slider("Max Daily Drawdown (%)", 1.0, 10.0, 3.0, 0.5)
    
    st.markdown("---")
    
    # --- DANGER ZONE ---
    with st.expander("🚨 Danger Zone"):
        st.warning("These actions are irreversible.")
        if st.button("Flush Trade Database"):
            st.error("Feature disabled in Demo mode.")
