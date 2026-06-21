"""
StyleSync Reusable Wardrobe Components

Provides rendering elements for individual clothing items and collections.
"""
import streamlit as st

def render_clothing_card(item: dict):
    """
    Renders a clothing card using native Streamlit components.
    Guaranteed to render correctly regardless of CSS/escaping issues.
    """
    with st.container(border=True):
        # 1. Handle image rendering safely
        if item.get("image"):
            st.image(item["image"], use_container_width=True)
        else:
            # Completely native fallback wrapper 
            st.header("👕")
            
        # 2. Main item heading
        st.subheader(item.get('type', 'Unknown Item'), divider="gray")

        # 3. Dynamic clean tags using inline markdown styling
        tags = [
            f"**Color:** {item.get('color')}" if item.get('color') else None,
            item.get("season"),
            item.get("style"),
            item.get("occasion"),
        ]
        
        # Filter out empty fields and display cleanly
        clean_tags = "  •  ".join(filter(None, tags))
        st.markdown(clean_tags)