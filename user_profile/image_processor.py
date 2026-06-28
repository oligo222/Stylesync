"""
StyleSync Profile Image Processor Module

Handles validation, resizing, optimization, and storage of uploaded profile pictures.
"""
import os
import io
from PIL import Image

def process_and_save_profile_pic(image_bytes, filename: str, user_id: str) -> str:
    """
    Validates, resizes, and optimizes an uploaded profile picture.
    Saves it as a JPEG in data/profile_pics/{user_id}.jpg.
    
    Returns:
        str: Relative path to the saved image file.
    """
    # Verify file extension (sanity check)
    ext = os.path.splitext(filename.lower())[1]
    if ext not in [".png", ".jpg", ".jpeg"]:
        raise ValueError("Unsupported file format. Please upload a JPG, JPEG, or PNG.")

    # Create storage directory inside the project root's data folder
    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data"
    )
    pics_dir = os.path.join(data_dir, "profile_pics")
    os.makedirs(pics_dir, exist_ok=True)
    
    dest_path = os.path.join(pics_dir, f"{user_id}.jpg")
    
    # Process image using Pillow
    img = Image.open(io.BytesIO(image_bytes))
    
    # Convert transparent PNGs (RGBA) or palette images (P) to standard RGB
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    # Resize to standard size (e.g. max 400x400) using Lanczos filter
    img.thumbnail((400, 400), Image.Resampling.LANCZOS)
    
    # Save optimized JPEG
    img.save(dest_path, "JPEG", quality=85, optimize=True)
    
    # Return the relative path from the project root
    return f"data/profile_pics/{user_id}.jpg"


def process_and_save_3d_avatar_image(image_bytes, filename: str, user_id: str) -> str:
    """
    Validates and saves a front-facing full-body image for 3D avatar creation.
    Saves it as a JPEG in data/profile_pics/{user_id}_3d.jpg.

    Returns:
        str: Relative path to the saved image file.
    """
    ext = os.path.splitext(filename.lower())[1]
    if ext not in [".png", ".jpg", ".jpeg"]:
        raise ValueError("Unsupported file format. Please upload a JPG, JPEG, or PNG.")

    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data"
    )
    user_pics_dir = os.path.join(data_dir, "profile_pics", user_id)
    os.makedirs(user_pics_dir, exist_ok=True)

    dest_path = os.path.join(user_pics_dir, "3d_full_body.jpg")

    img = Image.open(io.BytesIO(image_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
    img.save(dest_path, "JPEG", quality=85, optimize=True)

    return f"data/profile_pics/{user_id}/3d_full_body.jpg"
