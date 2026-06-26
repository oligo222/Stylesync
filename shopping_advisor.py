"""
StyleSync Smart Shopping Advisor

Analyzes wardrobe gaps and generates one-click shopping links
across Indian fashion platforms.
"""
import urllib.parse
import streamlit as st

# Shopping platforms with their search URL patterns
PLATFORMS = {
    "Myntra": {
        "url": "https://www.myntra.com/{query}",
        "color": "#FF3F6C",
        "icon": "🛍️",
    },
    "Ajio": {
        "url": "https://www.ajio.com/search/?text={query}",
        "color": "#E8611A",
        "icon": "🧡",
    },
    "Amazon Fashion": {
        "url": "https://www.amazon.in/s?k={query}&rh=n%3A1571271031",
        "color": "#FF9900",
        "icon": "📦",
    },
    "Flipkart": {
        "url": "https://www.flipkart.com/search?q={query}&otracker=search",
        "color": "#2874F0",
        "icon": "🔵",
    },
    "Nykaa Fashion": {
        "url": "https://www.nykaafashion.com/search?q={query}",
        "color": "#FC2779",
        "icon": "💗",
    },
}

# Specific search terms per gap type — tuned for Indian fashion sites
SHOPPING_QUERIES = {
    "Formal Outerwear": {
        "search_term": "women black blazer formal",
        "display_name": "Black Blazer",
        "price_range": "₹800 – ₹3,500",
        "why": "A black blazer unlocks the most outfit combinations of any single purchase.",
        "combos": 8,
        "tags": ["Workwear", "Interviews", "Dinner dates"],
    },
    "Formal Top": {
        "search_term": "women white formal shirt office",
        "display_name": "White Formal Shirt",
        "price_range": "₹400 – ₹1,800",
        "why": "A crisp white shirt is the single most versatile formal item you can own.",
        "combos": 5,
        "tags": ["Office", "Formal events", "Smart casual"],
    },
    "Formal Bottom": {
        "search_term": "women black formal trousers office",
        "display_name": "Black Formal Trousers",
        "price_range": "₹600 – ₹2,500",
        "why": "Tailored black trousers work for every formal occasion — day or night.",
        "combos": 7,
        "tags": ["Office", "Events", "Formal dinners"],
    },
    "Formal Footwear": {
        "search_term": "women black heels formal office",
        "display_name": "Black Heels / Formal Shoes",
        "price_range": "₹500 – ₹2,000",
        "why": "Classic black formal footwear ties together any professional outfit.",
        "combos": 5,
        "tags": ["Office", "Weddings", "Formal events"],
    },
    "Casual Top": {
        "search_term": "women white t-shirt casual basic",
        "display_name": "White / Grey Basic T-Shirt",
        "price_range": "₹200 – ₹800",
        "why": "A neutral basic tee pairs with literally everything in your wardrobe.",
        "combos": 6,
        "tags": ["Everyday", "Weekend", "Layering"],
    },
    "Casual Bottom": {
        "search_term": "women dark blue jeans casual",
        "display_name": "Dark Blue / Black Jeans",
        "price_range": "₹600 – ₹2,500",
        "why": "Dark jeans bridge casual and smart-casual — the most wearable bottom you can buy.",
        "combos": 6,
        "tags": ["Weekend", "Casual outings", "Smart casual"],
    },
    "Casual Footwear": {
        "search_term": "women white sneakers casual",
        "display_name": "White Sneakers",
        "price_range": "₹500 – ₹2,500",
        "why": "White sneakers are the single most versatile casual shoe — pairs with everything.",
        "combos": 8,
        "tags": ["Everyday", "Weekend", "Travel"],
    },
}


def build_search_url(platform_name: str, search_term: str) -> str:
    """Builds a search URL for the given platform and search term."""
    platform = PLATFORMS[platform_name]
    encoded = urllib.parse.quote_plus(search_term)
    return platform["url"].replace("{query}", encoded)


def get_shopping_recommendations(wardrobe: list) -> list:
    """
    Detects wardrobe gaps and returns shopping recommendations with links.
    """
    from gap_detector import WARDROBE_ESSENTIALS

    recommendations = []

    for essential_key, essential in WARDROBE_ESSENTIALS.items():
        has_item = any(
            item.get("category") == essential["category"]
            and item.get("style") == essential["style"]
            for item in wardrobe
        )
        if not has_item and essential_key in SHOPPING_QUERIES:
            query_info = SHOPPING_QUERIES[essential_key]
            links = {
                platform: build_search_url(platform, query_info["search_term"])
                for platform in PLATFORMS
            }
            recommendations.append({
                "essential_key": essential_key,
                "display_name": query_info["display_name"],
                "price_range": query_info["price_range"],
                "why": query_info["why"],
                "combos": query_info["combos"],
                "tags": query_info["tags"],
                "search_term": query_info["search_term"],
                "links": links,
            })

    return recommendations


def render_shopping_advisor(wardrobe: list):
    """
    Renders the Smart Shopping Advisor section in Streamlit.
    """
    st.markdown(
        """
        <h2 style="font-weight: 700; margin-bottom: 4px;">🛒 Smart Shopping Advisor</h2>
        <p style="color: #6b7280; margin-bottom: 8px;">
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
            <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25);
                border-radius: 12px; padding: 20px; text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 8px;">🎉</div>
                <p style="color: #10b981; font-weight: 600; margin: 0;">
                    Your wardrobe is complete! No essential gaps detected.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # Summary bar
    total_combos = sum(r["combos"] for r in recommendations)
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(167,139,250,0.15), rgba(167,139,250,0.05));
            border: 1px solid rgba(167,139,250,0.3);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 16px;
        ">
            <div style="font-size: 2rem;">🧠</div>
            <div>
                <p style="color: #a78bfa; font-weight: 600; margin: 0 0 2px;">
                    {len(recommendations)} smart purchases identified
                </p>
                <p style="color: #9ca3af; font-size: 0.85rem; margin: 0;">
                    These additions would unlock <strong style="color:#10b981;">+{total_combos} new outfit combinations</strong> from clothes you already own.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # One card per recommendation
    for i, rec in enumerate(recommendations):
        tags_html = "".join(
            f'<span style="background: rgba(255,255,255,0.06); color: #9ca3af; '
            f'font-size: 0.75rem; padding: 2px 8px; border-radius: 999px; '
            f'border: 1px solid rgba(255,255,255,0.1);">{tag}</span>'
            for tag in rec["tags"]
        )

        with st.container(border=True):
            col_left, col_right = st.columns([3, 1])
            with col_left:
                st.markdown(f"**{rec['display_name']}**")
                st.markdown(tags_html, unsafe_allow_html=True)
                st.caption(rec['why'])
                st.markdown(f"✨ Unlocks **+{rec['combos']}** new outfit combinations")
            with col_right:
                st.markdown(
                    f'<div style="text-align:right;color:#10b981;font-weight:700;">{rec["price_range"]}</div>'
                    f'<div style="text-align:right;color:#6b7280;font-size:0.75rem;">estimated range</div>',
                    unsafe_allow_html=True
                )

        # Shopping links as buttons
        st.markdown(
            "<p style='color: #6b7280; font-size: 0.8rem; margin: -8px 0 8px;'>Shop now — compare prices:</p>",
            unsafe_allow_html=True
        )

        cols = st.columns(len(PLATFORMS))
        for col, (platform_name, url) in zip(cols, rec["links"].items()):
            platform = PLATFORMS[platform_name]
            with col:
                st.link_button(
                    f"{platform['icon']} {platform_name}",
                    url,
                    use_container_width=True,
                )

        st.write("")