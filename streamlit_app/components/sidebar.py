"""
StyleSync Sidebar Component

Renders sidebar branding, user profile card, and quick styling tips.
"""
import streamlit as st

import os
import sys

def render_sidebar(user_name: str = "Alex", membership_tier: str = "Premium Member"):
    """
    Renders the sidebar navigation branding, profile card, and status widget.
    """
    # Check if user is logged in
    user = st.session_state.get("user")
    if user:
        user_name = user.get("name", user_name)
        membership_tier = user.get("membership_tier", membership_tier)

    with st.sidebar:
        # App logo / title
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 24px;">
                <h1 style="font-size: 1.8rem; font-weight: 700; color: #111827; margin: 0;">StyleSync ✨</h1>
                <span style="font-size: 0.8rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.1em;">AI Fashion Stylist</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Profile Card
        first_initial = user_name[0].upper() if user_name else "U"
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-avatar">{first_initial}</div>
                <h3 class="profile-name">{user_name}</h3>
                <p class="profile-role">{membership_tier}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Style Tip of the Day Container
        st.info(
            "💡 **Style Tip of the Day**\n\n"
            "Embrace neutral tones this week. Sand, beige, and slate grey form a versatile foundation for any smart-casual look."
        )
        
        st.divider()

        # Add Logout button in sidebar if logged in
        if st.session_state.get("logged_in"):
            # Ensure path is set for imports
            PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if PROJECT_ROOT not in sys.path:
                sys.path.append(PROJECT_ROOT)
            from authentication.auth_utils import logout

            if st.button("🚪 Log Out", key="sidebar_logout_btn", use_container_width=True):
                logout()
            st.divider()
        
        # Status Card
        st.markdown(
            """
            <div style="font-size: 0.85rem; color: #6b7280; display: flex; flex-direction: column; gap: 4px;">
                <div><b>AI Engine:</b> Active & Synced</div>
                <div><b>Wardrobe Database:</b> Local</div>
                <div><b>Version:</b> 1.0.0</div>
            </div>
            """,
            unsafe_allow_html=True
        )
