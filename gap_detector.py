"""
StyleSync Gap Detector

Analyzes wardrobe completeness and suggests missing essential items.
"""
import streamlit as st
from collections import Counter

WARDROBE_ESSENTIALS = {
    # Formal
    "Formal Top":           {"category": "Top",        "style": "Formal",      "label": "Formal top (shirt/blouse)"},
    "Formal Bottom":        {"category": "Bottom",     "style": "Formal",      "label": "Formal bottom (trousers/skirt)"},
    "Formal Footwear":      {"category": "Footwear",   "style": "Formal",      "label": "Formal footwear (heels/dress shoes)"},
    "Formal Outerwear":     {"category": "Outerwear",  "style": "Formal",      "label": "Formal outerwear (blazer/coat)"},
    "Formal Dress":         {"category": "Dress",      "style": "Formal",      "label": "Formal dress (for events/dinners)"},
    # Casual
    "Casual Top":           {"category": "Top",        "style": "Casual",      "label": "Casual top (t-shirt/knit)"},
    "Casual Bottom":        {"category": "Bottom",     "style": "Casual",      "label": "Casual bottom (jeans/skirt)"},
    "Casual Footwear":      {"category": "Footwear",   "style": "Casual",      "label": "Casual footwear (sneakers/flats)"},
    "Casual Outerwear":     {"category": "Outerwear",  "style": "Casual",      "label": "Casual outerwear (denim jacket/hoodie)"},
    "Casual Dress":         {"category": "Dress",      "style": "Casual",      "label": "Casual dress (summer/everyday)"},
    # Smart Casual
    "Smart Casual Top":     {"category": "Top",        "style": "Smart Casual","label": "Smart casual top (polo/linen shirt)"},
    "Smart Casual Bottom":  {"category": "Bottom",     "style": "Smart Casual","label": "Smart casual bottom (chinos/trousers)"},
    "Smart Casual Footwear":{"category": "Footwear",   "style": "Smart Casual","label": "Smart casual shoes (loafers/clean boots)"},
    # Ethnic
    "Ethnic Top":           {"category": "Top",        "style": "Ethnic",      "label": "Ethnic top (kurta/kurti)"},
    "Ethnic Bottom":        {"category": "Bottom",     "style": "Ethnic",      "label": "Ethnic bottom (salwar/palazzo)"},
    "Ethnic Outfit":        {"category": "Dress",      "style": "Ethnic",      "label": "Ethnic outfit (saree/salwar suit/lehenga)"},
    "Ethnic Footwear":      {"category": "Footwear",   "style": "Ethnic",      "label": "Ethnic footwear (juttis/kolhapuris)"},
    # Active / Loungewear
    "Activewear Top":       {"category": "Top",        "style": "Activewear",  "label": "Activewear top (sports tee/tank)"},
    "Activewear Bottom":    {"category": "Bottom",     "style": "Activewear",  "label": "Activewear bottom (leggings/shorts)"},
    "Activewear Footwear":  {"category": "Footwear",   "style": "Activewear",  "label": "Sports footwear (running shoes)"},
    "Loungewear":           {"category": "Loungewear", "style": "Casual",      "label": "Loungewear / pyjama set"},
    # Accessories
    "Belt":                 {"category": "Accessory",  "style": "Formal",      "label": "Formal belt (black/brown leather)"},
    "Casual Bag":           {"category": "Bag",        "style": "Casual",      "label": "Casual bag (tote/backpack)"},
    "Formal Bag":           {"category": "Bag",        "style": "Formal",      "label": "Formal bag (structured handbag)"},
    "Sunglasses":           {"category": "Accessory",  "style": "Casual",      "label": "Sunglasses"},
    "Watch":                {"category": "Accessory",  "style": "Smart Casual","label": "Watch (everyday wear)"},
    "Scarf / Dupatta":      {"category": "Accessory",  "style": "Ethnic",      "label": "Scarf / dupatta"},
}

GAP_SUGGESTIONS = {
    "Formal Outerwear":      {"suggestion": "A black blazer instantly elevates any formal outfit.", "combo_boost": 8},
    "Formal Top":            {"suggestion": "A crisp white shirt is the most versatile formal item you can own.", "combo_boost": 5},
    "Formal Bottom":         {"suggestion": "Tailored black trousers unlock countless formal combinations.", "combo_boost": 7},
    "Formal Footwear":       {"suggestion": "Classic black heels or Oxford shoes work for almost every formal event.", "combo_boost": 5},
    "Formal Dress":          {"suggestion": "A little black dress is the ultimate one-and-done outfit for events.", "combo_boost": 4},
    "Casual Top":            {"suggestion": "A neutral white or grey t-shirt pairs with almost everything.", "combo_boost": 6},
    "Casual Bottom":         {"suggestion": "Dark jeans bridge casual and smart-casual effortlessly.", "combo_boost": 6},
    "Casual Footwear":       {"suggestion": "White sneakers are the single most versatile casual shoe.", "combo_boost": 8},
    "Casual Outerwear":      {"suggestion": "A denim jacket or neutral hoodie layers over any casual look.", "combo_boost": 5},
    "Casual Dress":          {"suggestion": "A floral or solid midi dress is perfect for warm-weather outings.", "combo_boost": 3},
    "Smart Casual Top":      {"suggestion": "A linen shirt or polo keeps you polished without being overdressed.", "combo_boost": 5},
    "Smart Casual Bottom":   {"suggestion": "Chinos in beige or olive work for work-to-weekend transitions.", "combo_boost": 5},
    "Smart Casual Footwear": {"suggestion": "Loafers or clean white trainers complete a smart casual look effortlessly.", "combo_boost": 4},
    "Ethnic Top":            {"suggestion": "A printed kurti covers festive, casual, and semi-formal occasions.", "combo_boost": 4},
    "Ethnic Bottom":         {"suggestion": "A palazzo or salwar pairs with most kurtis for instant ethnic looks.", "combo_boost": 4},
    "Ethnic Outfit":         {"suggestion": "A saree or salwar suit is essential for Indian weddings and festivals.", "combo_boost": 3},
    "Ethnic Footwear":       {"suggestion": "Juttis or kolhapuris complete ethnic looks and are very versatile.", "combo_boost": 3},
    "Activewear Top":        {"suggestion": "A breathable sports top keeps you ready for workouts or morning walks.", "combo_boost": 3},
    "Activewear Bottom":     {"suggestion": "Leggings or shorts are a must-have for any active lifestyle.", "combo_boost": 3},
    "Activewear Footwear":   {"suggestion": "A proper pair of running shoes protects your feet and boosts performance.", "combo_boost": 2},
    "Loungewear":            {"suggestion": "A comfortable co-ord or pyjama set makes evenings at home much better.", "combo_boost": 2},
    "Belt":                  {"suggestion": "A leather belt in black or brown finishes off formal and smart casual looks.", "combo_boost": 4},
    "Casual Bag":            {"suggestion": "A tote or backpack keeps your everyday outfits practical and put-together.", "combo_boost": 3},
    "Formal Bag":            {"suggestion": "A structured handbag elevates any formal or smart casual outfit.", "combo_boost": 3},
    "Sunglasses":            {"suggestion": "A classic pair of sunglasses instantly upgrades any outdoor look.", "combo_boost": 3},
    "Watch":                 {"suggestion": "An everyday watch adds polish to both casual and smart casual outfits.", "combo_boost": 4},
    "Scarf / Dupatta":       {"suggestion": "A dupatta or printed scarf can transform a simple outfit into a full ethnic look.", "combo_boost": 3},
}


def calculate_combinations(wardrobe: list) -> int:
    tops     = sum(1 for i in wardrobe if i.get("category") == "Top")
    bottoms  = sum(1 for i in wardrobe if i.get("category") == "Bottom")
    footwear = sum(1 for i in wardrobe if i.get("category") == "Footwear")
    return max(tops, 1) * max(bottoms, 1) * max(footwear, 1)


def detect_gaps(wardrobe: list) -> dict:
    category_counts = Counter(item.get("category", "") for item in wardrobe)
    missing_items   = []
    gap_suggestions = []
    potential_boost = 0

    for essential_key, essential in WARDROBE_ESSENTIALS.items():
        has_item = any(
            item.get("category") == essential["category"]
            and item.get("style") == essential["style"]
            for item in wardrobe
        )
        if not has_item:
            missing_items.append(essential["label"])
            if essential_key in GAP_SUGGESTIONS:
                gap_info = GAP_SUGGESTIONS[essential_key]
                gap_suggestions.append({
                    "key":        essential_key,
                    "label":      essential["label"],
                    "suggestion": gap_info["suggestion"],
                    "combo_boost": gap_info["combo_boost"],
                })
                potential_boost += gap_info["combo_boost"]

    current_combos   = calculate_combinations(wardrobe)
    potential_combos = current_combos + potential_boost

    return {
        "missing_items":                   missing_items,
        "gap_suggestions":                 gap_suggestions,
        "combination_count":               current_combos,
        "potential_combos_with_gaps_filled": potential_combos,
        "category_counts":                 dict(category_counts),
    }


def render_gap_report(wardrobe: list):
    if not wardrobe:
        st.info("Add items to your wardrobe to see your gap analysis.")
        return

    gaps = detect_gaps(wardrobe)

    st.markdown(
        """
        <h2 style="font-weight: 700; margin-bottom: 4px;">🔍 Wardrobe Gap Analysis</h2>
        <p style="color: #6b7280; margin-bottom: 20px;">
            What's missing from your wardrobe — and what it's costing you in outfit combinations.
        </p>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div style="background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.25);
                border-radius:12px;padding:20px;text-align:center;">
                <p style="color:#9ca3af;font-size:0.8rem;margin:0 0 4px;">Current outfit combinations</p>
                <h2 style="font-size:2.2rem;font-weight:700;color:#a78bfa;margin:0;">{gaps['combination_count']}</h2>
            </div>""",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);
                border-radius:12px;padding:20px;text-align:center;">
                <p style="color:#9ca3af;font-size:0.8rem;margin:0 0 4px;">Potential with gaps filled</p>
                <h2 style="font-size:2.2rem;font-weight:700;color:#10b981;margin:0;">{gaps['potential_combos_with_gaps_filled']}</h2>
            </div>""",
            unsafe_allow_html=True
        )

    st.write("")
    st.markdown("<p style='font-weight:600;color:#e5e7eb;margin-bottom:10px;'>Wardrobe essentials checklist</p>", unsafe_allow_html=True)

    checklist_html = ""
    for essential_key, essential in WARDROBE_ESSENTIALS.items():
        has_item = any(
            item.get("category") == essential["category"]
            and item.get("style") == essential["style"]
            for item in wardrobe
        )
        icon  = "✅" if has_item else "❌"
        color = "#10b981" if has_item else "#ef4444"
        checklist_html += f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 0;
            border-bottom:1px solid rgba(255,255,255,0.05);font-size:0.9rem;">
            <span>{icon}</span>
            <span style="color:#d1d5db;">{essential['label']}</span>
        </div>"""
    st.markdown(checklist_html, unsafe_allow_html=True)

    if gaps["gap_suggestions"]:
        st.write("")
        st.markdown("<p style='font-weight:600;color:#e5e7eb;margin-bottom:10px;'>💡 Stylist recommendations</p>", unsafe_allow_html=True)
        for gap in gaps["gap_suggestions"][:5]:
            st.markdown(
                f"""
                <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
                    border-left:3px solid #a78bfa;border-radius:0 8px 8px 0;padding:12px 16px;margin-bottom:10px;">
                    <p style="color:#e5e7eb;font-size:0.9rem;margin:0 0 4px;">{gap['suggestion']}</p>
                    <p style="color:#10b981;font-size:0.8rem;margin:0;">+{gap['combo_boost']} new outfit combinations unlocked</p>
                </div>""",
                unsafe_allow_html=True
            )
    else:
        st.success("Your wardrobe has all the essentials covered! You're well-equipped for any occasion.")