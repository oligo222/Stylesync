"""
StyleSync Login Page Controller

Renders the login UI and processes user credentials.
"""
import streamlit as st
import os
import sys

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.users import get_user_by_email
from authentication.auth_utils import verify_password, login_user, validate_email

def render_login_page():
    # Guard: if already logged in, redirect immediately
    if st.session_state.get("logged_in"):
        st.switch_page("pages/profile.py")
        st.stop()

    # Load custom branding CSS
    css_path = os.path.join(PROJECT_ROOT, "streamlit_app", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Injected styles specifically for the premium auth cards
    st.markdown(
        """
        <style>
        .auth-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem 0;
        }
        .auth-logo {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
            background: linear-gradient(135deg, #111827 0%, #4b5563 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
        }
        .auth-sub {
            color: #6b7280;
            font-size: 0.95rem;
            margin-bottom: 2rem;
            text-align: center;
        }
        div[data-testid="stForm"] {
            border: 1px solid #e5e7eb !important;
            border-radius: 16px !important;
            padding: 2.5rem !important;
            background-color: #ffffff !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02) !important;
        }
        .stButton>button {
            background: linear-gradient(90deg, #111827 0%, #374151 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.6rem 1.5rem !important;
            transition: all 0.2s ease-in-out !important;
        }
        .stButton>button:hover {
            opacity: 0.9 !important;
            transform: translateY(-1px) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="auth-container">
            <div class="auth-logo">StyleSync ✨</div>
            <div class="auth-sub">AI-Powered Wardrobe & Style Planner</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Centered card layout
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        st.write("### Welcome Back")
        st.caption("Please log in to your account to continue styling.")

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email Address", placeholder="e.g. alex@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_btn = st.form_submit_button("Sign In", use_container_width=True)

        if submit_btn:
            if not email or not password:
                st.error("Please fill in all fields.")
            elif not validate_email(email):
                st.error("Please enter a valid email address format.")
            else:
                user = get_user_by_email(email)
                if not user:
                    st.error("No account found with this email.")
                elif not verify_password(password, user.get("password_hash", "")):
                    st.error("Incorrect password. Please try again.")
                else:
                    login_user(user)
                    st.success("Successfully logged in! Redirecting...")
                    st.rerun()

        # Link to signup
        st.write("")
        st.markdown(
            """
            <div style="text-align: center; margin-top: 1rem;">
                <span style="color: #6b7280; font-size: 0.9rem;">Don't have an account? </span>
                <a href="signup" target="_self" style="color: #111827; font-weight: 600; text-decoration: none;">Sign Up</a>
            </div>
            """,
            unsafe_allow_html=True
        )