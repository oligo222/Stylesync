"""
StyleSync User Profile Database Module

Handles persistence of user profile data, avatars, and appearance attributes.
"""
import os
import sys
from datetime import datetime

# Allow importing from parent directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.users import load_users, save_users

def update_user_profile(user_id: str, profile_data: dict) -> bool:
    """
    Updates the profile fields of an existing user in the database.
    
    Fields updated may include:
    - name, age, gender
    - profile_image_path, avatar_image_path
    - skin_tone, hair_color, hair_length, hair_style, body_type, face_shape, height
    """
    users = load_users()
    updated = False
    
    for user in users:
        if user.get("id") == user_id:
            # List of allowed fields to update
            allowed_fields = {
                "name", "age", "gender", "profile_image_path",
                "avatar_image_path", "avatar_3d_image_path", "skin_tone",
                "hair_color", "hair_length", "hair_style", "body_type",
                "face_shape", "height"
            }
            
            for key, val in profile_data.items():
                if key in allowed_fields:
                    user[key] = val
                    
            user["last_updated"] = datetime.utcnow().isoformat()
            updated = True
            break
            
    if updated:
        save_users(users)
        
    return updated
