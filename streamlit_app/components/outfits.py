"""
StyleSync Recent Outfits Component

Displays the grid of recent outfits, pulled from real usage history.
"""
import os
import json
import streamlit as st

def load_recent_outfits(limit=3):
    """
    Builds a simple 'recent outfits' view from real usage_history.json data.
    Since history only stores used item names (not full outfit groupings),
    this shows the most recently used items in groups of 3.
    """
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
        if len(group) < 1:
            continue
        score_index = i // 3
        score = scores[score_index] if score_index < len(scores) else None
        outfits.append({
            "items": group,
            "score": score
        })

    return list(reversed(outfits))[:limit]

def render_recent_outfits():
    """
    Renders a responsive 3-column layout showing the user's recent outfits,
    based on real usage history.
    """
    st.write("### Recent Outfits")

    outfits = load_recent_outfits()

    if not outfits:
        st.info("No outfits generated yet. Visit the **Event** page to get your first AI-styled outfit recommendation.")
        return

    cols = st.columns(3)

    for idx, outfit in enumerate(outfits):
        with cols[idx % 3]:
            items_text = ", ".join(outfit["items"])
            score_text = f"{outfit['score']}/100 match" if outfit["score"] is not None else "Recently styled"

            st.markdown(
                f"""
                <div class="outfit-card">
                    <div class="outfit-image-placeholder">
                        👔
                    </div>
                    <div class="outfit-details">
                        <h4 class="outfit-name">{score_text}</h4>
                        <p class="outfit-description">{items_text}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )