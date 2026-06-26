"""
StyleSync Intelligence Page
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
from components.sidebar import render_sidebar

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from wardrobe_adapter import load_and_adapt
from insights_engine import most_versatile_item, sustainability_insight, forgotten_gems, load_usage_history

st.set_page_config(
    page_title="Style Intelligence - StyleSync",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

def get_real_wardrobe_data():
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    try:
        wardrobe_path = os.path.join(project_root, "wardrobe.json")
        items = load_and_adapt(wardrobe_path).get("items", [])
    except Exception:
        items = []
    try:
        history_path = os.path.join(project_root, "data", "usage_history.json")
        used_items = load_usage_history(history_path)
    except Exception:
        used_items = []
    return items, used_items

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
    .stat-card {
        background: #ffffff;
        border: 1.5px solid #d0d5e8;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 0 14px rgba(129,199,132,0.2);
    }
    .stat-label {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #7986cb;
        margin-bottom: 6px;
    }
    .stat-value {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #0a0a0a;
        line-height: 1.3;
    }
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #0a0a0a;
        margin-bottom: 12px;
        letter-spacing: -0.3px;
    }
    .insight-row {
        font-size: 0.92rem;
        font-weight: 500;
        color: #0a0a0a;
        padding: 8px 0;
        border-bottom: 1px solid #eef0f7;
    }
    </style>

    <div class="page-label">StyleSync AI</div>
    <div class="page-title">Wardrobe Intelligence.</div>
    <div class="page-subtitle">Analytics, sustainability scores, and insights from your closet.</div>
    <hr style="border:none;border-top:1px solid #d0d5e8;margin:8px 0 24px 0;">
    """, unsafe_allow_html=True)

    items, used_items = get_real_wardrobe_data()
    num_outfits = max(1, len(used_items) // 3)
    sustainability = sustainability_insight(num_outfits)
    total_items = len(items)
    unique_used = len(set(used_items))
    utilization_pct = round((unique_used / total_items) * 100) if total_items > 0 else 0

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Sustainability Insight</div>
            <div class="stat-value" style="font-size:0.95rem;font-weight:500;">{sustainability['message']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Wardrobe Utilization</div>
            <div class="stat-value">{utilization_pct}%</div>
            <div style="font-size:0.82rem;color:#4a4a5a;margin-top:4px;">{unique_used} of {total_items} items used</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr style="border:none;border-top:1px solid #d0d5e8;margin:8px 0 24px 0;">', unsafe_allow_html=True)

    col_cat, col_color = st.columns(2)

    with col_cat:
        st.markdown('<div class="section-title">Category Distribution</div>', unsafe_allow_html=True)
        category_counts = {}
        for item in items:
            cat = item.get("category", "Unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1
        cat_data = pd.DataFrame({
            "Category": list(category_counts.keys()),
            "Count": list(category_counts.values())
        }) if category_counts else pd.DataFrame({"Category": ["No data yet"], "Count": [1]})

        fig_cat = px.pie(
            cat_data, values="Count", names="Category", hole=0.5,
            color_discrete_sequence=["#c5cae9", "#b2dfdb", "#f8bbd9", "#fff9c4", "#b3e5fc"]
        )
        fig_cat.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#0a0a0a"),
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_color:
        st.markdown('<div class="section-title">Dominant Wardrobe Colors</div>', unsafe_allow_html=True)
        color_counts = {}
        for item in items:
            color = item.get("color", "Unknown")
            color_counts[color] = color_counts.get(color, 0) + 1
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:6]
        color_data = pd.DataFrame({
            "Color": [c[0] for c in sorted_colors],
            "Items Count": [c[1] for c in sorted_colors]
        }) if sorted_colors else pd.DataFrame({"Color": ["No data yet"], "Items Count": [1]})

        fig_color = px.bar(
            color_data, x="Items Count", y="Color", orientation="h",
            color_discrete_sequence=["#9fa8da"]
        )
        fig_color.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#0a0a0a"),
            xaxis=dict(gridcolor="#e8eaf6"),
            yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig_color, use_container_width=True)

    st.markdown('<hr style="border:none;border-top:1px solid #d0d5e8;margin:8px 0 24px 0;">', unsafe_allow_html=True)

    col_versatile, col_unworn = st.columns(2)

    with col_versatile:
        st.markdown('<div class="section-title">Most Versatile Item</div>', unsafe_allow_html=True)
        versatile = most_versatile_item(items)
        if versatile.get("item"):
            st.markdown(f'<div class="insight-row">✨ <strong>{versatile["item"]}</strong> — combines with <strong>{versatile["combination_count"]}</strong> distinct outfits.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="insight-row">No versatility metrics calculated yet.</div>', unsafe_allow_html=True)

    with col_unworn:
        st.markdown('<div class="section-title">Forgotten Gems</div>', unsafe_allow_html=True)
        gems = forgotten_gems(items, used_items)
        if gems:
            for gem in gems:
                st.markdown(f'<div class="insight-row">💎 <strong>{gem}</strong> — not used in recent recommendations.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="insight-row">Your wardrobe is fully utilized!</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()