"""
StyleSync Dashboard Component - Redesigned
Clean white cards, soft gradient hero, no emojis in headings
"""
import streamlit as st

def render_welcome_banner(user_name: str = "Alex"):
    st.markdown(f"""
    <div style="
        background: #ffffff;
        border-radius: 16px;
        padding: 40px 40px 36px;
        margin-bottom: 8px;
        border: 1.5px solid #d0d5e8;
        box-shadow: 0 2px 12px rgba(121,134,203,0.12);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute; top: -60px; right: -60px;
            width: 250px; height: 250px; border-radius: 50%;
            background: radial-gradient(circle, rgba(149,117,205,0.12) 0%, transparent 70%);
        "></div>
        <div style="
            position: absolute; bottom: -40px; right: 100px;
            width: 180px; height: 180px; border-radius: 50%;
            background: radial-gradient(circle, rgba(121,134,203,0.1) 0%, transparent 70%);
        "></div>
        <div style="position: relative; z-index: 1;">
            <div style="font-size:0.68rem;font-weight:600;letter-spacing:3px;
                text-transform:uppercase;color:#7986cb;margin-bottom:10px;">
                StyleSync AI
            </div>
            <div style="font-family:'Inter',sans-serif;font-size:2rem;font-weight:800;
                color:#0a0a0a;letter-spacing:-0.5px;line-height:1.2;margin-bottom:10px;">
                Welcome back, {user_name}
            </div>
            <div style="color:#4a4a5a;font-size:0.95rem;max-width:520px;line-height:1.6;">
                Your personal AI stylist has analyzed your wardrobe.
                Today is a great day to express your style.
            </div>
            <div style="display:flex;gap:10px;margin-top:20px;flex-wrap:wrap;">
                <span style="background:#f3f4fd;border:1.5px solid #c5cae9;
                    border-radius:999px;padding:5px 16px;font-size:0.8rem;
                    font-weight:600;color:#5c6bc0;">AI Stylist Active</span>
                <span style="background:#f3f4fd;border:1.5px solid #c5cae9;
                    border-radius:999px;padding:5px 16px;font-size:0.8rem;
                    font-weight:600;color:#5c6bc0;">Wardrobe Synced</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_cards(total_items=0, outfits_count=0, style_score=0, requests_pending=0):
    col1, col2, col3, col4 = st.columns(4)
    cards = [
        (col1, "Total Wardrobe", total_items, "+12 this week", "up"),
        (col2, "Outfits Created", outfits_count, "+5 this week", "up"),
        (col3, "Style Match Score", f"{style_score}%", "+2% trend", "up"),
        (col4, "AI Recommendations", requests_pending, "-1 active", "down"),
    ]
    for col, label, val, delta, delta_type in cards:
        delta_color = "#2e7d32" if delta_type == "up" else "#b71c1c"
        delta_arrow = "▲" if delta_type == "up" else "▼"
        with col:
            st.markdown(f"""
            <div style="
                background: #ffffff;
                border: 1.5px solid #d0d5e8;
                border-radius: 12px;
                padding: 20px 22px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            ">
                <div style="font-size:0.65rem;font-weight:600;letter-spacing:2px;
                    text-transform:uppercase;color:#7986cb;margin-bottom:8px;">{label}</div>
                <div style="font-family:'Inter',sans-serif;font-size:2rem;font-weight:800;
                    color:#0a0a0a;line-height:1.1;margin-bottom:6px;">{val}</div>
                <div style="font-size:0.78rem;font-weight:500;color:{delta_color};">
                    {delta_arrow} {delta}
                </div>
            </div>
            """, unsafe_allow_html=True)