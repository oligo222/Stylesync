"""
StyleSync Event Planner Page
"""
import os
import sys
import streamlit as st
from components.sidebar import render_sidebar

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from main import run_pipeline

st.set_page_config(
    page_title="Event Planner - StyleSync",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    .outfit-result-card {
        background: #ffffff;
        border: 1.5px solid #d0d5e8;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 16px;
        box-shadow: 0 0 14px rgba(129,199,132,0.2);
    }
    .result-score {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        background: #e8f5e9;
        border: 1.5px solid #a5d6a7;
        display: inline-block;
        padding: 3px 14px;
        margin-bottom: 14px;
        color: #0a0a0a;
        border-radius: 6px;
    }
    .result-label {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #7986cb;
        margin-bottom: 6px;
    }
    .result-item {
        font-size: 0.95rem;
        font-weight: 500;
        color: #0a0a0a;
        padding: 6px 0;
        border-bottom: 1px solid #eef0f7;
    }
    .result-note {
        border-left: 3px solid #a5d6a7;
        padding: 10px 14px;
        background: #f1f8f1;
        color: #0a0a0a;
        margin-top: 14px;
        border-radius: 0 8px 8px 0;
        font-size: 0.88rem;
        line-height: 1.6;
    }
    .event-results-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #0a0a0a;
        margin-bottom: 16px;
    }
    </style>

    <div class="page-label">StyleSync AI</div>
    <div class="page-title">Plan Your Perfect Look.</div>
    <div class="page-subtitle">Tell us your event — we'll build outfits from what you already own.</div>
    <hr style="border:none;border-top:1px solid #d0d5e8;margin:8px 0 24px 0;">
    """, unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            event_name = st.text_input("Event Name", placeholder="e.g. Summer Wedding, Tech Conference")
            event_date = st.date_input("Date")
            location = st.text_input("Location / Venue", placeholder="e.g. Central Park, Ritz-Carlton")
        with col2:
            event_time = st.time_input("Time")
            dress_code = st.selectbox("Dress Code", [
                "Casual", "Smart Casual", "Business Casual",
                "Cocktail Attire", "Formal / Black Tie",
                "Athletic / Activewear", "Festival / Costume", "Other"
            ])
            venue_setting = st.radio("Venue Setting", ["Indoor", "Outdoor", "Mixed / Unsure"], horizontal=True)

    st.markdown('<hr style="border:none;border-top:1px solid #d0d5e8;margin:8px 0 24px 0;">', unsafe_allow_html=True)

    if st.button("Generate Outfit Suggestion", use_container_width=True):
        if not event_name:
            st.warning("Please enter an event name to generate an outfit suggestion.")
        else:
            event_description = (
                f"{event_name}, a {dress_code} event, "
                f"{venue_setting} setting, on {event_date} at {event_time}"
            )
            with st.spinner("StyleSync AI is selecting the best combinations from your wardrobe..."):
                result = run_pipeline(event_description)

            recommendations = result.get("recommendations", [])

            if not recommendations:
                st.warning("No outfit recommendations could be generated. Try a different event description.")
            else:
                st.markdown(f"""
                <div class="result-label" style="margin-top:8px;">Results for</div>
                <div class="event-results-title">{event_name}</div>
                """, unsafe_allow_html=True)

                for i, outfit in enumerate(recommendations):
                    items_html = ""
                    if outfit.get("top"):
                        items_html += f'<div class="result-item">👕 &nbsp; Top &nbsp;·&nbsp; {outfit["top"]}</div>'
                    if outfit.get("bottom"):
                        items_html += f'<div class="result-item">👖 &nbsp; Bottom &nbsp;·&nbsp; {outfit["bottom"]}</div>'
                    if outfit.get("footwear"):
                        items_html += f'<div class="result-item">👞 &nbsp; Footwear &nbsp;·&nbsp; {outfit["footwear"]}</div>'

                    st.markdown(f"""
                    <div class="outfit-result-card">
                        <div class="result-label">Look {i+1}</div>
                        <div class="result-score">{outfit.get('suitability_score', '?')} / 100</div>
                        <div class="result-label" style="margin-top:8px;">What to wear</div>
                        {items_html}
                        <div class="result-note">{outfit.get('explanation', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()