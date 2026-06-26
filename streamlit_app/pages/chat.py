"""
StyleSync AI Stylist Chat Page
"""
import os
import sys
import json
import streamlit as st
from components.sidebar import render_sidebar

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from wardrobe_adapter import client

st.set_page_config(
    page_title="AI Stylist Chat - StyleSync",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_wardrobe_summary():
    wardrobe_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "wardrobe.json"
    )
    if not os.path.exists(wardrobe_path):
        return "The user hasn't uploaded any wardrobe items yet."
    with open(wardrobe_path, "r") as f:
        items = json.load(f)
    if not items:
        return "The user hasn't uploaded any wardrobe items yet."
    lines = []
    for item in items:
        color = item.get("color", "")
        garment = item.get("garment_type") or item.get("category", "item")
        style = item.get("style", "")
        lines.append(f"- {color} {garment} ({style})")
    return "The user's actual wardrobe contains:\n" + "\n".join(lines)

def generate_stylist_response(prompt, chat_history, wardrobe_summary):
    system_context = f"""You are a friendly, knowledgeable AI fashion stylist for the StyleSync app.

{wardrobe_summary}

Give specific, practical styling advice. When relevant, reference actual items from
the user's wardrobe listed above by name, rather than generic suggestions. Keep
responses conversational and concise (2-4 sentences usually, more if genuinely needed).
"""
    history_text = ""
    for msg in chat_history[-6:]:
        role = "User" if msg["role"] == "user" else "Stylist"
        history_text += f"{role}: {msg['content']}\n"

    full_prompt = f"{system_context}\n\nConversation so far:\n{history_text}\nUser: {prompt}\n\nStylist:"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"Sorry, I couldn't process that right now. (Error: {e})"

def main():
    render_sidebar()

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #eef0f7 !important;
        color: #0a0a0a !important;
    }
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stMainBlockContainer"],
    .main, section.main > div, .block-container {
        background-color: #eef0f7 !important;
    }
    @media (prefers-color-scheme: dark) {
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"],
        [data-testid="stVerticalBlock"],
        [data-testid="stMainBlockContainer"],
        .main, section.main > div, .block-container {
            background-color: #eef0f7 !important;
            color: #0a0a0a !important;
        }
        p, span, div, label, li { color: #0a0a0a !important; }
    }
    .main .block-container { background: #eef0f7 !important; }

    .page-label {
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #7986cb;
        margin-bottom: 6px;
    }
    .page-title {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #0a0a0a;
        letter-spacing: -0.5px;
        line-height: 1.2;
        margin-bottom: 6px;
    }
    .page-subtitle {
        font-size: 0.95rem;
        color: #4a4a5a;
        margin-bottom: 24px;
    }
    [data-testid="stChatMessage"] {
        background: #ffffff !important;
        border: 1.5px solid #d0d5e8 !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
    }
    </style>

    <div class="page-label">StyleSync AI</div>
    <div class="page-title">Your Personal Stylist.</div>
    <div class="page-subtitle">Ask anything about your wardrobe — I know exactly what you own.</div>
    <hr style="border:none;border-top:1px solid #d0d5e8;margin:8px 0 24px 0;">
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I'm your StyleSync AI Stylist. 🙋‍♂️\n\n"
                    "I can see your real wardrobe and help you build outfits, plan for "
                    "upcoming events, or decide how to style items you already own. "
                    "What are we styling today?"
                )
            }
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask your stylist... (e.g., What should I wear to a winter wedding?)"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("*Stylist is thinking...*")
            wardrobe_summary = load_wardrobe_summary()
            response = generate_stylist_response(prompt, st.session_state.messages, wardrobe_summary)
            message_placeholder.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()