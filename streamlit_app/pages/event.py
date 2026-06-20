"""
StyleSync Event Planner Page

Allows users to plan outfits for upcoming events.
"""
import os
import streamlit as st
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Event Planner - StyleSync",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css(css_file_path):
    """
    Loads custom styling CSS.
    """
    if os.path.exists(css_file_path):
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    # Setup styling and sidebar
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    load_css(css_path)
    render_sidebar()
    
    # Page Header
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="font-weight: 700; margin-bottom: 4px;">📅 Event Outfit Planner</h1>
            <p style="color: #6b7280; font-size: 1.1rem; margin: 0;">
                Tell us about your upcoming event, and StyleSync will design the perfect look for you.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.write("---")
    
    # Form Layout
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            event_name = st.text_input(
                "Event Name",
                placeholder="e.g. Summer Wedding, Friday Gala, Tech Conference"
            )
            
            event_date = st.date_input("Date")
            
            location = st.text_input(
                "Location / Venue",
                placeholder="e.g. Central Park, Ritz-Carlton Ballroom, Office"
            )
            
        with col2:
            event_time = st.time_input("Time")
            
            dress_code = st.selectbox(
                "Dress Code",
                [
                    "Casual",
                    "Smart Casual",
                    "Business Casual",
                    "Cocktail Attire",
                    "Formal / Black Tie",
                    "Athletic / Activewear",
                    "Festival / Costume",
                    "Other"
                ]
            )
            
            venue_setting = st.radio(
                "Venue Setting",
                ["Indoor", "Outdoor", "Mixed / Unsure"],
                horizontal=True
            )
            
    st.write("---")
    
    # Generate Outfit Button
    if st.button("✨ Generate Outfit Suggestion", use_container_width=True):
        if not event_name:
            st.warning("Please enter an event name to generate an outfit suggestion.")
        else:
            st.success(f"Processing outfit request for **{event_name}**!")
            st.info(
                "StyleSync AI is selecting the best combinations from your wardrobe... "
                "(Backend model integration coming soon!)"
            )

if __name__ == "__main__":
    main()
