import streamlit as st
import os
import time
import hashlib
import secrets
from dotenv import load_dotenv
from src.dashboard.utils import verify_master_key, update_admin_password

load_dotenv()

import streamlit as st
import os
import time
from dotenv import load_dotenv
from src.dashboard.utils import verify_master_key, update_admin_password

load_dotenv()

def check_password():
    """Premium Authentication UI with High-Fidelity Glassmorphism."""
    
    # --- HIGH-FIDELITY CSS INJECTION ---
    st.markdown("""
        <style>
        /* Import Inter Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Animated Background Glows */
        .stApp {
            background-color: #050505;
            overflow: hidden;
        }
        
        .glow-container {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: 0;
            pointer-events: none;
        }
        
        .glow-1 {
            position: absolute;
            width: 500px; height: 500px;
            background: radial-gradient(circle, rgba(255, 77, 77, 0.15) 0%, rgba(0,0,0,0) 70%);
            top: -100px; left: -100px;
            border-radius: 50%;
            filter: blur(50px);
        }
        
        .glow-2 {
            position: absolute;
            width: 600px; height: 600px;
            background: radial-gradient(circle, rgba(66, 135, 245, 0.1) 0%, rgba(0,0,0,0) 70%);
            bottom: -150px; right: -100px;
            border-radius: 50%;
            filter: blur(50px);
        }

        /* TARGETING THE MIDDLE COLUMN TO BE THE GLASS CARD */
        div[data-testid="column"]:nth-of-type(2) {
            background: rgba(255, 255, 255, 0.07); /* Increased opacity */
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 255, 255, 0.15); /* Brighter border */
            border-radius: 28px;
            padding: 40px;
            box-shadow: 0 4px 60px rgba(0, 0, 0, 0.5); /* Deeper shadow */
            margin-top: 5vh; /* Adjusted centering */
        }

        /* Typography */
        .brand-title {
            font-family: 'Inter', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: white;
            text-align: center;
            margin-bottom: 5px;
        }
        .brand-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #6b7280;
            text-align: center;
            margin-bottom: 30px;
        }
        .eagle-icon {
            font-size: 48px;
            text-align: center;
            margin-bottom: 15px;
            filter: drop-shadow(0 0 15px rgba(255, 77, 77, 0.3));
        }

        /* Custom Input Styling */
        .stTextInput input {
            background: rgba(0, 0, 0, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            color: white !important;
            padding: 15px !important;
        }
        .stTextInput input:focus {
            border-color: rgba(255, 77, 77, 0.5) !important;
            box-shadow: 0 0 15px rgba(255, 77, 77, 0.1) !important;
        }
        label { color: #9ca3af !important; font-size: 12px !important; }

        /* Buttons */
        div.stButton > button.element-container { width: 100%; }
        
        button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #ff4d4d 0%, #d60000 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            height: 48px !important;
            width: 100% !important;
        }
        
        button[data-testid="baseButton-secondary"] {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #d1d5db !important;
            border-radius: 12px !important;
            height: 48px !important;
            width: 100% !important;
        }
        
        .footer-link {
            text-align: center;
            margin-top: 20px; 
            font-size: 11px; color: #555; 
        }
        </style>
        
        <div class="glow-container">
            <div class="glow-1"></div>
            <div class="glow-2"></div>
        </div>
    """, unsafe_allow_html=True)

    if "auth_state" not in st.session_state:
        st.session_state["auth_state"] = "login"

    # Layout: Use empty columns to center content
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    
    with col2:
        if st.session_state.get("password_correct", False):
            return True

        # --- LOGIN CONTENT ---
        if st.session_state["auth_state"] == "login":
            st.markdown('<div class="eagle-icon">🦅</div>', unsafe_allow_html=True)
            st.markdown('<div class="brand-title">Forex Agent Premium</div>', unsafe_allow_html=True)
            st.markdown('<div class="brand-subtitle">Authorized Access Only</div>', unsafe_allow_html=True)

            pwd = st.text_input("Secure Password", type="password", key="login_pwd", placeholder="Enter access key...")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Using columns inside the card for buttons
            b1, b2 = st.columns([2, 1])
            with b1:
                if st.button("Authenticate", type="primary", use_container_width=True):
                    load_dotenv(override=True)
                    # Verify Hash
                    stored_hash = os.getenv("ADMIN_PASSWORD_HASH", "")
                    input_hash = hashlib.sha256(pwd.strip().encode()).hexdigest()
                    
                    if secrets.compare_digest(input_hash, stored_hash):
                        st.session_state["password_correct"] = True
                        st.balloons()
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Access Denied")
            with b2:
                if st.button("Reset", type="secondary", use_container_width=True):
                    st.session_state["auth_state"] = "reset_request"
                    st.rerun()
            
            st.markdown('<div class="footer-link">Request Access Permissions</div>', unsafe_allow_html=True)


        # --- RESET REQUEST CONTENT ---
        elif st.session_state["auth_state"] == "reset_request":
            st.markdown('<div class="eagle-icon">🔐</div>', unsafe_allow_html=True)
            st.markdown('<div class="brand-title">System Recovery</div>', unsafe_allow_html=True)
            st.markdown('<div class="brand-subtitle">Master Key Protocol</div>', unsafe_allow_html=True)

            master_key = st.text_input("Master Recovery Key", type="password", help="Found in your .env file")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Verify Identity", type="primary", use_container_width=True):
                if verify_master_key(master_key):
                    st.session_state["auth_state"] = "reset_confirm"
                    st.session_state["verified_master_reset"] = True
                    st.rerun()
                else:
                    st.error("Invalid Master Key")
            
            if st.button("Back to Login", type="secondary", use_container_width=True):
                st.session_state["auth_state"] = "login"
                st.rerun()

        # --- UPDATE CONTENT ---
        elif st.session_state["auth_state"] == "reset_confirm":
            if not st.session_state.get("verified_master_reset"):
                st.session_state["auth_state"] = "login"
                st.rerun()

            st.markdown('<div class="eagle-icon">✨</div>', unsafe_allow_html=True)
            st.markdown('<div class="brand-title">New Credentials</div>', unsafe_allow_html=True)
            st.markdown('<div class="brand-subtitle">Set Secure Password</div>', unsafe_allow_html=True)

            new_pwd = st.text_input("New Password", type="password", placeholder="New password")
            confirm_pwd = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Update Access Key", type="primary", use_container_width=True):
                if new_pwd and new_pwd == confirm_pwd:
                    update_admin_password(new_pwd)
                    st.success("Updated. Redirecting...")
                    time.sleep(1.5)
                    st.session_state["auth_state"] = "login"
                    st.rerun()
                else:
                    st.error("Passwords do not match.")

    return False

def logout():
    """Logs the user out."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

