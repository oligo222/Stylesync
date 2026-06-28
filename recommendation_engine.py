import json

def load_wardrobe(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            return data.get("items", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading wardrobe file: {e}")
        return []

def generate_outfits(wardrobe, event_style):
    categories = ["Top", "Bottom", "Footwear"]
    
    tops = [item for item in wardrobe if item.get("category") == "Top"]
    bottoms = [item for item in wardrobe if item.get("category") == "Bottom"]
    footwear = [item for item in wardrobe if item.get("category") == "Footwear"]
    
    matching_tops = [item for item in tops if item.get("style") == event_style]
    if not matching_tops:
        matching_tops = tops
        
    matching_bottoms = [item for item in bottoms if item.get("style") == event_style]
    if not matching_bottoms:
        matching_bottoms = bottoms
        
    matching_footwear = [item for item in footwear if item.get("style") == event_style]
    if not matching_footwear:
        matching_footwear = footwear
        
    top_names = [item["item"] for item in matching_tops] if matching_tops else [None]
    bottom_names = [item["item"] for item in matching_bottoms] if matching_bottoms else [None]
    footwear_names = [item["item"] for item in matching_footwear] if matching_footwear else [None]
    
    outfits = []
    seen = set()
    
    for top in top_names:
        for bottom in bottom_names:
            for shoe in footwear_names:
                combo = (top, bottom, shoe)
                if combo not in seen:
                    seen.add(combo)
                    outfits.append({
                        "top": top,
                        "bottom": bottom,
                        "footwear": shoe
                    })
                    if len(outfits) == 3:
                        return outfits
                        
    return outfits

if __name__ == "__main__":
    wardrobe_items = load_wardrobe("data/wardrobe.json")
    formal_outfits = generate_outfits(wardrobe_items, "Formal")
    print(json.dumps(formal_outfits, indent=2))