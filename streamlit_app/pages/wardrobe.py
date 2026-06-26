"""
StyleSync Wardrobe Page
"""
import os
import sys
import json
import streamlit as st
from components.sidebar import render_sidebar
from components.wardrobe import render_clothing_card

_HERE = os.path.abspath(__file__)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from wardrobe_adapter import scan_single_image, add_item_to_wardrobe

st.set_page_config(
    page_title="My Wardrobe - StyleSync",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css(css_file_path):
    if os.path.exists(css_file_path):
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_real_wardrobe():
    wardrobe_path = os.path.join(_PROJECT_ROOT, "wardrobe.json")
    if os.path.exists(wardrobe_path):
        with open(wardrobe_path, "r") as f:
            items = json.load(f)
            return list(reversed(items)) if isinstance(items, list) else list(reversed(items.get("items", [])))
    return []

def main():
    css_path = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "assets", "style.css")
    load_css(css_path)
    render_sidebar()

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #eef0f7 !important;
        color: #0a0a0a !important;
    }
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stMainBlockContainer"],
    .main, section.main > div, .block-container {
        background-color: #eef0f7 !important;
    }
    @media (prefers-color-scheme: dark) {
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"],
        [data-testid="stVerticalBlock"],
        [data-testid="stMainBlockContainer"],
        .main, section.main > div, .block-container {
            background-color: #eef0f7 !important;
            color: #0a0a0a !important;
        }
        p, span, div, label, li { color: #0a0a0a !important; }
    }
    .main .block-container { background: #eef0f7 !important; }

    .page-label {
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #7986cb;
        margin-bottom: 6px;
    }
    .page-title {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #0a0a0a;
        letter-spacing: -0.5px;
        line-height: 1.2;
        margin-bottom: 6px;
    }
    .page-subtitle {
        font-size: 0.95rem;
        color: #4a4a5a;
        margin-bottom: 24px;
    }
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #0a0a0a;
        margin-bottom: 12px;
    }
    .tips-box {
        background: #ffffff;
        border: 1.5px solid #d0d5e8;
        border-radius: 10px;
        padding: 14px 16px;
        margin-top: 16px;
    }
    .tips-label {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #7986cb;
        margin-bottom: 6px;
    }
    .tips-text {
        font-size: 0.82rem;
        color: #0a0a0a;
        line-height: 1.6;
    }
    </style>

    <div class="page-label">StyleSync AI</div>
    <div class="page-title">My Wardrobe.</div>
    <div class="page-subtitle">Upload your clothes — our AI will categorize them automatically.</div>
    <hr style="border:none;border-top:1px solid #d0d5e8;margin:8px 0 24px 0;">
    """, unsafe_allow_html=True)

    col_form, col_grid = st.columns([1, 2], gap="large")

    with col_form:
        st.markdown('<div class="section-title">Add New Item</div>', unsafe_allow_html=True)

        uploaded_image = st.file_uploader(
            "Upload Image",
            type=["png", "jpg", "jpeg"],
            help="Upload a clear photo of your clothing item."
        )

        if uploaded_image is not None:
            st.image(uploaded_image, caption="Preview", use_container_width=True)
            if st.button("Scan & Add to Wardrobe", use_container_width=True, type="primary"):
                with st.spinner("Analyzing your clothing item..."):
                    image_bytes = uploaded_image.getvalue()
                    scanned_data = scan_single_image(image_bytes, filename=uploaded_image.name)
                if scanned_data:
                    add_item_to_wardrobe(scanned_data)
                    st.success(
                        f"✅ Added: {scanned_data.get('color', '')} {scanned_data.get('category', '')} "
                        f"({scanned_data.get('style', '')})"
                    )
                    st.rerun()
                else:
                    st.error("Couldn't analyze this image. Please try a clearer photo.")

        st.markdown("""
        <div class="tips-box">
            <div class="tips-label">💡 For best results</div>
            <div class="tips-text">
                • Use a plain white or neutral background<br>
                • Photograph one item at a time<br>
                • Include the full item in frame<br>
                • Good lighting helps accuracy
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_grid:
        items = load_real_wardrobe()
        total = len(items)

        col_title, col_count = st.columns([3, 1])
        with col_title:
            st.markdown('<div class="section-title">Digital Closet</div>', unsafe_allow_html=True)
        with col_count:
            st.markdown(
                f'<div style="text-align:right;padding-top:4px;font-size:0.82rem;'
                f'font-weight:600;color:#7986cb;">{total} items</div>',
                unsafe_allow_html=True
            )

        if not items:
            st.info("Your wardrobe is empty. Upload your first item using the form!")
        else:
            categories = ["All"] + sorted({i.get("category", "Other") for i in items})
            selected = st.selectbox("Filter by category", categories, label_visibility="collapsed")
            filtered = items if selected == "All" else [i for i in items if i.get("category") == selected]

            card_cols = st.columns(3)
            for index, item in enumerate(filtered):
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