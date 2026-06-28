"""
StyleSync User Database Module

Handles loading, saving, and querying user data stored in JSON format.
"""
import os
import json
import uuid
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "users.json")

def _init_db():
    """Ensures database directory and file exist."""
    os.makedirs(DB_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump([], f, indent=4)

def load_users() -> list:
    """Loads all users from the JSON database."""
    _init_db()
    try:
        with open(DB_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_users(users: list):
    """Saves all users to the JSON database."""
    _init_db()
    with open(DB_PATH, "w") as f:
        json.dump(users, f, indent=4, default=str)

def get_user_by_email(email: str) -> dict:
    """Finds a user by email (case-insensitive). Returns user dict or None."""
    users = load_users()
    email_lower = email.strip().lower()
    for user in users:
        if user.get("email", "").strip().lower() == email_lower:
            return user
    return None

def get_user_by_id(user_id: str) -> dict:
    """Finds a user by User ID. Returns user dict or None."""
    users = load_users()
    for user in users:
        if user.get("id") == user_id:
            return user
    return None

def create_user(name: str, age: int, gender: str, email: str, password_hash: str) -> dict:
    """
    Creates a new user, saves it to the database, and returns the user dict.
    Returns None if a duplicate email is found.
    """
    if get_user_by_email(email):
        return None

    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "name": name.strip(),
        "age": int(age),
        "gender": gender.strip(),
        "email": email.strip().lower(),
        "password_hash": password_hash,
        "created_at": datetime.utcnow().isoformat(),
        "membership_tier": "Premium Member" # Default membership tier for integration
    }

    users = load_users()
    users.append(new_user)
    save_users(users)
    return new_user

def update_user(user_id: str, updates: dict) -> dict:
    """
    Updates fields of an existing user and returns the updated user dict or None.
    Does not allow modifying the email or ID fields directly.
    """
    users = load_users()
    for user in users:
        if user.get("id") == user_id:
            for key, val in updates.items():
                if key not in ["id", "email", "password_hash", "created_at"]:
                    user[key] = val
            save_users(users)
            return user
    return None
