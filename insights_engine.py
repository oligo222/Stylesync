import json
import os
from recommendation_engine import load_wardrobe

def load_usage_history(filepath="data/usage_history.json"):
    """
    Reads the JSON file at filepath if it exists and returns the list under
    the "used_items" key. Returns an empty list if file doesn't exist or is invalid.
    
    Parameters:
        filepath (str): The path to the usage history JSON file.
        
    Returns:
        list: A list of item name strings.
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, "r") as file:
                data = json.load(file)
                return data.get("used_items", [])
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        pass
    return []

def save_usage_history(item_names, filepath="data/usage_history.json"):
    """
    Saves new item names to the usage history JSON file, avoiding duplicates.
    Creates parent directories and the file if they do not exist.
    
    Parameters:
        item_names (list): A list of item name strings to add.
        filepath (str): The path to save the usage history.
    """
    # Ensure parent directory exists
    dir_name = os.path.dirname(filepath)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
        
    # Load existing history list
    history = load_usage_history(filepath)
    
    # Append new item names if they are not already present (maintaining order)
    for name in item_names:
        if name not in history:
            history.append(name)
            
    # Save the updated history back to the file
    try:
        with open(filepath, "w") as file:
            json.dump({"used_items": history}, file, indent=2)
    except Exception as e:
        print(f"Error saving usage history: {e}")

def most_versatile_item(wardrobe):
    """
    Counts how many times each item could theoretically be combined with items
    from other core categories (Top, Bottom, Footwear).
    
    Parameters:
        wardrobe (list): The list of wardrobe items.
        
    Returns:
        dict: A dictionary containing the "item" name and its "combination_count".
    """
    categories = ["Top", "Bottom", "Footwear"]
    
    # Count the total number of items in each category
    counts = {cat: 0 for cat in categories}
    for item in wardrobe:
        cat = item.get("category")
        if cat in counts:
            counts[cat] += 1
            
    best_item = None
    max_combinations = -1
    
    # Calculate combination score for each item
    for item in wardrobe:
        cat = item.get("category")
        if cat not in categories:
            continue
            
        other_cats = [c for c in categories if c != cat]
        combinations = 1
        for oc in other_cats:
            combinations *= counts[oc]
            
        if combinations > max_combinations:
            max_combinations = combinations
            best_item = item.get("item")
            
    return {
        "item": best_item,
        "combination_count": max(0, max_combinations)
    }

def sustainability_insight(num_outfits_generated, num_new_items_needed=0):
    """
    Calculates the wardrobe reuse percentage and provides a sustainability message.
    
    Parameters:
        num_outfits_generated (int): The number of outfits recommended.
        num_new_items_needed (int): The number of new items needed.
        
    Returns:
        dict: A dictionary containing the sustainability "message".
    """
    if num_new_items_needed == 0:
        reuse_pct = 100
    else:
        total_slots = num_outfits_generated * 3
        if total_slots > 0:
            reuse_pct = round(((total_slots - num_new_items_needed) / total_slots) * 100, 1)
        else:
            reuse_pct = 0.0
            
    message = (
        f"Your outfit recommendations successfully reused {reuse_pct}% of your "
        f"existing wardrobe, requiring {num_new_items_needed} new items."
    )
    
    return {
        "message": message
    }

def forgotten_gems(wardrobe, recently_used_items):
    """
    Identifies items in the wardrobe that have not been recently recommended.
    Returns at most 3 unique item names.
    
    Parameters:
        wardrobe (list): The list of wardrobe items.
        recently_used_items (list): Names of items recently used.
        
    Returns:
        list: A list of up to 3 "forgotten" item name strings.
    """
    forgotten = []
    seen = set()
    
    for item in wardrobe:
        name = item.get("item")
        if name not in recently_used_items and name not in seen:
            seen.add(name)
            forgotten.append(name)
            if len(forgotten) == 3:
                break
                
    return forgotten

def gap_analysis(wardrobe):
    """
    Analyzes item counts per category (Top, Bottom, Footwear, Outerwear) and
    identifies which category has the fewest items (the weakest category).
    
    Parameters:
        wardrobe (list): The list of wardrobe items.
        
    Returns:
        dict: Contains a suggestions "message" and the "weakest_category".
    """
    categories = ["Top", "Bottom", "Footwear", "Outerwear"]
    
    counts = {cat: 0 for cat in categories}
    for item in wardrobe:
        cat = item.get("category")
        if cat in counts:
            counts[cat] += 1
            
    weakest_category = min(categories, key=lambda c: counts[c])
    message = f"You could add an item in the '{weakest_category}' category to unlock more outfit combinations."
    
    return {
        "message": message,
        "weakest_category": weakest_category
    }

def generate_insights(wardrobe, recently_used_items):
    """
    Runs all four insights functions and returns a combined dictionary.
    
    Parameters:
        wardrobe (list): The list of wardrobe items.
        recently_used_items (list): Names of items recently used.
        
    Returns:
        dict: A combined dictionary containing all insights.
    """
    # Infer the number of outfits generated based on the number of recently used items (3 items per outfit)
    num_outfits = max(1, len(recently_used_items) // 3)
    
    return {
        "most_versatile": most_versatile_item(wardrobe),
        "sustainability": sustainability_insight(num_outfits),
        "forgotten_gems": forgotten_gems(wardrobe, recently_used_items),
        "gap_analysis": gap_analysis(wardrobe)
    }

if __name__ == "__main__":
    # Test main execution locally
    wardrobe_items = load_wardrobe("data/wardrobe.json")
    
    # Try to load existing history or use a mock fallback
    history = load_usage_history()
    if not history:
        print("No history found, using test items and writing them to history...")
        test_items = ["White Shirt", "Black Trousers", "Black Formal Shoes"]
        save_usage_history(test_items)
        history = load_usage_history()
        
    print(f"Current Usage History: {history}")
    
    # Generate insights using current history
    insights = generate_insights(wardrobe_items, history)
    print("\nGenerated Insights:")
    print(json.dumps(insights, indent=2))
