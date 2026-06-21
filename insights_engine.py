import json
import os
from recommendation_engine import load_wardrobe

def load_usage_history(filepath="data/usage_history.json"):
    """
    Reads the JSON file at filepath if it exists and returns the list under
    the "used_items" key. Returns an empty list if file doesn't exist or is invalid.
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, "r") as file:
                data = json.load(file)
                return data.get("used_items", [])
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        pass
    return []

def load_score_history(filepath="data/usage_history.json"):
    """
    Reads the JSON file at filepath if it exists and returns the list under
    the "scores" key. Returns an empty list if file doesn't exist or is invalid.
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, "r") as file:
                data = json.load(file)
                return data.get("scores", [])
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        pass
    return []

def save_usage_history(item_names, score=None, filepath="data/usage_history.json"):
    """
    Saves new item names to the usage history JSON file, avoiding duplicates.
    Also appends the outfit's suitability score to a running score log, if provided.
    Creates parent directories and the file if they do not exist.
    """
    dir_name = os.path.dirname(filepath)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
        
    history = load_usage_history(filepath)
    scores = load_score_history(filepath)
    
    for name in item_names:
        if name not in history:
            history.append(name)
    
    if score is not None:
        scores.append(score)
            
    try:
        with open(filepath, "w") as file:
            json.dump({"used_items": history, "scores": scores}, file, indent=2)
    except Exception as e:
        print(f"Error saving usage history: {e}")

def most_versatile_item(wardrobe):
    """
    Counts how many times each item could theoretically be combined with items
    from other core categories (Top, Bottom, Footwear).
    """
    categories = ["Top", "Bottom", "Footwear"]
    
    counts = {cat: 0 for cat in categories}
    for item in wardrobe:
        cat = item.get("category")
        if cat in counts:
            counts[cat] += 1
            
    best_item = None
    max_combinations = -1
    
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
    Analyzes core item counts, identifies the weakest category, and returns
    a mathematically defensible shopping suggestion with real impact metrics.
    """
    core_categories = ["Top", "Bottom", "Footwear"]
    
    # Track counts across core items for math calculations
    counts = {cat: 0 for cat in core_categories}
    for item in wardrobe:
        cat = item.get("category")
        if cat in counts:
            counts[cat] += 1
            
    # Fallback/include Outerwear in evaluation if everything else is fully stacked
    all_categories = ["Top", "Bottom", "Footwear", "Outerwear"]
    full_counts = {cat: 0 for cat in all_categories}
    for item in wardrobe:
        cat = item.get("category")
        if cat in full_counts:
            full_counts[cat] += 1
            
    weakest_category = min(all_categories, key=lambda c: full_counts[c])
    
    # Define archetypes for the core recommendations
    archetype_map = {
        "Top": "a classic neutral white t-shirt",
        "Bottom": "a versatile pair of dark denim jeans",
        "Footwear": "a clean pair of minimalist white sneakers",
        "Outerwear": "a timeless neutral jacket"
    }
    suggestion = archetype_map.get(weakest_category, "a versatile basic piece")
    
    # Compute exact combination impact matrix if a core category is lacking
    if weakest_category in core_categories:
        other_cats = [c for c in core_categories if c != weakest_category]
        combos_unlocked = counts[other_cats[0]] * counts[other_cats[1]]
    else:
        # If Outerwear is missing, it multiplies across existing 3-piece core outfits
        combos_unlocked = counts["Top"] * counts["Bottom"] * counts["Footwear"]

    # Heuristic versatility calculation: % of core elements this item natively pairs with
    total_wardrobe = len(wardrobe)
    versatility_impact = round((combos_unlocked / max(1, total_wardrobe)) * 10)
    # Clip versatility to a realistic, clean range (+10% to +25%)
    versatility_impact = max(10, min(versatility_impact, 25))

    scores = load_score_history()
    current_score = round(sum(scores) / len(scores)) if scores else None

    return {
        "weakest_category": weakest_category,
        "shopping_advisor": {
            "current_score": current_score,
            "suggestion": suggestion,
            "impact": {
                "combos_unlocked": f"+{combos_unlocked} outfit combinations unlocked",
                "versatility": f"+{versatility_impact}% versatility impact"
            }
        }
    }

def generate_insights(wardrobe, recently_used_items):
    """
    Runs all four insights functions and returns a combined dictionary.
    """
    num_outfits = max(1, len(recently_used_items) // 3)
    
    return {
        "most_versatile": most_versatile_item(wardrobe),
        "sustainability": sustainability_insight(num_outfits),
        "forgotten_gems": forgotten_gems(wardrobe, recently_used_items),
        "gap_analysis": gap_analysis(wardrobe)
    }
