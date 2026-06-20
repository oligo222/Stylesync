"""
StyleSync Wardrobe Statistics Component

Displays charts and analytics showing user's wardrobe breakdown.
"""
import streamlit as st
import pandas as pd

def render_wardrobe_stats():
    """
    Renders wardrobe distribution statistics in a responsive 2-column layout.
    """
    st.write("### Wardrobe Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### Category Breakdown")
        # Mock categories data
        categories_data = {
            "Category": ["Tops", "Bottoms", "Outerwear", "Shoes", "Accessories"],
            "Count": [45, 32, 18, 15, 32]
        }
        df_cat = pd.DataFrame(categories_data).set_index("Category")
        st.bar_chart(df_cat, color="#4b5563")
        
    with col2:
        st.write("#### Seasonal Style Distribution")
        # Mock seasonal data
        seasonal_data = {
            "Season": ["Spring", "Summer", "Autumn", "Winter"],
            "Items Count": [35, 48, 30, 29]
        }
        df_season = pd.DataFrame(seasonal_data).set_index("Season")
        st.bar_chart(df_season, color="#111827")
