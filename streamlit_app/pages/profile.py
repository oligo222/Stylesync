"""
StyleSync Profile Page
Handles both auth (logged out) and profile (logged in) in one page.
"""
import os
import sys
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from authentication.auth_utils import (
    init_session, hash_password, login_user,
    validate_email, verify_password
)
from database.users import get_user_by_email, create_user
from user_profile.profile_page import render_profile_page

st.set_page_config(
    page_title="StyleSync",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def render_auth():
    css_path = os.path.join(PROJECT_ROOT, "streamlit_app", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown("""
        <style>
        div[data-testid="stForm"] {
            border: 1px solid #e5e7eb !important;
            border-radius: 16px !important;
            padding: 2.5rem !important;
            background-color: #ffffff !important;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05) !important;
        }
        .stButton>button {
            background: linear-gradient(90deg, #111827 0%, #374151 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.6rem 1.5rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("""
            <div style="text-align:center; padding: 2rem 0 1.5rem 0;">
                <div style="font-size:2.5rem; font-weight:700;
                    background: linear-gradient(135deg, #111827 0%, #4b5563 100%);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    StyleSync ✨
                </div>
                <div style="color:#6b7280; font-size:0.95rem; margin-top:4px;">
                    AI-Powered Wardrobe & Style Planner
                </div>
            </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

        # ── LOGIN ──────────────────────────────────────────────────
        with tab_login:
            st.write("### Welcome Back")
            st.caption("Log in to your account to continue styling.")

            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email Address", placeholder="e.g. alex@example.com")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                login_btn = st.form_submit_button("Sign In", use_container_width=True)

            if login_btn:
                if not email or not password:
                    st.error("Please fill in all fields.")
                elif not validate_email(email):
                    st.error("Please enter a valid email address.")
                else:
                    user = get_user_by_email(email)
                    if not user:
                        st.error("No account found with this email.")
                    elif not verify_password(password, user.get("password_hash", "")):
                        st.error("Incorrect password. Please try again.")
                    else:
                        login_user(user)
                        st.success("Logged in! Loading your profile...")
                        st.rerun()

        # ── SIGN UP ────────────────────────────────────────────────
        with tab_signup:
            st.write("### Create Account")
            st.caption("Join StyleSync to digitize your closet and get AI recommendations.")

            with st.form("signup_form", clear_on_submit=False):
                name = st.text_input("Full Name", placeholder="e.g. Alex Johnson")

                col_age, col_gender = st.columns(2)
                with col_age:
                    age_input = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)
                with col_gender:
                    gender = st.selectbox("Gender", ["Female", "Male", "Non-binary", "Prefer not to say"])

                email_s = st.text_input("Email Address", placeholder="e.g. alex@example.com")
                password_s = st.text_input("Password", type="password", placeholder="At least 6 characters")
                confirm_s = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                signup_btn = st.form_submit_button("Sign Up", use_container_width=True)

            if signup_btn:
                if not name or not email_s or not password_s or not confirm_s:
                    st.error("Please fill in all fields.")
                elif not validate_email(email_s):
                    st.error("Please enter a valid email address.")
                elif len(password_s) < 6:
                    st.error("Password must be at least 6 characters.")
                elif password_s != confirm_s:
                    st.error("Passwords do not match.")
                elif get_user_by_email(email_s):
                    st.error("An account with this email already exists.")
                else:
                    hashed = hash_password(password_s)
                    new_user = create_user(
                        name=name,
                        age=age_input,
                        gender=gender,
                        email=email_s,
                        password_hash=hashed
                    )
                    if new_user:
                        login_user(new_user)
                        st.success("Account created! Loading your profile...")
                        st.rerun()
                    else:
                        st.error("Something went wrong. Please try again.")

def main():
    init_session()

    if st.session_state.get("logged_in"):
        render_profile_page()
    else:
        render_auth()

if __name__ == "__main__":
    main()