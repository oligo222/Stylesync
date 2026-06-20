"""
StyleSync Wardrobe Page

Allows users to upload, classify, and view their clothing items.
"""
import os
import streamlit as st
from components.sidebar import render_sidebar
from components.wardrobe import render_clothing_card

st.set_page_config(
    page_title="My Wardrobe - StyleSync",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css(css_file_path):
    """
    Loads custom CSS from file.
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
            <h1 style="font-weight: 700; margin-bottom: 4px;">👗 My Wardrobe</h1>
            <p style="color: #6b7280; font-size: 1.1rem; margin: 0;">
                Upload your clothes and organize your digital wardrobe.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.write("---")
    
    # Initialize session state for wardrobe items if not exists
    if "wardrobe_items" not in st.session_state:
        st.session_state.wardrobe_items = [
            {
                "type": "Beige Trench Coat",
                "color": "Beige",
                "color_hex": "#f5f5dc",
                "season": "Autumn",
                "style": "Classic",
                "occasion": "Work",
                "image": None
            },
            {
                "type": "Navy Knit Sweater",
                "color": "Navy",
                "color_hex": "#000080",
                "season": "Winter",
                "style": "Minimalist",
                "occasion": "Casual",
                "image": None
            },
            {
                "type": "White Silk Blouse",
                "color": "White",
                "color_hex": "#ffffff",
                "season": "Spring",
                "style": "Chic",
                "occasion": "Cocktail",
                "image": None
            }
        ]
        
    # Split layout into Upload Form (left) and Wardrobe Grid (right)
    col_form, col_grid = st.columns([1, 2], gap="large")
    
    with col_form:
        st.write("### Add New Item")
        
        # Upload Fields
        uploaded_image = st.file_uploader(
            "Upload Image",
            type=["png", "jpg", "jpeg"],
            help="Upload a clear photo of your clothing item."
        )
        
        clothing_type = st.selectbox(
            "Clothing Type",
            [
                "T-Shirt / Top",
                "Blouse / Shirt",
                "Sweater / Knitwear",
                "Blazer / Jacket",
                "Coat / Outerwear",
                "Jeans / Pants",
                "Skirt / Shorts",
                "Dress",
                "Sneakers / Shoes",
                "Boots",
                "Accessory"
            ]
        )
        
        color_name = st.text_input("Color Name", value="Black")
        color_hex = st.color_picker("Pick Exact Color shade", value="#000000")
        
        season = st.selectbox(
            "Season Compatibility",
            ["All Seasons", "Spring", "Summer", "Autumn", "Winter"]
        )
        
        style = st.selectbox(
            "Primary Style",
            ["Minimalist", "Classic", "Bohemian", "Edgy / Streetwear", "Vintage / Retro", "Chic", "Preppy", "Casual"]
        )
        
        occasion = st.selectbox(
            "Primary Occasion",
            ["Casual", "Smart Casual", "Business Casual", "Formal / Black Tie", "Cocktail Attire", "Athletic / Activewear", "Party"]
        )
        
        # Upload Action
        if st.button("Upload to Wardrobe", use_container_width=True):
            new_item = {
                "type": clothing_type,
                "color": color_name,
                "color_hex": color_hex,
                "season": season,
                "style": style,
                "occasion": occasion,
                "image": uploaded_image
            }
            st.session_state.wardrobe_items.insert(0, new_item)
            st.success(f"Successfully uploaded {clothing_type} to your wardrobe!")
            
    with col_grid:
        st.write("### Digital Closet")
        
        items = st.session_state.wardrobe_items
        
        if not items:
            st.info("Your wardrobe is empty. Use the form on the left to upload your first item!")
        else:
            # Display items in a responsive grid (3 cards per row)
            card_cols = st.columns(3)
            for index, item in enumerate(items):
                col_index = index % 3
                with card_cols[col_index]:
                    render_clothing_card(item)

if __name__ == "__main__":
    main()
