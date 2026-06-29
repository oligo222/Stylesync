"""
wardrobe_adapter.py
"""
import os
import json
import uuid
import base64
from pathlib import Path
from dotenv import load_dotenv
from google import genai

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def scan_single_image(image_bytes, filename="uploaded_image.jpg"):
    wardrobe_folder = Path(__file__).resolve().parent / "wardrobe"
    wardrobe_folder.mkdir(exist_ok=True)
    image_save_path = wardrobe_folder / filename
    image_save_path.write_bytes(image_bytes)

    prompt = """Analyze this clothing item and respond ONLY with a JSON object like this:
{
  "category": "...",
  "garment_type": "...",
  "color": "...",
  "pattern": "...",
  "style": "..."
}

For "category", you MUST choose exactly one of these four values: "Top", "Bottom", "Footwear", "Outerwear".
For "garment_type", describe the specific item naturally (e.g. "camisole", "blazer", "ankle boots", "wide-leg trousers").
For "style", you MUST choose exactly one of these two values: "Formal", "Casual".

No extra text, just the JSON."""

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
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
    if os.path.exists(wardrobe_path):
        wardrobe = json.loads(open(wardrobe_path).read())
    else:
        wardrobe = []
    wardrobe.append(item_data)
    with open(wardrobe_path, "w") as f:
        json.dump(wardrobe, f, indent=2)


CATEGORY_MAP = {
    # Tops
    "shirt": "Top", "t-shirt": "Top", "tshirt": "Top", "polo": "Top",
    "blouse": "Top", "top": "Top", "sweater": "Top", "sweatshirt": "Top",
    "hoodie": "Top", "long-sleeve t-shirt": "Top", "camisole": "Top",
    "tank top": "Top", "vest top": "Top", "tunic": "Top", "crop top": "Top",
    "bodysuit": "Top", "turtleneck": "Top", "henley": "Top",
    "graphic tee": "Top", "sleeveless top": "Top", "knit top": "Top",
    "button-down shirt": "Top", "flannel shirt": "Top", "polo shirt": "Top",

    # Bottoms
    "pants": "Bottom", "trousers": "Bottom", "jeans": "Bottom",
    "shorts": "Bottom", "skirt": "Bottom", "bottom": "Bottom",
    "leggings": "Bottom", "joggers": "Bottom", "chinos": "Bottom",
    "culottes": "Bottom", "wide-leg trousers": "Bottom", "midi skirt": "Bottom",
    "mini skirt": "Bottom", "cargo pants": "Bottom", "sweatpants": "Bottom",
    "track pants": "Bottom", "palazzo pants": "Bottom", "capri pants": "Bottom",

    # Footwear
    "shoes": "Footwear", "sneakers": "Footwear", "boots": "Footwear",
    "sandals": "Footwear", "heels": "Footwear", "footwear": "Footwear",
    "loafers": "Footwear", "flats": "Footwear", "slip-ons": "Footwear",
    "ankle boots": "Footwear", "pumps": "Footwear", "mules": "Footwear",
    "oxfords": "Footwear", "wedges": "Footwear", "espadrilles": "Footwear",
    "slides": "Footwear", "flip flops": "Footwear", "chelsea boots": "Footwear",

    # Outerwear
    "jacket": "Outerwear", "blazer": "Outerwear", "coat": "Outerwear",
    "cardigan": "Outerwear", "outerwear": "Outerwear", "denim jacket": "Outerwear",
    "dress": "Outerwear", "fleece jacket": "Outerwear", "parka": "Outerwear",
    "varsity jacket": "Outerwear", "jumpsuit": "Outerwear", "romper": "Outerwear",
    "overalls": "Outerwear", "trench coat": "Outerwear", "bomber jacket": "Outerwear",
    "windbreaker": "Outerwear", "vest": "Outerwear", "gilet": "Outerwear",
}


def map_category(raw_category):
    if not raw_category:
        return None
    return CATEGORY_MAP.get(raw_category.strip().lower())


def map_style(raw_style):
    if not raw_style:
        return "Casual"
    cleaned = raw_style.strip().lower()
    if "formal" in cleaned:
        return "Formal"
    return "Casual"


def build_item_name(scanned_item):
    color = (scanned_item.get("color") or "").strip().title()
    pattern = (scanned_item.get("pattern") or "").strip().title()
    garment = (scanned_item.get("garment_type") or scanned_item.get("category") or "Item").strip().title()
    parts = [p for p in (color, pattern if pattern.lower() != "solid" else None, garment) if p]
    return " ".join(parts) if parts else "Unnamed Item"


def adapt_scanned_wardrobe(scanned_items):
    converted = []
    skipped = []
    for raw in scanned_items:
        category = map_category(raw.get("category"))
        if category is None:
            # Try to map from garment_type as fallback
            category = map_category(raw.get("garment_type"))
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