import json
from pathlib import Path

def load_wardrobe():
    wardrobe_file = Path("wardrobe.json")
    if wardrobe_file.exists():
        return json.loads(wardrobe_file.read_text())
    return []

def get_by_style(style):
    wardrobe = load_wardrobe()
    return [item for item in wardrobe if item["style"].lower() == style.lower()]

def get_by_color(color):
    wardrobe = load_wardrobe()
    return [item for item in wardrobe if item["color"].lower() == color.lower()]

def get_by_category(category):
    wardrobe = load_wardrobe()
    return [item for item in wardrobe if item["category"].lower() == category.lower()]

# Test it
