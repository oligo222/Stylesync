import json
import random
from itertools import product

def load_wardrobe(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            # Handle both formats: plain list or {"items": [...]}
            if isinstance(data, list):
                return data
            return data.get("items", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading wardrobe file: {e}")
        return []

def generate_outfits(wardrobe, event_style, max_outfits=6):
    tops     = [item for item in wardrobe if item.get("category") == "Top"]
    bottoms  = [item for item in wardrobe if item.get("category") == "Bottom"]
    footwear = [item for item in wardrobe if item.get("category") == "Footwear"]

    # Prefer style-matched items, fall back to all items
    matching_tops     = [i for i in tops     if i.get("style") == event_style] or tops
    matching_bottoms  = [i for i in bottoms  if i.get("style") == event_style] or bottoms
    matching_footwear = [i for i in footwear if i.get("style") == event_style] or footwear

    random.shuffle(matching_tops)
    random.shuffle(matching_bottoms)
    random.shuffle(matching_footwear)

    top_names      = [i.get("item") or i.get("garment_type", "Unknown") for i in matching_tops]     or [None]
    bottom_names   = [i.get("item") or i.get("garment_type", "Unknown") for i in matching_bottoms]  or [None]
    footwear_names = [i.get("item") or i.get("garment_type", "Unknown") for i in matching_footwear] or [None]

    # Generate all unique combinations then pick the best spread
    all_combos = list(product(top_names, bottom_names, footwear_names))
    random.shuffle(all_combos)

    outfits      = []
    seen_tops    = set()
    seen_bottoms = set()
    seen_shoes   = set()

    # First pass: maximise variety — each item used at most once
    for top, bottom, shoe in all_combos:
        if top not in seen_tops and bottom not in seen_bottoms and shoe not in seen_shoes:
            outfits.append({"top": top, "bottom": bottom, "footwear": shoe})
            seen_tops.add(top)
            seen_bottoms.add(bottom)
            seen_shoes.add(shoe)
        if len(outfits) >= max_outfits:
            break

    # Second pass: fill remaining slots allowing item reuse (different combos)
    if len(outfits) < max_outfits:
        existing = {(o["top"], o["bottom"], o["footwear"]) for o in outfits}
        for top, bottom, shoe in all_combos:
            if (top, bottom, shoe) not in existing:
                outfits.append({"top": top, "bottom": bottom, "footwear": shoe})
                existing.add((top, bottom, shoe))
            if len(outfits) >= max_outfits:
                break

    return outfits

if __name__ == "__main__":
    wardrobe_items = load_wardrobe("wardrobe.json")
    print(f"Loaded {len(wardrobe_items)} wardrobe items")
    casual_outfits = generate_outfits(wardrobe_items, "Casual")
    print(f"Generated {len(casual_outfits)} outfits")
    print(json.dumps(casual_outfits, indent=2))