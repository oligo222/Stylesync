"""
StyleSync AI Stylist Chat Page

Real conversational interface powered by Gemini, aware of the user's
actual wardrobe items.
"""
import os
import sys
import json
import streamlit as st
from components.sidebar import render_sidebar

# Allow importing from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from wardrobe_adapter import client

st.set_page_config(
    page_title="AI Stylist Chat - StyleSync",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css(css_file_path):
    if os.path.exists(css_file_path):
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_wardrobe_summary():
    """Loads the real wardrobe and builds a short text summary for the prompt."""
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
    """Calls Gemini with real wardrobe context and conversation history."""
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
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    load_css(css_path)
    render_sidebar()

    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="font-weight: 700; margin-bottom: 4px;">💬 AI Stylist Consultation</h1>
            <p style="color: #6b7280; font-size: 1.1rem; margin: 0;">
                Ask questions, describe outfits, or get help styling your closet.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("---")

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