"""
StyleSync User Profile Page

Streamlit entry point for user profile, routing to profile/profile_page.py.
"""
import os
import sys
import streamlit as st

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from user_profile.profile_page import render_profile_page
st.set_page_config(
    page_title="My Profile - StyleSync",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    render_profile_page()

if __name__ == "__main__":
    main()
