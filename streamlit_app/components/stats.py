"""
StyleSync Wardrobe Statistics Component
"""
import streamlit as st
import pandas as pd

def render_wardrobe_stats():
    st.markdown("""
    <div style="margin-bottom:20px;">
        <div style="font-size:0.68rem;font-weight:600;letter-spacing:3px;
            text-transform:uppercase;color:#7986cb;margin-bottom:4px;">Analytics</div>
        <div style="font-family:'Inter',sans-serif;font-size:1.4rem;font-weight:700;
            color:#0a0a0a;">Wardrobe Insights</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background:#ffffff;border:1.5px solid #d0d5e8;border-radius:12px;
            padding:20px 22px;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="font-size:0.68rem;font-weight:600;letter-spacing:2px;
                text-transform:uppercase;color:#7986cb;margin-bottom:4px;">Category</div>
            <div style="font-weight:700;color:#0a0a0a;margin-bottom:16px;">Breakdown</div>
        """, unsafe_allow_html=True)
        df_cat = pd.DataFrame({
            "Category": ["Tops", "Bottoms", "Outerwear", "Shoes", "Accessories"],
            "Count": [45, 32, 18, 15, 32]
        }).set_index("Category")
        st.bar_chart(df_cat, color="#7986cb")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:#ffffff;border:1.5px solid #d0d5e8;border-radius:12px;
            padding:20px 22px;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="font-size:0.68rem;font-weight:600;letter-spacing:2px;
                text-transform:uppercase;color:#7986cb;margin-bottom:4px;">Seasonal</div>
            <div style="font-weight:700;color:#0a0a0a;margin-bottom:16px;">Style Distribution</div>
        """, unsafe_allow_html=True)
        df_season = pd.DataFrame({
            "Season": ["Spring", "Summer", "Autumn", "Winter"],
            "Items Count": [35, 48, 30, 29]
        }).set_index("Season")
        st.bar_chart(df_season, color="#9575cd")
        st.markdown("</div>", unsafe_allow_html=True)