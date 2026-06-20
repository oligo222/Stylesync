"""
StyleSync AI Stylist Chat Page

ChatGPT-style conversational interface for style advice and outfit recommendations.
"""
import os
import time
import streamlit as st
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="AI Stylist Chat - StyleSync",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css(css_file_path):
    """
    Loads custom styling CSS.
    """
    if os.path.exists(css_file_path):
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def generate_stylist_response(prompt: str) -> str:
    """
    Generates tailored style-advisor responses based on prompt keywords.
    """
    prompt_lower = prompt.lower()
    
    if "wedding" in prompt_lower or "formal" in prompt_lower or "gala" in prompt_lower:
        return (
            "✨ **AI Stylist Recommendation:**\n\n"
            "Formal occasions are a perfect time to showcase structured silhouettes! "
            "For a modern polished look, I suggest pairing your **White Silk Blouse** with a high-waisted midi skirt, "
            "or going with a tailored double-breasted charcoal suit. "
            "Pair this with minimal gold accessories and sleek leather footwear or classic pumps."
        )
    elif "casual" in prompt_lower or "weekend" in prompt_lower or "jeans" in prompt_lower:
        return (
            "🧶 **AI Stylist Recommendation:**\n\n"
            "For a cozy, elevated casual look, I recommend layering your **Navy Knit Sweater** over a crisp white tee, "
            "paired with relaxed fit light-wash denim. "
            "Complete the look with clean white leather sneakers and a minimal leather crossbody bag."
        )
    elif "outerwear" in prompt_lower or "coat" in prompt_lower or "winter" in prompt_lower:
        return (
            "🧥 **AI Stylist Recommendation:**\n\n"
            "Layering is key for colder weather. Your **Beige Trench Coat** is a timeless piece that works beautifully "
            "over hoodies, sweaters, or shirts. "
            "Try pairing it with slim-fit black trousers and Chelsea boots for a sleek metropolitan look."
        )
    else:
        return (
            "💡 **AI Stylist Suggestion:**\n\n"
            "That's an interesting style idea! To pull that outfit together, "
            "focus on the Rule of Thirds (tucking your top in to define your waistline) "
            "and stick to a harmonious 3-color palette maximum (e.g. Navy, White, and Beige). "
            "Let me know if you'd like suggestions for a specific occasion or item in your closet!"
        )

def main():
    # Setup styling and sidebar
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    load_css(css_path)
    render_sidebar()
    
    # Page Header
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
    
    # Initialize chat message session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am your StyleSync AI Stylist. 🙋‍♂️\n\n"
                    "I can help you build outfits, plan for upcoming events, or decide "
                    "how to style items in your wardrobe. What are we styling today?"
                )
            }
        ]
        
    # Render Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Chat Input Box
    if prompt := st.chat_input("Ask your stylist... (e.g., What should I wear to a winter wedding?)"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display assistant response placeholder
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("*Stylist is thinking...*")
            time.sleep(0.8) # Simulate thinking time
            
            response = generate_stylist_response(prompt)
            message_placeholder.markdown(response)
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
