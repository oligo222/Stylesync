"""
StyleSync Smart Shopping Advisor

Analyzes wardrobe gaps and generates one-click shopping links
across Indian fashion platforms.
"""
import urllib.parse
import streamlit as st

PLATFORMS = {
    "Myntra":        {"url": "https://www.myntra.com/{query}",                              "color": "#FF3F6C", "icon": "🛍️"},
    "Ajio":          {"url": "https://www.ajio.com/search/?text={query}",                   "color": "#E8611A", "icon": "🧡"},
    "Amazon Fashion":{"url": "https://www.amazon.in/s?k={query}&rh=n%3A1571271031",         "color": "#FF9900", "icon": "📦"},
    "Flipkart":      {"url": "https://www.flipkart.com/search?q={query}&otracker=search",   "color": "#2874F0", "icon": "🔵"},
    "Nykaa Fashion": {"url": "https://www.nykaafashion.com/search?q={query}",               "color": "#FC2779", "icon": "💗"},
}

SHOPPING_QUERIES = {
    # Formal
    "Formal Outerwear":      {"search_term": "women black blazer formal",             "display_name": "Black Blazer",                  "price_range": "₹800 – ₹3,500",  "why": "A black blazer unlocks the most outfit combinations of any single purchase.",           "combos": 8,  "tags": ["Workwear", "Interviews", "Dinner dates"]},
    "Formal Top":            {"search_term": "women white formal shirt office",       "display_name": "White Formal Shirt",            "price_range": "₹400 – ₹1,800",  "why": "A crisp white shirt is the single most versatile formal item you can own.",            "combos": 5,  "tags": ["Office", "Formal events", "Smart casual"]},
    "Formal Bottom":         {"search_term": "women black formal trousers office",    "display_name": "Black Formal Trousers",         "price_range": "₹600 – ₹2,500",  "why": "Tailored black trousers work for every formal occasion — day or night.",             "combos": 7,  "tags": ["Office", "Events", "Formal dinners"]},
    "Formal Footwear":       {"search_term": "women black heels formal office",       "display_name": "Black Heels / Formal Shoes",    "price_range": "₹500 – ₹2,000",  "why": "Classic black formal footwear ties together any professional outfit.",               "combos": 5,  "tags": ["Office", "Weddings", "Formal events"]},
    "Formal Dress":          {"search_term": "women little black dress formal",       "display_name": "Little Black Dress",            "price_range": "₹700 – ₹3,000",  "why": "A little black dress is the ultimate one-and-done outfit for events and dinners.",    "combos": 4,  "tags": ["Events", "Dinners", "Cocktail parties"]},
    # Casual
    "Casual Top":            {"search_term": "women white t-shirt casual basic",      "display_name": "White / Grey Basic T-Shirt",    "price_range": "₹200 – ₹800",    "why": "A neutral basic tee pairs with literally everything in your wardrobe.",              "combos": 6,  "tags": ["Everyday", "Weekend", "Layering"]},
    "Casual Bottom":         {"search_term": "women dark blue jeans casual",          "display_name": "Dark Blue / Black Jeans",       "price_range": "₹600 – ₹2,500",  "why": "Dark jeans bridge casual and smart-casual — the most wearable bottom you can buy.", "combos": 6,  "tags": ["Weekend", "Casual outings", "Smart casual"]},
    "Casual Footwear":       {"search_term": "women white sneakers casual",           "display_name": "White Sneakers",                "price_range": "₹500 – ₹2,500",  "why": "White sneakers are the single most versatile casual shoe — pairs with everything.",  "combos": 8,  "tags": ["Everyday", "Weekend", "Travel"]},
    "Casual Outerwear":      {"search_term": "women denim jacket casual",             "display_name": "Denim Jacket / Hoodie",         "price_range": "₹600 – ₹2,500",  "why": "A denim jacket or hoodie layers perfectly over any casual outfit.",                 "combos": 5,  "tags": ["Weekend", "Layering", "Travel"]},
    "Casual Dress":          {"search_term": "women casual midi dress summer",        "display_name": "Casual Midi Dress",             "price_range": "₹400 – ₹1,800",  "why": "A floral or solid midi dress is effortless for warm-weather outings.",             "combos": 3,  "tags": ["Brunch", "Outings", "Summer"]},
    # Smart Casual
    "Smart Casual Top":      {"search_term": "women linen shirt smart casual",        "display_name": "Linen / Polo Shirt",            "price_range": "₹400 – ₹1,800",  "why": "A linen shirt keeps you polished without being overdressed.",                       "combos": 5,  "tags": ["Brunch", "Casual office", "Dates"]},
    "Smart Casual Bottom":   {"search_term": "women beige chinos trousers",           "display_name": "Chinos / Smart Trousers",       "price_range": "₹500 – ₹2,000",  "why": "Chinos in beige or olive work for work-to-weekend transitions.",                    "combos": 5,  "tags": ["Office casual", "Outings", "Dates"]},
    "Smart Casual Footwear": {"search_term": "women loafers smart casual",            "display_name": "Loafers / Clean Trainers",      "price_range": "₹600 – ₹2,500",  "why": "Loafers or clean trainers complete a smart casual look effortlessly.",             "combos": 4,  "tags": ["Office casual", "Weekend", "Dates"]},
    # Ethnic
    "Ethnic Top":            {"search_term": "women printed kurti ethnic casual",     "display_name": "Printed Kurti",                 "price_range": "₹300 – ₹1,500",  "why": "A printed kurti covers festive, casual, and semi-formal occasions.",               "combos": 4,  "tags": ["Festivals", "Casual ethnic", "Family events"]},
    "Ethnic Bottom":         {"search_term": "women palazzo salwar ethnic",           "display_name": "Palazzo / Salwar",              "price_range": "₹300 – ₹1,200",  "why": "A palazzo or salwar pairs with most kurtis for instant ethnic looks.",             "combos": 4,  "tags": ["Festivals", "Ethnic occasions", "Comfort"]},
    "Ethnic Outfit":         {"search_term": "women salwar suit ethnic festive",      "display_name": "Salwar Suit / Saree",           "price_range": "₹800 – ₹5,000",  "why": "A saree or salwar suit is essential for Indian weddings and festivals.",           "combos": 3,  "tags": ["Weddings", "Festivals", "Pujas"]},
    "Ethnic Footwear":       {"search_term": "women juttis ethnic footwear",          "display_name": "Juttis / Kolhapuris",           "price_range": "₹300 – ₹1,500",  "why": "Juttis or kolhapuris complete ethnic looks and go with most kurtas.",             "combos": 3,  "tags": ["Ethnic", "Festivals", "Casual ethnic"]},
    # Activewear
    "Activewear Top":        {"search_term": "women sports tshirt activewear gym",    "display_name": "Sports T-Shirt / Tank Top",     "price_range": "₹200 – ₹1,000",  "why": "A breathable sports top keeps you ready for workouts or morning walks.",           "combos": 3,  "tags": ["Gym", "Morning walks", "Yoga"]},
    "Activewear Bottom":     {"search_term": "women gym leggings activewear",         "display_name": "Gym Leggings / Shorts",         "price_range": "₹300 – ₹1,500",  "why": "Leggings or shorts are a must-have for any active lifestyle.",                     "combos": 3,  "tags": ["Gym", "Running", "Yoga"]},
    "Activewear Footwear":   {"search_term": "women running shoes sports",            "display_name": "Running / Sports Shoes",        "price_range": "₹800 – ₹4,000",  "why": "A proper pair of running shoes protects your feet and boosts performance.",         "combos": 2,  "tags": ["Running", "Gym", "Sports"]},
    "Loungewear":            {"search_term": "women pyjama set loungewear co-ord",    "display_name": "Pyjama / Loungewear Co-ord",    "price_range": "₹300 – ₹1,200",  "why": "A comfortable co-ord or pyjama set makes evenings at home much better.",           "combos": 2,  "tags": ["Home", "Lounging", "Sleep"]},
    # Accessories
    "Belt":                  {"search_term": "women leather belt black formal",       "display_name": "Leather Belt (Black / Brown)",  "price_range": "₹200 – ₹800",    "why": "A leather belt finishes off formal and smart casual looks cleanly.",               "combos": 4,  "tags": ["Formal", "Smart casual", "Office"]},
    "Casual Bag":            {"search_term": "women tote bag casual everyday",        "display_name": "Tote Bag / Backpack",           "price_range": "₹400 – ₹2,000",  "why": "A tote or backpack keeps everyday outfits practical and put-together.",            "combos": 3,  "tags": ["Everyday", "College", "Travel"]},
    "Formal Bag":            {"search_term": "women structured handbag formal",       "display_name": "Structured Handbag",            "price_range": "₹600 – ₹3,000",  "why": "A structured handbag elevates any formal or smart casual outfit instantly.",       "combos": 3,  "tags": ["Office", "Events", "Formal"]},
    "Sunglasses":            {"search_term": "women sunglasses UV protection fashion","display_name": "Sunglasses",                    "price_range": "₹200 – ₹1,500",  "why": "A classic pair of sunglasses instantly upgrades any outdoor look.",               "combos": 3,  "tags": ["Outdoor", "Travel", "Everyday"]},
    "Watch":                 {"search_term": "women watch everyday casual elegant",   "display_name": "Everyday Watch",               "price_range": "₹500 – ₹3,000",  "why": "An everyday watch adds polish to both casual and smart casual outfits.",           "combos": 4,  "tags": ["Everyday", "Office", "Smart casual"]},
    "Scarf / Dupatta":       {"search_term": "women dupatta scarf ethnic printed",    "display_name": "Dupatta / Printed Scarf",       "price_range": "₹150 – ₹800",    "why": "A dupatta or printed scarf can transform a simple outfit into a full ethnic look.", "combos": 3,  "tags": ["Ethnic", "Festivals", "Layering"]},
}


def build_search_url(platform_name: str, search_term: str) -> str:
    platform = PLATFORMS[platform_name]
    encoded  = urllib.parse.quote_plus(search_term)
    return platform["url"].replace("{query}", encoded)


def get_shopping_recommendations(wardrobe: list) -> list:
    from gap_detector import WARDROBE_ESSENTIALS
    recommendations = []
    for essential_key, essential in WARDROBE_ESSENTIALS.items():
        has_item = any(
            item.get("category") == essential["category"]
            and item.get("style") == essential["style"]
            for item in wardrobe
        )
        if not has_item and essential_key in SHOPPING_QUERIES:
            q = SHOPPING_QUERIES[essential_key]
            links = {p: build_search_url(p, q["search_term"]) for p in PLATFORMS}
            recommendations.append({
                "essential_key": essential_key,
                "display_name":  q["display_name"],
                "price_range":   q["price_range"],
                "why":           q["why"],
                "combos":        q["combos"],
                "tags":          q["tags"],
                "search_term":   q["search_term"],
                "links":         links,
            })
    return recommendations


def render_shopping_advisor(wardrobe: list):
    st.markdown(
        """
        <h2 style="font-weight:700;margin-bottom:4px;">🛒 Smart Shopping Advisor</h2>
        <p style="color:#6b7280;margin-bottom:8px;">
            Based on your wardrobe gaps — exactly what to buy and where to find it cheaper.
        </p>
        """,
        unsafe_allow_html=True
    )

    if not wardrobe:
        st.info("Add items to your wardrobe to get shopping recommendations.")
        return

    recommendations = get_shopping_recommendations(wardrobe)

    if not recommendations:
        st.markdown(
            """
            <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);
                border-radius:12px;padding:20px;text-align:center;">
                <div style="font-size:2rem;margin-bottom:8px;">🎉</div>
                <p style="color:#10b981;font-weight:600;margin:0;">
                    Your wardrobe is complete! No essential gaps detected.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    total_combos = sum(r["combos"] for r in recommendations)
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,rgba(167,139,250,0.15),rgba(167,139,250,0.05));
            border:1px solid rgba(167,139,250,0.3);border-radius:12px;padding:16px 20px;
            margin-bottom:24px;display:flex;align-items:center;gap:16px;">
            <div style="font-size:2rem;">🧠</div>
            <div>
                <p style="color:#a78bfa;font-weight:600;margin:0 0 2px;">
                    {len(recommendations)} smart purchases identified
                </p>
                <p style="color:#9ca3af;font-size:0.85rem;margin:0;">
                    These additions would unlock <strong style="color:#10b981;">+{total_combos} new outfit combinations</strong> from clothes you already own.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    for rec in recommendations:
        tags_html = "".join(
            f'<span style="background:rgba(255,255,255,0.06);color:#9ca3af;font-size:0.75rem;'
            f'padding:2px 8px;border-radius:999px;border:1px solid rgba(255,255,255,0.1);">{tag}</span> '
            for tag in rec["tags"]
        )

        with st.container(border=True):
            col_left, col_right = st.columns([3, 1])
            with col_left:
                st.markdown(f"**{rec['display_name']}**")
                st.markdown(tags_html, unsafe_allow_html=True)
                st.caption(rec["why"])
                st.markdown(f"✨ Unlocks **+{rec['combos']}** new outfit combinations")
            with col_right:
                st.markdown(
                    f'<div style="text-align:right;color:#10b981;font-weight:700;">{rec["price_range"]}</div>'
                    f'<div style="text-align:right;color:#6b7280;font-size:0.75rem;">estimated range</div>',
                    unsafe_allow_html=True
                )

        st.markdown(
            "<p style='color:#6b7280;font-size:0.8rem;margin:-8px 0 8px;'>Shop now — compare prices:</p>",
            unsafe_allow_html=True
        )
        cols = st.columns(len(PLATFORMS))
        for col, (platform_name, url) in zip(cols, rec["links"].items()):
            with col:
                st.link_button(
                    f"{PLATFORMS[platform_name]['icon']} {platform_name}",
                    url,
                    use_container_width=True,
                )
        st.write("")