"""
StyleSync Recommendations Page
"""
import os
import json
import streamlit as st
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="AI Recommendations - StyleSync",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_latest_recommendations():
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "output", "recommendations.json"
    )
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            return json.load(f)
    return None

def main():
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
    .event-tag {
        display: inline-block;
        font-family: 'Inter', sans-serif;
        font-size: 0.88rem;
        font-weight: 600;
        background: #e8eaf6;
        color: #0a0a0a;
        border: 1.5px solid #c5cae9;
        padding: 4px 14px;
        margin-bottom: 6px;
        border-radius: 6px;
    }
    .event-reasoning {
        font-size: 0.88rem;
        color: #4a4a5a;
        margin-bottom: 24px;
    }
    .outfit-card {
        background: #ffffff;
        border: 1.5px solid #d0d5e8;
        border-radius: 12px;
        padding: 24px 26px;
        margin-bottom: 20px;
        box-shadow: 0 0 14px rgba(129,199,132,0.2);
    }
    .outfit-number {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #7986cb;
        margin-bottom: 4px;
    }
    .outfit-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #0a0a0a;
        margin-bottom: 12px;
    }
    .score-badge {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        background: #e8f5e9;
        border: 1.5px solid #a5d6a7;
        display: inline-block;
        padding: 3px 14px;
        margin-bottom: 16px;
        color: #0a0a0a;
        border-radius: 6px;
    }
    .items-label {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #7986cb;
        margin-bottom: 8px;
    }
    .item-row {
        font-size: 0.92rem;
        font-weight: 500;
        color: #0a0a0a;
        padding: 7px 0;
        border-bottom: 1px solid #eef0f7;
    }
    .note-label {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #7986cb;
        margin-top: 16px;
        margin-bottom: 6px;
    }
    .stylist-note {
        border-left: 3px solid #a5d6a7;
        padding: 10px 14px;
        background: #f1f8f1;
        font-size: 0.88rem;
        color: #0a0a0a;
        margin-top: 4px;
        line-height: 1.6;
        border-radius: 0 8px 8px 0;
    }
    .empty-card {
        background: #ffffff;
        border: 1.5px solid #d0d5e8;
        border-radius: 12px;
        padding: 36px 28px;
        margin-top: 24px;
        box-shadow: 0 0 14px rgba(129,199,132,0.2);
    }
    .divider {
        border: none;
        border-top: 1px solid #d0d5e8;
        margin: 8px 0 24px 0;
    }
    </style>

    <div class="page-label">StyleSync AI</div>
    <div class="page-title">Your Outfits, Reimagined.</div>
    <div class="page-subtitle">AI-generated looks built entirely from your existing wardrobe.</div>
    <hr style="border:none;border-top:1px solid #d0d5e8;margin:8px 0 24px 0;">
    """, unsafe_allow_html=True)

    data = load_latest_recommendations()

    if not data or not data.get("recommendations"):
        st.markdown("""
        <div class="empty-card">
            <div class="page-label">Nothing here yet</div>
            <div class="outfit-title">No Recommendations</div>
            <p style="font-size:0.92rem;color:#4a4a5a;margin-top:8px;">
                Head to the <strong>Event</strong> page, describe an upcoming event,
                and your AI-generated outfits will appear here.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    event_info = data.get("event_analysis", {})
    recommendations = data.get("recommendations", [])

    st.markdown(f"""
    <div class="event-tag">— {event_info.get('occasion_type', 'Your Event')} · {event_info.get('event_style', '')} —</div>
    <div class="event-reasoning">{event_info.get('reasoning', '')}</div>
    """, unsafe_allow_html=True)

    for i, outfit in enumerate(recommendations):
        items_html = ""
        if outfit.get("top"):
            items_html += f'<div class="item-row">👕 &nbsp; Top &nbsp;·&nbsp; {outfit["top"]}</div>'
        if outfit.get("bottom"):
            items_html += f'<div class="item-row">👖 &nbsp; Bottom &nbsp;·&nbsp; {outfit["bottom"]}</div>'
        if outfit.get("footwear"):
            items_html += f'<div class="item-row">👞 &nbsp; Footwear &nbsp;·&nbsp; {outfit["footwear"]}</div>'

        st.markdown(f"""
        <div class="outfit-card">
            <div class="outfit-number">Look {i+1} of {len(recommendations)}</div>
            <div class="outfit-title">Outfit {i+1}</div>
            <div class="score-badge">{outfit.get('suitability_score', '?')} / 100</div>
            <div class="items-label">What to wear</div>
            {items_html}
            <div class="note-label">Stylist Note</div>
            <div class="stylist-note">{outfit.get('explanation', 'No explanation available.')}</div>
        </div>
        <hr class="divider"/>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()