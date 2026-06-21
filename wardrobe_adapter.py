"""
wardrobe_adapter.py

Converts Module B's scanned wardrobe output (scan_clothing.py's wardrobe.json)
into the schema Module C's recommendation_engine.py expects, and provides
functions for scanning new items directly from the Streamlit UI.
"""

import os
import json
import uuid
import base64
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Explicitly point to .env in the project root, regardless of where this
# module gets imported from (fixes silent auth failures when imported
# from Streamlit pages running with a different working directory).
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def scan_single_image(image_bytes, filename="uploaded_image.jpg"):
    """
    Sends a single image to Gemini Vision and returns structured clothing data.
    Also saves the image file into the wardrobe/ folder.
    """
    # Save the image file so it can be displayed later
    wardrobe_folder = Path(__file__).resolve().parent / "wardrobe"
    wardrobe_folder.mkdir(exist_ok=True)
    image_save_path = wardrobe_folder / filename
    image_save_path.write_bytes(image_bytes)

    prompt = """Analyze this clothing item and respond ONLY with a JSON object like this:
{
  "category": "...",
  "color": "...",
  "pattern": "...",
  "style": "..."
}
No extra text, just the JSON."""

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[
                {
                    "parts": [
                        {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(image_bytes).decode()}},
                        {"text": prompt}
                    ]
                }
            ]
        )
        cleaned = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(cleaned)
        data["id"] = str(uuid.uuid4())
        data["image_path"] = f"wardrobe/{filename}"
        return data
    except Exception as e:
        import streamlit as st
        st.error(f"DEBUG - Real error: {e}")
        print(f"Error scanning image: {e}")
        return None


def add_item_to_wardrobe(item_data, wardrobe_path="wardrobe.json"):
    """
    Appends a new scanned item to wardrobe.json and saves it.
    """
    if os.path.exists(wardrobe_path):
        wardrobe = json.loads(open(wardrobe_path).read())
    else:
        wardrobe = []

    wardrobe.append(item_data)

    with open(wardrobe_path, "w") as f:
        json.dump(wardrobe, f, indent=2)


# Maps the raw garment-type strings Gemini Vision might return (lowercase,
# loosely matched) to Module C's four category buckets.
CATEGORY_MAP = {
    "shirt": "Top", "t-shirt": "Top", "tshirt": "Top", "polo": "Top",
    "blouse": "Top", "top": "Top", "sweater": "Top", "sweatshirt": "Top",
    "hoodie": "Top", "long-sleeve t-shirt": "Top",

    "pants": "Bottom", "trousers": "Bottom", "jeans": "Bottom",
    "shorts": "Bottom", "skirt": "Bottom", "bottom": "Bottom",

    "shoes": "Footwear", "sneakers": "Footwear", "boots": "Footwear",
    "sandals": "Footwear", "heels": "Footwear", "footwear": "Footwear",

    "jacket": "Outerwear", "blazer": "Outerwear", "coat": "Outerwear",
    "cardigan": "Outerwear", "outerwear": "Outerwear", "denim jacket": "Outerwear",
    "dress": "Outerwear", "fleece jacket": "Outerwear", "parka": "Outerwear",
    "varsity jacket": "Outerwear",
}


def map_category(raw_category):
    """Maps a raw scanned category string to Module C's taxonomy."""
    if not raw_category:
        return None
    return CATEGORY_MAP.get(raw_category.strip().lower())


def map_style(raw_style):
    """Title-cases the style string. Defaults to 'Casual' if missing/unrecognized."""
    if not raw_style:
        return "Casual"
    cleaned = raw_style.strip().lower()
    if cleaned == "formal":
        return "Formal"
    if cleaned == "casual":
        return "Casual"
    return raw_style.strip().title()


def build_item_name(scanned_item):
    """Builds the human-readable 'item' name Module C requires."""
    color = (scanned_item.get("color") or "").strip().title()
    pattern = (scanned_item.get("pattern") or "").strip().title()
    category = (scanned_item.get("category") or "Item").strip().title()

    parts = [p for p in (color, pattern if pattern.lower() != "solid" else None, category) if p]
    return " ".join(parts) if parts else "Unnamed Item"


def adapt_scanned_wardrobe(scanned_items):
    """
    Converts a list of Module B scanned items into Module C's item schema.
    Returns: (converted_items, skipped_items)
    """
    converted = []
    skipped = []

    for raw in scanned_items:
        category = map_category(raw.get("category"))
        if category is None:
            skipped.append(raw)
            continue

        converted.append({
            "item": build_item_name(raw),
            "category": category,
            "color": (raw.get("color") or "").strip().title(),
            "style": map_style(raw.get("style")),
        })

    return converted, skipped


def load_and_adapt(scanned_wardrobe_filepath):
    """
    Reads Module B's wardrobe.json (bare list) and returns it converted
    into Module C's wrapped {"items": [...]} schema.
    """
    path = Path(scanned_wardrobe_filepath)
    if not path.exists():
        print(f"Scanned wardrobe file not found: {path}")
        return {"items": []}

    try:
        raw_items = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"Error parsing scanned wardrobe file: {e}")
        return {"items": []}

    converted, skipped = adapt_scanned_wardrobe(raw_items)

    if skipped:
        skipped_categories = sorted({(item.get("category") or "unknown") for item in skipped})
        print(
            f"Skipped {len(skipped)} item(s) with unrecognized category: "
            f"{skipped_categories}. Add them to CATEGORY_MAP in "
            f"wardrobe_adapter.py if they should be included."
        )

    return {"items": converted}


if __name__ == "__main__":
    result = load_and_adapt("wardrobe.json")
    print(json.dumps(result, indent=2))
