"""
StyleSync Recent Outfits Component
"""
import os
import json
import streamlit as st

def load_recent_outfits(limit=3):
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    history_path = os.path.join(project_root, "data", "usage_history.json")
    if not os.path.exists(history_path):
        return []
    with open(history_path, "r") as f:
        history = json.load(f)
    used_items = history.get("used_items", [])
    scores = history.get("scores", [])
    outfits = []
    for i in range(0, len(used_items), 3):
        group = used_items[i:i+3]
        if not group:
            continue
        score_index = i // 3
        score = scores[score_index] if score_index < len(scores) else None
        outfits.append({"items": group, "score": score})
    return list(reversed(outfits))[:limit]

def render_recent_outfits():
    st.markdown("""
    <div class="section-title">Recent Outfits</div>
    <div class="section-subtitle">Your latest AI-styled looks.</div>
    """, unsafe_allow_html=True)

    outfits = load_recent_outfits()
    if not outfits:
        st.info("No outfits yet. Visit the Event page to get your first AI-styled look.")
        return

    cols = st.columns(3)
    for idx, outfit in enumerate(outfits):
        with cols[idx % 3]:
            items_text = ", ".join(outfit["items"])
            score = outfit["score"]

            if score is not None:
                if score >= 80:
                    badge = "Great match"
                    badge_color = "#2e7d32"
                    badge_bg = "#e8f5e9"
                elif score >= 60:
                    badge = "Good match"
                    badge_color = "#5c6bc0"
                    badge_bg = "#e8eaf6"
                else:
                    badge = "Casual look"
                    badge_color = "#7986cb"
                    badge_bg = "#e8eaf6"
            else:
                badge = "AI styled"
                badge_color = "#7986cb"
                badge_bg = "#e8eaf6"

            st.markdown(f"""
            <div class="outfit-card">
                <div class="outfit-image-placeholder" style="font-size:2rem;">
                    👔
                </div>
                <div style="margin-bottom:8px;">
                    <span style="background:{badge_bg};color:{badge_color};
                        font-size:0.75rem;font-weight:600;padding:3px 10px;
                        border-radius:999px;border:1px solid {badge_color}30;">
                        {badge}
                    </span>
                </div>
                <div class="outfit-description">{items_text}</div>
            </div>
            """, unsafe_allow_html=True)