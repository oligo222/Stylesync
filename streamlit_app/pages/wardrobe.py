"""
StyleSync Wardrobe Page

Allows users to upload clothing photos, which are automatically scanned
and categorized using Gemini Vision, and view their digital wardrobe.
"""
import os
import sys
import json
import streamlit as st
from components.sidebar import render_sidebar
from components.wardrobe import render_clothing_card

# Allow importing from project root (where wardrobe_adapter.py lives)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from wardrobe_adapter import scan_single_image, add_item_to_wardrobe

st.set_page_config(
    page_title="My Wardrobe - StyleSync",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css(css_file_path):
    if os.path.exists(css_file_path):
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_real_wardrobe():
    """Loads the actual scanned wardrobe.json from the project root,
    showing most recently added items first."""
    wardrobe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "wardrobe.json")
    if os.path.exists(wardrobe_path):
        with open(wardrobe_path, "r") as f:
            items = json.load(f)
            return list(reversed(items))
    return []

def main():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    load_css(css_path)
    render_sidebar()

    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="font-weight: 700; margin-bottom: 4px;">👗 My Wardrobe</h1>
            <p style="color: #6b7280; font-size: 1.1rem; margin: 0;">
                Upload your clothes — our AI will categorize them automatically.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("---")

    col_form, col_grid = st.columns([1, 2], gap="large")

    with col_form:
        st.write("### Add New Item")

        uploaded_image = st.file_uploader(
            "Upload Image",
            type=["png", "jpg", "jpeg"],
            help="Upload a clear photo of your clothing item — we'll detect the category, color, and style automatically."
        )

        if uploaded_image is not None:
            if st.button("Scan & Add to Wardrobe", use_container_width=True):
                with st.spinner("Analyzing your clothing item..."):
                    image_bytes = uploaded_image.getvalue()
                    scanned_data = scan_single_image(image_bytes, filename=uploaded_image.name)

                if scanned_data:
                    add_item_to_wardrobe(scanned_data)
                    st.success(
                        f"Added: {scanned_data.get('color', '')} {scanned_data.get('category', '')} "
                        f"({scanned_data.get('style', '')})"
                    )
                    st.rerun()
                else:
                    st.error("Couldn't analyze this image. Please try a clearer photo.")

    with col_grid:
        st.write("### Digital Closet")

        items = load_real_wardrobe()

        if not items:
            st.info("Your wardrobe is empty. Use the form on the left to upload your first item!")
        else:
            card_cols = st.columns(3)
            for index, item in enumerate(items):
                col_index = index % 3
                with card_cols[col_index]:
                    image_path = item.get("image_path")
                    image_to_show = image_path if image_path and os.path.exists(image_path) else None

                    render_clothing_card({
                        "type": item.get("category", "Item").title(),
                        "color": item.get("color", "").title(),
                        "color_hex": "#cccccc",
                        "season": "All Seasons",
                        "style": item.get("style", "").title(),
                        "occasion": item.get("style", "").title(),
                        "image": image_to_show
                    })

if __name__ == "__main__":
    main()
