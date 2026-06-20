"""
StyleSync Reusable Wardrobe Components

Provides rendering elements for individual clothing items and collections.
"""
import streamlit as st
from PIL import Image

def render_clothing_card(item: dict):
    """
    Renders an aesthetic clothing card containing an image (or placeholder) and item metadata.
    """
    with st.container():
        # HTML structure for the card start
        st.markdown('<div class="clothing-card">', unsafe_allow_html=True)
        
        # Image rendering section
        if item.get("image") is not None:
            # Display uploaded image
            st.image(item["image"], use_container_width=True)
        else:
            # Display placeholder emoji box
            st.markdown(
                """
                <div style="height: 180px; background-color: #f3f4f6; display: flex; align-items: center; justify-content: center; font-size: 3rem;">
                    👕
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Metadata / details rendering section
        pills_html = f"""
            <span class="clothing-pill" style="border-left: 3px solid {item['color_hex']}; padding-left: 8px;">{item['color']}</span>
            <span class="clothing-pill">{item['season']}</span>
            <span class="clothing-pill">{item['style']}</span>
            <span class="clothing-pill">{item['occasion']}</span>
        """
        
        st.markdown(
            f"""
            <div class="clothing-details">
                <h4 class="clothing-type">{item['type']}</h4>
                <div class="clothing-meta">
                    {pills_html}
                </div>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )
