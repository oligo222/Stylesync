"""
StyleSync Dashboard Component

Provides the UI components for the main dashboard dashboard view:
- Welcome Banner
- Metric Cards
"""
import streamlit as st

def render_welcome_banner(user_name: str = "Alex"):
    """
    Renders the modern, clean welcome banner for the user.
    """
    st.markdown(
        f"""
        <div class="welcome-banner">
            <h1 class="welcome-title">Welcome back, {user_name}! ✨</h1>
            <p class="welcome-subtitle">
                Your personal AI stylist has analyzed your wardrobe. Today is a great day to express your style.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_metric_cards(total_items: int = 142, outfits_count: int = 38, style_score: int = 92, requests_pending: int = 2):
    """
    Renders a row of metric cards highlighting wardrobe stats.
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Wardrobe</div>
                <div class="metric-val">{total_items}</div>
                <div class="metric-delta up">▲ +12 this week</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Outfits Created</div>
                <div class="metric-val">{outfits_count}</div>
                <div class="metric-delta up">▲ +5 this week</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Style Match Score</div>
                <div class="metric-val">{style_score}%</div>
                <div class="metric-delta up">▲ +2% trend</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">AI Recommendations</div>
                <div class="metric-val">{requests_pending}</div>
                <div class="metric-delta down">▼ -1 active</div>
            </div>
            """,
            unsafe_allow_html=True
        )
