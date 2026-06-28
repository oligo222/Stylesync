"""
StyleSync Sign Up Page

Streamlit entry point for user registration.
"""
import os
import sys
import streamlit as st

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from authentication.auth_utils import init_session
from authentication.signup import render_signup_page

st.set_page_config(
    page_title="Sign Up - StyleSync",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def main():
    init_session()
    
    # If already logged in, redirect to Profile
    if st.session_state.get("logged_in"):
        st.switch_page("pages/profile.py")
        st.stop()
        
    render_signup_page()

if __name__ == "__main__":
    main()
