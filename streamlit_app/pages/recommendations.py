"""
StyleSync Recommendations Page

Displays AI-generated outfit recommendations, match scores, explanations,
and action buttons for saving or regenerating looks.
"""
import os
import random
import streamlit as st
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="AI Recommendations - StyleSync",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Mock recommendation data
RECOMMENDATIONS_POOL = [
    {
        "name": "Classic Metropolitan Layering",
        "items": [
            "🧥 Beige Trench Coat (Outerwear)",
            "🧶 Navy Knit Sweater (Tops)",
            "👖 Dark Slim Chinos (Bottoms)",
            "👞 Leather Chelsea Boots (Shoes)"
        ],
        "score": 94,
        "explanation": "This look balances length and color weight. The long line of the Beige Trench Coat provides structured elegance, while the deep Navy Knit sweater brings texture. Light-brown Chelsea boots pull the earthy shades together for an effortless smart-casual vibe.",
        "emoji": "🧥"
    },
    {
        "name": "Effortless Chic Evening",
        "items": [
            "👚 White Silk Blouse (Tops)",
            "👗 Charcoal High-Waisted Skirt (Bottoms)",
            "👠 Black Suede Heels (Shoes)",
            "👜 Minimal Leather Clutch (Accessories)"
        ],
        "score": 89,
        "explanation": "A clean, high-contrast look suitable for dinner dates or evening events. The soft drape of the White Silk Blouse creates an upscale feel, contrasted cleanly by the structured dark skirt. Classic black heels anchor the ensemble.",
        "emoji": "👗"
    },
    {
        "name": "Smart Casual Blazer Look",
        "items": [
            "🧥 Tailored Navy Blazer (Outerwear)",
            "👕 White Crewneck Tee (Tops)",
            "👖 Charcoal Slim Trousers (Bottoms)",
            "👞 White Leather Sneakers (Shoes)"
        ],
        "score": 92,
        "explanation": "A timeless workplace combination. The navy blazer lends instant structure and professionalism, while the clean crewneck tee keeps it fresh. White sneakers soften the look to be accessible and modern.",
        "emoji": "💼"
    },
    {
        "name": "Relaxed Urban Streetwear",
        "items": [
            "🧥 Olive Bomber Jacket (Outerwear)",
            "👕 Black Graphic Tee (Tops)",
            "👖 Olive Cargo Pants (Bottoms)",
            "👟 Retro Runner Sneakers (Shoes)"
        ],
        "score": 87,
        "explanation": "Perfect for off-duty weekend errands. This look embraces tonal olive greens and practical street style. High-contrast white/black details keep the visual fields defined.",
        "emoji": "👟"
    }
]

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
            <h1 style="font-weight: 700; margin-bottom: 4px;">✨ AI Outfit Recommendations</h1>
            <p style="color: #6b7280; font-size: 1.1rem; margin: 0;">
                Personalized style recommendations crafted from your wardrobe database.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.write("---")
    
    # Initialize active recommendation in session state
    if "current_rec" not in st.session_state:
        st.session_state.current_rec = RECOMMENDATIONS_POOL[0]
        
    rec = st.session_state.current_rec
    
    # Layout splits: Visual mockup card (left) and styled details card (right)
    col_visual, col_details = st.columns([1, 1], gap="large")
    
    with col_visual:
        st.write("### Outfit Visual Layout")
        st.markdown(
            f"""
            <div style="
                border: 1px solid #e5e7eb; 
                border-radius: 16px; 
                background: #ffffff; 
                padding: 40px; 
                text-align: center;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                margin-top: 10px;
            ">
                <div style="font-size: 8rem; line-height: 1.2;">{rec['emoji']}</div>
                <h3 style="font-weight: 600; color: #111827; margin-top: 16px; margin-bottom: 4px;">{rec['name']}</h3>
                <span style="
                    font-size: 0.85rem; 
                    font-weight: 600; 
                    color: #4b5563; 
                    background-color: #f3f4f6; 
                    padding: 6px 12px; 
                    border-radius: 9999px;
                ">
                    AI Suggested Combination
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_details:
        st.write("### Recommendation Details")
        
        # Match Score Badge
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px; margin-top: 10px;">
                <span style="font-size: 1.1rem; font-weight: 600; color: #4b5563;">Stylist Match Score:</span>
                <span style="
                    font-size: 1.5rem; 
                    font-weight: 700; 
                    color: #10b981; 
                    background-color: #ecfdf5; 
                    border: 1px solid #10b981; 
                    padding: 4px 16px; 
                    border-radius: 8px;
                ">
                    {rec['score']}% Match
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Clothing Items List
        st.markdown("#### Included Clothing Items:")
        for item in rec["items"]:
            st.markdown(f"- {item}")
            
        st.write("")
        
        # Styling Explanation
        st.markdown("#### Stylist Note:")
        st.info(rec["explanation"])
        
    st.write("---")
    
    # Action buttons row
    col_btn_left, col_btn_right = st.columns(2)
    
    with col_btn_left:
        if st.button("💾 Save Outfit to Collection", use_container_width=True):
            st.success(f"Successfully saved '**{rec['name']}**' to your outfits history!")
            
    with col_btn_right:
        if st.button("🔄 Generate Another Recommendation", use_container_width=True):
            # Select a random recommendation from the pool (different from the current one)
            remaining_pool = [r for r in RECOMMENDATIONS_POOL if r["name"] != rec["name"]]
            st.session_state.current_rec = random.choice(remaining_pool)
            # Force refresh page to display new recommendation
            st.rerun()

if __name__ == "__main__":
    main()
