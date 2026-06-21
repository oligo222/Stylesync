"""
StyleSync Recommendations Page

Displays the most recent real AI-generated outfit recommendations,
pulled from output/recommendations.json (produced by the actual
recommendation pipeline via the Event page).
"""
import os
import json
import streamlit as st
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="AI Recommendations - StyleSync",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css(css_file_path):
    if os.path.exists(css_file_path):
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_latest_recommendations():
    """Loads the most recent pipeline output from output/recommendations.json."""
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "output", "recommendations.json"
    )
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            return json.load(f)
    return None

def main():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    load_css(css_path)
    render_sidebar()

    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="font-weight: 700; margin-bottom: 4px;">✨ AI Outfit Recommendations</h1>
            <p style="color: #6b7280; font-size: 1.1rem; margin: 0;">
                Your most recent AI-generated recommendations, based on your real wardrobe.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("---")

    data = load_latest_recommendations()

    if not data or not data.get("recommendations"):
        st.info(
            "No recommendations yet. Head to the **Event** page, describe an upcoming "
            "event, and generate outfit suggestions — they'll show up here."
        )
        return

    event_info = data.get("event_analysis", {})
    recommendations = data.get("recommendations", [])

    st.markdown(f"#### For: *{event_info.get('occasion_type', 'Your Event')}* ({event_info.get('event_style', '')})")
    if event_info.get("reasoning"):
        st.caption(event_info["reasoning"])

    st.write("")

    for i, outfit in enumerate(recommendations):
        with st.container():
            col_visual, col_details = st.columns([1, 2], gap="large")

            with col_visual:
                st.markdown(
                    f"""
                    <div style="
                        border: 1px solid #e5e7eb;
                        border-radius: 16px;
                        background: #ffffff;
                        padding: 32px;
                        text-align: center;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                    ">
                        <div style="font-size: 4rem;">👕</div>
                        <h4 style="font-weight: 600; color: #111827; margin-top: 8px;">Outfit {i+1}</h4>
                        <span style="
                            font-size: 1.2rem;
                            font-weight: 700;
                            color: #10b981;
                            background-color: #ecfdf5;
                            padding: 4px 14px;
                            border-radius: 8px;
                        ">
                            {outfit.get('suitability_score', '?')}/100
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col_details:
                st.markdown("**Items:**")
                if outfit.get("top"):
                    st.markdown(f"- 👕 Top: {outfit['top']}")
                if outfit.get("bottom"):
                    st.markdown(f"- 👖 Bottom: {outfit['bottom']}")
                if outfit.get("footwear"):
                    st.markdown(f"- 👞 Footwear: {outfit['footwear']}")

                st.markdown("**Stylist Note:**")
                st.info(outfit.get("explanation", "No explanation available."))

        st.write("---")

if __name__ == "__main__":
    main()