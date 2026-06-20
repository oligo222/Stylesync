"""
StyleSync Intelligence Page

Wardrobe analytics dashboard including sustainability score, versatility insights,
cost-per-wear tables, and plotly-based category/color/seasonal distributions.
"""
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from components.sidebar import render_sidebar

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
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Sustainability Score</div>
                <div class="metric-val" style="color: #10b981;">78 / 100</div>
                <div class="metric-delta up" style="color: #10b981;">🌿 Good • Top 15% of Stylers</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Average Cost per Wear</div>
                <div class="metric-val">$2.45</div>
                <div class="metric-delta up" style="color: #10b981;">▼ -$0.12 this month</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Wardrobe Utilization</div>
                <div class="metric-val">84%</div>
                <div class="metric-delta up" style="color: #10b981;">▲ +4% active items</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.write("---")
    
    # Row 2: Plotly Distribution Charts (Category & Color)
    col_cat, col_color = st.columns(2)
    
    with col_cat:
        st.write("### Category Distribution")
        
        cat_data = pd.DataFrame({
            "Category": ["Tops", "Bottoms", "Outerwear", "Shoes", "Accessories"],
            "Count": [45, 32, 18, 15, 32]
        })
        
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
        
        color_data = pd.DataFrame({
            "Color": ["Black", "Navy", "White", "Beige", "Grey", "Olive"],
            "Items Count": [38, 28, 25, 20, 16, 15]
        })
        
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
    
    # Row 3: Seasonal Chart & Cost per Wear
    col_season, col_cost = st.columns(2)
    
    with col_season:
        st.write("### Seasonal Distribution")
        
        season_data = pd.DataFrame({
            "Season": ["Spring", "Summer", "Autumn", "Winter"],
            "Items": [35, 48, 30, 29]
        })
        
        # Stacked / Clean vertical Bar Chart
        fig_season = px.bar(
            season_data,
            x="Season",
            y="Items",
            color_discrete_sequence=["#111827"]
        )
        fig_season.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#e5e7eb")
        )
        st.plotly_chart(fig_season, use_container_width=True)
        
    with col_cost:
        st.write("### Cost Per Wear Leaderboard")
        
        # Cost per wear calculation dataframe
        cost_df = pd.DataFrame({
            "Garment Item": [
                "🧥 Beige Trench Coat",
                "👖 Classic Blue Jeans",
                "👟 White Leather Sneakers",
                "👜 Black Leather Tote",
                "👚 White Silk Blouse"
            ],
            "Retail Cost": ["$180.00", "$90.00", "$120.00", "$210.00", "$110.00"],
            "Times Worn": [62, 54, 78, 48, 22],
            "Cost Per Wear": ["$2.90", "$1.67", "$1.54", "$4.38", "$5.00"]
        })
        
        st.dataframe(cost_df, use_container_width=True, hide_index=True)
        
    st.write("---")
    
    # Row 4: Versatility Analysis
    col_versatile, col_unworn = st.columns(2)
    
    with col_versatile:
        st.write("### Most Versatile Items")
        st.markdown(
            """
            *   **Beige Trench Coat**: Combines with **32** distinct outfits.
            *   **Classic Blue Jeans**: Combines with **28** distinct outfits.
            *   **White Silk Blouse**: Combines with **24** distinct outfits.
            *   **White Leather Sneakers**: Fits both semi-formal and casual styling.
            """
        )
        
    with col_unworn:
        st.write("### Least Used Items (Opportunities to Style)")
        st.markdown(
            """
            *   **Neon Green Raincoat**: Worn **0** times (last 90 days).
            *   **Red Velvet Bowtie**: Worn **1** time (last 180 days).
            *   **Yellow Suede Loafers**: Worn **2** times (last 180 days).
            *   **Plaid Wool Scarf**: Unworn since last season.
            """
        )

if __name__ == "__main__":
    main()
