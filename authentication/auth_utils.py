"""
StyleSync Authentication Utility Functions
Contains helpers for cryptography, input validation, and session state guarding.
"""
import re
import os
import json
import hashlib
import streamlit as st
import sys

# Ensure database module is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.users import get_user_by_id

SESSION_FILE = os.path.join(PROJECT_ROOT, "data", "active_session.json")

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    pw_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000
    ).hex()
    return f"{salt}:{pw_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash or ":" not in stored_hash:
        return False
    try:
        salt, pw_hash = stored_hash.split(":", 1)
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000
        ).hex()
        return computed_hash == pw_hash
    except Exception:
        return False

def validate_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def init_session():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = None

    if not st.session_state["logged_in"]:
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r") as f:
                    data = json.load(f)
                user_id = data.get("user_id")
                if user_id:
                    user = get_user_by_id(user_id)
                    if user:
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = user
            except Exception:
                try:
                    os.remove(SESSION_FILE)
                except Exception:
                    pass

def login_user(user: dict):
    st.session_state["logged_in"] = True
    st.session_state["user"] = user
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump({"user_id": user.get("id")}, f)
    except Exception:
        pass

def logout():
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except Exception:
            pass
    st.switch_page("pages/profile.py")  # ← changed from auth.py

def require_login():
    init_session()
    if not st.session_state["logged_in"]:
        st.switch_page("pages/profile.py")  # ← changed from auth.py
        st.stop()