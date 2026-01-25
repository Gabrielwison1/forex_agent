import streamlit as st
from src.dashboard.auth import check_password, logout
from src.dashboard import dashboard as live_monitor
from src.dashboard.views import settings, admin
from src.database.models import init_db # Import for auto-setup

# Ensure database tables exist (Critical for Cloud cold-starts)
init_db()

st.set_page_config(layout="wide", page_title="Premium FX Agent", page_icon="🦅")

# Global CSS
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
</style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION ---
if not check_password():
    st.stop()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🦅 Navigator")
page = st.sidebar.radio("Go to", ["Live War Room", "Settings Manager", "Admin Deep Dive"])

st.sidebar.markdown("---")
st.sidebar.caption("Logged in as Super Admin")
if st.sidebar.button("Logout"):
    logout()
    st.rerun()

# --- ROUTING ---
if page == "Live War Room":
    live_monitor.app()
elif page == "Settings Manager":
    settings.app()
elif page == "Admin Deep Dive":
    admin.app()
