"""
StyleSync Intelligence Page

Wardrobe analytics dashboard including sustainability score, versatility insights,
cost-per-wear tables, and plotly-based category/color/seasonal distributions.
"""
import os
import sys
import json
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

def load_css(css_file_path):
    """
    Loads custom styling CSS.
    """
    if os.path.exists(css_file_path):
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_real_wardrobe_data():
    """
    Loads real wardrobe + usage data for the intelligence page, with safe
    fallbacks if files are missing or empty.
    """
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
    # Setup styling and sidebar
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    load_css(css_path)
    render_sidebar()
    
    # Page Header
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="font-weight: 700; margin-bottom: 4px;">📈 Style Intelligence</h1>
            <p style="color: #6b7280; font-size: 1.1rem; margin: 0;">
                Detailed analytics, usage frequencies, sustainability scores, and wardrobe insights.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.write("---")
    
    # Row 1: High Level Metrics
    items, used_items = get_real_wardrobe_data()
    num_outfits = max(1, len(used_items) // 3)
    sustainability = sustainability_insight(num_outfits)

    total_items = len(items)
    unique_used = len(set(used_items))
    utilization_pct = round((unique_used / total_items) * 100) if total_items > 0 else 0

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Sustainability Insight</div>
                <div class="metric-val" style="color: #10b981; font-size: 1.1rem;">{sustainability['message']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Wardrobe Utilization</div>
                <div class="metric-val">{utilization_pct}%</div>
                <div class="metric-delta up" style="color: #10b981;">{unique_used} of {total_items} items used</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.write("---")
    
    # Row 2: Plotly Distribution Charts (Category & Color)
    col_cat, col_color = st.columns(2)
    
    with col_cat:
        st.write("### Category Distribution")
        
        category_counts = {}
        for item in items:
            cat = item.get("category", "Unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        cat_data = pd.DataFrame({
            "Category": list(category_counts.keys()),
            "Count": list(category_counts.values())
        }) if category_counts else pd.DataFrame({"Category": ["No data yet"], "Count": [1]})
        
        # Donut Chart with clean palette
        fig_cat = px.pie(
            cat_data, 
            values="Count", 
            names="Category", 
            hole=0.5,
            color_discrete_sequence=["#111827", "#374151", "#4b5563", "#9ca3af", "#e5e7eb"]
        )
        fig_cat.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with col_color:
        st.write("### Dominant Wardrobe Colors")
        
        color_counts = {}
        for item in items:
            color = item.get("color", "Unknown")
            color_counts[color] = color_counts.get(color, 0) + 1

        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:6]

        color_data = pd.DataFrame({
            "Color": [c[0] for c in sorted_colors],
            "Items Count": [c[1] for c in sorted_colors]
        }) if sorted_colors else pd.DataFrame({"Color": ["No data yet"], "Items Count": [1]})
        
        # Horizontal Bar Chart
        fig_color = px.bar(
            color_data,
            x="Items Count",
            y="Color",
            orientation="h",
            color_discrete_sequence=["#374151"]
        )
        fig_color.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="#e5e7eb"),
            yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig_color, use_container_width=True)
        
    st.write("---")
    
  # Row 3: Versatility & Usage Analysis
    col_versatile, col_unworn = st.columns(2)

    with col_versatile:
        st.write("### Most Versatile Item")

        versatile = most_versatile_item(items)
        if versatile.get("item"):
            st.markdown(f"*   **{versatile['item']}**: Combines with **{versatile['combination_count']}** distinct outfits.")
        else:
            st.markdown("*   *No versatility metrics calculated yet.*")

    with col_unworn:
        st.write("### Forgotten Gems (Opportunities to Style)")

        gems = forgotten_gems(items, used_items)
        if gems:
            for gem in gems:
                st.markdown(f"*   **{gem}**: Not used in your recent recommendations.")
        else:
            st.markdown("*   *Your wardrobe is fully utilized! No forgotten items found.*")

if __name__ == "__main__":
    main()
