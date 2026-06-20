"""
wardrobe_adapter.py

Converts Module B's scanned wardrobe output (scan_clothing.py's wardrobe.json)
into the schema Module C's recommendation_engine.py expects.

Module B schema (bare list):
    [{"category": "shirt", "color": "blue", "pattern": "solid",
      "style": "formal", "id": "...", "image_path": "..."}, ...]

Module C schema (wrapped dict):
    {"items": [{"item": "Blue Solid Shirt", "category": "Top",
                "color": "Blue", "style": "Formal"}, ...]}

generate_outfits() in recommendation_engine.py does EXACT, case-sensitive
matches on "category" (Top/Bottom/Footwear/Outerwear) and "style"
(Formal/Casual), and does item["item"] with direct indexing (no .get),
so every converted item MUST have a non-empty "item" name or it will crash.
"""

import json
from pathlib import Path

# Maps the raw garment-type strings Gemini Vision might return (lowercase,
# loosely matched) to Module C's four category buckets. Extend this as
# scan_clothing.py encounters new garment types during testing.
CATEGORY_MAP = {
    "shirt": "Top", "t-shirt": "Top", "tshirt": "Top", "polo": "Top",
    "blouse": "Top", "top": "Top", "sweater": "Top", "sweatshirt": "Top",
    "hoodie": "Top",

    "pants": "Bottom", "trousers": "Bottom", "jeans": "Bottom",
    "shorts": "Bottom", "skirt": "Bottom", "bottom": "Bottom",

    "shoes": "Footwear", "sneakers": "Footwear", "boots": "Footwear",
    "sandals": "Footwear", "heels": "Footwear", "footwear": "Footwear",

    "jacket": "Outerwear", "blazer": "Outerwear", "coat": "Outerwear",
    "cardigan": "Outerwear", "outerwear": "Outerwear", "denim jacket": "Outerwear",
}


def map_category(raw_category):
    """
    Maps a raw scanned category string to Module C's Top/Bottom/Footwear/
    Outerwear taxonomy. Returns None if unrecognized (caller should skip
    such items rather than guess, to avoid silently misplacing them).
    """
    if not raw_category:
        return None
    return CATEGORY_MAP.get(raw_category.strip().lower())


def map_style(raw_style):
    """Title-cases the style string: 'formal' -> 'Formal'. Defaults to
    'Casual' if missing/unrecognized, since that's the safer fallback
    (won't be excluded from a Casual-event outfit search)."""
    if not raw_style:
        return "Casual"
    cleaned = raw_style.strip().lower()
    if cleaned == "formal":
        return "Formal"
    if cleaned == "casual":
        return "Casual"
    return raw_style.strip().title()


def build_item_name(scanned_item):
    """
    Builds the human-readable 'item' name Module C requires, since
    Module B's scanner doesn't produce one. E.g.
    {"color": "blue", "pattern": "solid", "category": "shirt"}
    -> "Blue Solid Shirt"
    """
    color = (scanned_item.get("color") or "").strip().title()
    pattern = (scanned_item.get("pattern") or "").strip().title()
    category = (scanned_item.get("category") or "Item").strip().title()

    # Skip "Solid" in the name since it's the default/uninteresting case
    parts = [p for p in (color, pattern if pattern.lower() != "solid" else None, category) if p]
    return " ".join(parts) if parts else "Unnamed Item"


def adapt_scanned_wardrobe(scanned_items):
    """
    Converts a list of Module B scanned items into Module C's item schema.
    Items with an unrecognized category are skipped (and reported) rather
    than guessed, since generate_outfits() requires an exact category match
    to ever place an item into an outfit.

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
    Reads Module B's wardrobe.json (bare list) and returns it already
    converted into Module C's wrapped {"items": [...]} schema, ready to
    pass straight to recommendation_engine.generate_outfits().
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
    # Quick smoke test against the real scanned file
    result = load_and_adapt("wardrobe.json")
    print(json.dumps(result, indent=2))