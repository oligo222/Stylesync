"""
StyleSync Main Dashboard Application Entrypoint

This file handles layout setup, imports CSS styling, and assembles
the core dashboard view (metrics, recent outfits, stats, sidebar).
"""
import os
import streamlit as st
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
    # Load custom branding CSS
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    load_css(css_path)
    
    # Render modular sidebar component
    render_sidebar(user_name="Alex", membership_tier="Premium Member")
    
    # Welcome Banner Section
    render_welcome_banner(user_name="Alex")
    
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
