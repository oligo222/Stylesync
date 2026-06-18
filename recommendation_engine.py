import json

def load_wardrobe(filepath):
    """
    Reads a wardrobe JSON file and returns the list of wardrobe items.
    
    Parameters:
        filepath (str): The path to the wardrobe JSON file.
        
    Returns:
        list: A list of dicts representing wardrobe items.
    """
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            # Return the list under the "items" key, or an empty list if not found
            return data.get("items", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading wardrobe file: {e}")
        return []

def generate_outfits(wardrobe, event_style):
    """
    Generates up to 3 outfit combinations matching the event style.
    
    Parameters:
        wardrobe (list): The list of wardrobe items.
        event_style (str): The desired style of the outfit (e.g., "Formal", "Casual").
        
    Returns:
        list: A list of up to 3 outfit dicts, each containing "top", "bottom", and "footwear".
    """
    # 1. Filter items by category: "Top", "Bottom", and "Footwear"
    tops = [item for item in wardrobe if item.get("category") == "Top"]
    bottoms = [item for item in wardrobe if item.get("category") == "Bottom"]
    footwear = [item for item in wardrobe if item.get("category") == "Footwear"]
    
    # 2. Filter items within each category by event_style
    # If no items match the style in a category, fall back to including all items of that category.
    matching_tops = [item for item in tops if item.get("style") == event_style]
    if not matching_tops:
        matching_tops = tops
        
    matching_bottoms = [item for item in bottoms if item.get("style") == event_style]
    if not matching_bottoms:
        matching_bottoms = bottoms
        
    matching_footwear = [item for item in footwear if item.get("style") == event_style]
    if not matching_footwear:
        matching_footwear = footwear
        
    # Extract item name strings, or use [None] if no items are available in that category
    top_names = [item["item"] for item in matching_tops] if matching_tops else [None]
    bottom_names = [item["item"] for item in matching_bottoms] if matching_bottoms else [None]
    footwear_names = [item["item"] for item in matching_footwear] if matching_footwear else [None]
    
    # 3. Build up to 3 different outfit combinations
    outfits = []
    seen = set()
    
    # Nested loops to generate combinations of tops, bottoms, and footwear
    for top in top_names:
        for bottom in bottom_names:
            for shoe in footwear_names:
                # Store the outfit combo
                combo = (top, bottom, shoe)
                if combo not in seen:
                    seen.add(combo)
                    outfits.append({
                        "top": top,
                        "bottom": bottom,
                        "footwear": shoe
                    })
                    # Limit to at most 3 outfits
                    if len(outfits) == 3:
                        return outfits
                        
    return outfits

if __name__ == "__main__":
    # Load the wardrobe data
    wardrobe_items = load_wardrobe("data/wardrobe.json")
    
    # Generate Formal outfits
    formal_outfits = generate_outfits(wardrobe_items, "Formal")
    
    # Print the resulting outfits as formatted JSON
    print(json.dumps(formal_outfits, indent=2))
