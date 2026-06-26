"""
StyleSync Style Insights Page
"""
import os
import sys
import json
import streamlit as st
from components.sidebar import render_sidebar

_HERE = os.path.abspath(__file__)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from palette_engine import render_palette_card
from gap_detector import render_gap_report
from shopping_advisor import render_shopping_advisor

st.set_page_config(
    page_title="Style Insights - StyleSync",
    page_icon="🛍️",
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
            raw = json.load(f)
            return raw if isinstance(raw, list) else raw.get("items", [])
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
    </style>

    <div class="page-label">StyleSync AI</div>
    <div class="page-title">Style Insights.</div>
    <div class="page-subtitle">Your wardrobe intelligence — color profile, gaps, and smart shopping picks.</div>
    <hr style="border:none;border-top:1px solid #d0d5e8;margin:8px 0 24px 0;">
    """, unsafe_allow_html=True)

    items = load_real_wardrobe()

    if not items:
        st.info("Your wardrobe is empty. Head to **My Wardrobe** to upload your first item!")
        return

    render_palette_card(items)
    st.markdown('<hr style="border:none;border-top:1px solid #d0d5e8;margin:16px 0 24px 0;">', unsafe_allow_html=True)
    render_gap_report(items)
    st.markdown('<hr style="border:none;border-top:1px solid #d0d5e8;margin:16px 0 24px 0;">', unsafe_allow_html=True)
    render_shopping_advisor(items)

if __name__ == "__main__":
    main()