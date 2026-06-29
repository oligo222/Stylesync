"""
StyleSync Main Dashboard
"""
import os
import sys
import json
import streamlit as st

# Allow importing from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from authentication.auth_utils import require_login, init_session
from components.sidebar import render_sidebar
from components.dashboard import render_welcome_banner, render_metric_cards
from components.outfits import render_recent_outfits
from components.stats import render_wardrobe_stats

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from wardrobe_adapter import load_and_adapt
from revival_engine import render_revival_section

st.set_page_config(
    page_title="StyleSync - AI Fashion Stylist Dashboard",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css(css_file_path):
    if os.path.exists(css_file_path):
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_real_dashboard_stats():
    project_root = os.path.dirname(os.path.dirname(__file__))
    try:
        wardrobe_path = os.path.join(project_root, "wardrobe.json")
        adapted = load_and_adapt(wardrobe_path)
        total_items = len(adapted.get("items", []))
    except Exception:
        total_items = 0

    outfits_count = 0
    style_score = 0
    try:
        history_path = os.path.join(project_root, "data", "usage_history.json")
        if os.path.exists(history_path):
            with open(history_path, "r") as f:
                history = json.load(f)
            used_items = history.get("used_items", [])
            outfits_count = max(0, len(used_items) // 3)
            scores = history.get("scores", [])
            if scores:
                style_score = round(sum(scores) / len(scores))
    except Exception:
        pass

    requests_pending = 0
    try:
        rec_path = os.path.join(project_root, "output", "recommendations.json")
        if os.path.exists(rec_path):
            with open(rec_path, "r") as f:
                rec_data = json.load(f)
            requests_pending = len(rec_data.get("recommendations", []))
    except Exception:
        pass

    return total_items, outfits_count, style_score, requests_pending

def load_wardrobe_and_history():
    project_root = os.path.dirname(os.path.dirname(__file__))
    wardrobe = []
    history = {}
    try:
        wardrobe_path = os.path.join(project_root, "wardrobe.json")
        if os.path.exists(wardrobe_path):
            with open(wardrobe_path, "r") as f:
                raw = json.load(f)
                wardrobe = raw if isinstance(raw, list) else raw.get("items", [])
    except Exception:
        pass
    try:
        history_path = os.path.join(project_root, "data", "usage_history.json")
        if os.path.exists(history_path):
            with open(history_path, "r") as f:
                history = json.load(f)
    except Exception:
        pass
    return wardrobe, history

def show_profile_setup_prompt(user):
    """Show a popup if appearance hasn't been set up yet."""
    traits = ["skin_tone", "hair_color", "body_type", "face_shape"]
    all_unknown = all(user.get(t, "Unknown") in (None, "Unknown") for t in traits)

    if not all_unknown:
        return  # Already set up, don't show

    # Only show once per session
    if st.session_state.get("_profile_prompt_dismissed"):
        return

    @st.dialog("👤 Complete Your Profile")
    def _prompt():
        st.markdown("""
            <div style="text-align:center; padding: 8px 0 16px 0;">
                <div style="font-size: 2rem;">✨</div>
                <div style="font-weight: 700; font-size: 1.1rem; margin: 8px 0 4px;">
                    Set up your appearance profile
                </div>
                <div style="color: #6b7280; font-size: 0.9rem; line-height: 1.6;">
                    Upload a photo so StyleSync can auto-detect your skin tone, hair, body type and more —
                    and give you truly personalized style recommendations.
                </div>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Go to Profile", use_container_width=True, type="primary"):
                st.switch_page("pages/profile.py")
        with col2:
            if st.button("Maybe Later", use_container_width=True):
                st.session_state["_profile_prompt_dismissed"] = True
                st.rerun()

    _prompt()

def main():
    # ── Auth gate ──
    init_session()
    if not st.session_state.get("logged_in"):
        st.switch_page("pages/profile.py")
        st.stop()

    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    load_css(css_path)

    user = st.session_state.get("user", {})
    user_name = user.get("name", "Alex")

    # ── Show profile setup popup if appearance not filled ──
    show_profile_setup_prompt(user)

    render_sidebar(user_name=user_name, membership_tier="Premium Member")
    render_welcome_banner(user_name=user_name)

    st.write("---")

    total_items, outfits_count, style_score, requests_pending = get_real_dashboard_stats()
    render_metric_cards(
        total_items=total_items,
        outfits_count=outfits_count,
        style_score=style_score,
        requests_pending=requests_pending
    )

    st.write("---")

    render_recent_outfits()

    st.write("---")

    wardrobe, history = load_wardrobe_and_history()
    render_revival_section(wardrobe, history)

    st.write("---")

    render_wardrobe_stats()

if __name__ == "__main__":
    main()