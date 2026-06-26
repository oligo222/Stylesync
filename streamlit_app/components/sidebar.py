"""
StyleSync Sidebar Component
"""
import streamlit as st

def render_sidebar(user_name: str = "Alex", membership_tier: str = "Premium Member"):
    with st.sidebar:
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        @media (prefers-color-scheme: dark) {
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #e8eaf6 0%, #ede7f6 100%) !important;
            }
            [data-testid="stSidebar"] * { color: #0a0a0a !important; }
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;margin-bottom:24px;padding-top:8px;">
            <div style="font-family:'Inter',sans-serif;font-size:1.5rem;font-weight:800;
                color:#0a0a0a;letter-spacing:-0.5px;">StyleSync</div>
            <div style="font-size:0.65rem;font-weight:600;letter-spacing:3px;
                text-transform:uppercase;color:#7986cb;margin-top:2px;">AI Fashion Stylist</div>
        </div>
        """, unsafe_allow_html=True)

        first_initial = user_name[0].upper() if user_name else "U"
        st.markdown(f"""
        <div style="background:#ffffff;border:1.5px solid #d0d5e8;border-radius:12px;
            padding:18px;text-align:center;margin-bottom:16px;
            box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="width:48px;height:48px;background:linear-gradient(135deg,#c5cae9,#9fa8da);
                border-radius:50%;display:flex;align-items:center;justify-content:center;
                font-family:'Inter',sans-serif;font-size:1.2rem;font-weight:700;
                color:#0a0a0a;margin:0 auto 10px;border:1.5px solid #9fa8da;">
                {first_initial}
            </div>
            <div style="font-family:'Inter',sans-serif;font-size:1rem;font-weight:700;
                color:#0a0a0a;margin:0 0 4px;">{user_name}</div>
            <div style="font-size:0.72rem;font-weight:600;letter-spacing:2px;
                text-transform:uppercase;color:#7986cb;">{membership_tier}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#ffffff;border:1.5px solid #d0d5e8;border-radius:10px;
            padding:14px 16px;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="font-size:0.65rem;font-weight:600;letter-spacing:2px;
                text-transform:uppercase;color:#7986cb;margin-bottom:6px;">
                Style Tip of the Day
            </div>
            <div style="font-size:0.82rem;color:#0a0a0a;line-height:1.6;">
                Embrace neutral tones this week. Sand, beige, and slate grey form
                a versatile foundation for any smart-casual look.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border:none;border-top:1px solid #d0d5e8;margin:8px 0 12px;'>",
                    unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size:0.8rem;color:#4a4a5a;line-height:1.9;">
            <div><span style="color:#7986cb;font-weight:600;">AI Engine</span>
                <span style="float:right;color:#2e7d32;font-weight:600;">Active</span></div>
            <div><span style="color:#7986cb;font-weight:600;">Wardrobe DB</span>
                <span style="float:right;color:#0a0a0a;">Local</span></div>
            <div><span style="color:#7986cb;font-weight:600;">Version</span>
                <span style="float:right;color:#0a0a0a;">1.0.0</span></div>
        </div>
        """, unsafe_allow_html=True)