"""
StyleSync Main Dashboard Application Entrypoint

This file handles layout setup, imports CSS styling, and assembles
the core dashboard view (metrics, recent outfits, stats, sidebar).
"""
import os
import sys
import streamlit as st

# Allow importing from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from authentication.auth_utils import require_login
from components.sidebar import render_sidebar
from components.dashboard import render_welcome_banner, render_metric_cards
from components.outfits import render_recent_outfits
from components.stats import render_wardrobe_stats

st.set_page_config(
    page_title="StyleSync - AI Fashion Stylist Dashboard",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css(css_file_path):
    """
    Loads custom CSS from file and injects it into streamlit app layout.
    """
    if os.path.exists(css_file_path):
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    # Require login first
    require_login()

    # Load custom branding CSS
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    load_css(css_path)
    
    # Get current user name dynamically
    user = st.session_state.get("user", {})
    user_name = user.get("name", "User")
    
    # Render modular sidebar component
    render_sidebar(user_name=user_name, membership_tier="Premium Member")
    
    # Welcome Banner Section
    render_welcome_banner(user_name=user_name)
    
    st.write("---")
    
    # Metric cards row
    render_metric_cards(
        total_items=142,
        outfits_count=38,
        style_score=92,
        requests_pending=2
    )
    
    st.write("---")
    
    # Main contents split into outfits and stats
    render_recent_outfits()
    
    st.write("---")
    
    render_wardrobe_stats()

if __name__ == "__main__":
    main()
