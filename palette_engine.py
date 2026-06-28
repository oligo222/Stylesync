"""
StyleSync Palette Engine

Extracts color palette from wardrobe and generates a style profile.
"""
import streamlit as st
from collections import Counter

COLOR_FAMILIES = {
    "Neutrals": ["white", "ivory", "cream", "beige", "camel", "off white", "eggshell"],
    "Darks": ["black", "charcoal", "dark grey", "dark gray", "onyx"],
    "Blues": ["navy", "blue", "light blue", "denim", "cobalt", "royal blue", "sky blue"],
    "Earthy": ["tan", "brown", "camel", "khaki", "rust", "terracotta", "olive", "sand"],
    "Muted": ["grey", "gray", "dusty pink", "mauve", "sage", "muted green", "lilac"],
    "Bold/Bright": ["red", "yellow", "multicolor", "orange", "hot pink", "green", "purple", "pink"],
}

# Map color display names to hex for swatches
COLOR_HEX = {
    "black": "#1a1a1a",
    "white": "#f8f8f8",
    "navy": "#1e3a5f",
    "blue": "#3b82f6",
    "light blue": "#93c5fd",
    "grey": "#9ca3af",
    "gray": "#9ca3af",
    "beige": "#d4b896",
    "ivory": "#fffff0",
    "cream": "#fffdd0",
    "camel": "#c19a6b",
    "tan": "#d2b48c",
    "red": "#ef4444",
    "multicolor": "linear-gradient(135deg, #ef4444, #3b82f6, #10b981)",
    "brown": "#92400e",
    "green": "#10b981",
    "yellow": "#f59e0b",
    "orange": "#f97316",
    "pink": "#ec4899",
    "purple": "#8b5cf6",
    "charcoal": "#374151",
}

STYLE_PROFILES = {
    "Minimal Urban": {
        "condition": lambda f: f.get("Neutrals", 0) + f.get("Darks", 0) >= 50,
        "description": "Clean lines, neutral tones, effortless sophistication.",
        "icon": "🤍"
    },
    "Classic Coastal": {
        "condition": lambda f: f.get("Blues", 0) >= 25 and f.get("Neutrals", 0) >= 20,
        "description": "Navy and neutrals — timeless, polished, relaxed.",
        "icon": "🌊"
    },
    "Dark Romantic": {
        "condition": lambda f: f.get("Darks", 0) >= 40,
        "description": "Moody, dramatic, and effortlessly editorial.",
        "icon": "🖤"
    },
    "Warm Naturalist": {
        "condition": lambda f: f.get("Earthy", 0) >= 30,
        "description": "Earth tones, organic textures, grounded style.",
        "icon": "🍂"
    },
    "Statement Maker": {
        "condition": lambda f: f.get("Bold/Bright", 0) >= 30,
        "description": "Bold colors, expressive choices, unapologetic style.",
        "icon": "🔥"
    },
    "Eclectic Explorer": {
        "condition": lambda f: True,  # fallback
        "description": "A rich mix of styles — adventurous and versatile.",
        "icon": "🌈"
    },
}


def extract_palette(wardrobe: list) -> dict:
    """
    Analyzes wardrobe colors and returns palette data.
    """
    color_counts = Counter()
    for item in wardrobe:
        color = item.get("color", "").strip()
        if color:
            color_counts[color] += 1

    total = sum(color_counts.values()) or 1

    # Map to families
    family_counts = {family: 0 for family in COLOR_FAMILIES}
    for color, count in color_counts.items():
        color_lower = color.lower()
        matched = False
        for family, members in COLOR_FAMILIES.items():
            if color_lower in members:
                family_counts[family] += count
                matched = True
                break
        if not matched:
            family_counts["Muted"] += count  # default bucket

    family_percentages = {
        family: round((count / total) * 100)
        for family, count in family_counts.items()
        if count > 0
    }

    top_3 = [color for color, _ in color_counts.most_common(3)]
    dominant_family = max(family_counts, key=family_counts.get) if family_counts else "Neutrals"

    return {
        "color_counts": dict(color_counts),
        "family_percentages": family_percentages,
        "dominant_family": dominant_family,
        "top_3_colors": top_3,
    }


def get_style_profile(family_percentages: dict) -> tuple:
    """
    Returns (profile_name, profile_dict) based on family percentages.
    """
    for name, profile in STYLE_PROFILES.items():
        if profile["condition"](family_percentages):
            return name, profile
    return "Eclectic Explorer", STYLE_PROFILES["Eclectic Explorer"]


def render_palette_card(wardrobe: list):
    """
    Renders the color palette analysis section in Streamlit.
    """
    if not wardrobe:
        st.info("Add items to your wardrobe to see your color palette.")
        return

    palette = extract_palette(wardrobe)
    profile_name, profile = get_style_profile(palette["family_percentages"])

    st.markdown(
        """
        <h2 style="font-weight: 700; margin-bottom: 4px;">🎨 Your Color Palette</h2>
        <p style="color: #6b7280; margin-bottom: 20px;">
            A breakdown of your wardrobe's color story.
        </p>
        """,
        unsafe_allow_html=True
    )

    # Style profile hero
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(167,139,250,0.15), rgba(167,139,250,0.05));
            border: 1px solid rgba(167,139,250,0.3);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            text-align: center;
        ">
            <div style="font-size: 2.5rem; margin-bottom: 8px;">{profile['icon']}</div>
            <p style="color: #9ca3af; font-size: 0.85rem; margin: 0 0 4px;">Your style profile</p>
            <h2 style="font-size: 1.8rem; font-weight: 700; color: #a78bfa; margin: 0 0 8px;">
                {profile_name}
            </h2>
            <p style="color: #d1d5db; font-size: 0.95rem; margin: 0;">
                {profile['description']}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Color swatches — top 5 colors using native columns
    top_colors = list(palette["color_counts"].items())[:5]
    swatch_cols = st.columns(len(top_colors)) if top_colors else []
    for col, (color, count) in zip(swatch_cols, top_colors):
        hex_val = COLOR_HEX.get(color.lower(), "#888888")
        with col:
            st.markdown(
                f'<div style="width:48px;height:48px;border-radius:50%;background:{hex_val};'
                f'border:2px solid rgba(255,255,255,0.2);margin:0 auto 4px;"></div>'
                f'<div style="font-size:0.7rem;color:#9ca3af;text-align:center;">{color}</div>'
                f'<div style="font-size:0.65rem;color:#6b7280;text-align:center;">{count} items</div>',
                unsafe_allow_html=True
            )

    # Family breakdown bars
    st.markdown("<p style='color: #9ca3af; font-size: 0.85rem; margin-bottom: 8px;'>Wardrobe breakdown by color family</p>", unsafe_allow_html=True)
    sorted_families = sorted(palette["family_percentages"].items(), key=lambda x: x[1], reverse=True)
    for family, pct in sorted_families:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(pct / 100, text=family)
        with col2:
            st.markdown(f"<p style='text-align:right; color:#a78bfa; font-weight:600; padding-top:6px;'>{pct}%</p>", unsafe_allow_html=True)