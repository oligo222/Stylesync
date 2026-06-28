"""
StyleSync Revival Engine
"""
import os
import streamlit as st

COLOR_PAIRINGS = {
    "black": ["white", "ivory", "cream", "beige", "camel", "grey", "navy", "red", "multicolor"],
    "white": ["black", "navy", "blue", "camel", "tan", "beige", "multicolor"],
    "navy": ["white", "ivory", "cream", "beige", "camel", "tan", "grey"],
    "blue": ["white", "beige", "camel", "grey", "tan"],
    "beige": ["black", "navy", "white", "brown", "camel", "tan"],
    "grey": ["black", "white", "navy", "blue", "burgundy"],
    "camel": ["white", "black", "navy", "cream", "ivory"],
    "ivory": ["black", "navy", "camel", "tan", "brown"],
    "cream": ["black", "navy", "camel", "brown"],
    "tan": ["white", "navy", "black", "cream"],
    "multicolor": ["black", "white", "navy", "beige"],
    "light blue": ["white", "beige", "camel", "grey"],
    "teal": ["white", "black", "beige", "grey"],
}

def get_forgotten_items(wardrobe, history):
    used_items = history.get("used_items", [])
    worn_set = {name.lower().strip() for name in used_items if isinstance(name, str)}
    never_worn, worn_before = [], []
    for item in wardrobe:
        item_name = (item.get("item") or item.get("garment_type") or
                     f"{item.get('color', '')} {item.get('category', '')}".strip() or "Unknown Item")
        times_worn = sum(1 for e in used_items
                         if isinstance(e, str) and e.lower().strip() == item_name.lower().strip())
        entry = {**item, "item": item_name, "times_worn": times_worn}
        if item_name.lower().strip() not in worn_set:
            entry["days_since_worn"] = 999
            entry["worn_label"] = "Never worn"
            never_worn.append(entry)
        else:
            entry["days_since_worn"] = times_worn
            entry["worn_label"] = f"Worn {times_worn}x"
            worn_before.append(entry)
    worn_before.sort(key=lambda x: x["times_worn"])
    return never_worn + worn_before

def generate_revival_outfits(forgotten_item, wardrobe):
    item_color = forgotten_item.get("color", "").lower()
    item_category = forgotten_item.get("category", "")
    item_style = forgotten_item.get("style", "")
    item_name = forgotten_item.get("item", "")
    compatible_colors = COLOR_PAIRINGS.get(item_color, [])

    def is_compatible(candidate):
        if candidate.get("item") == item_name: return False
        if candidate.get("category") == item_category: return False
        cc = candidate.get("color", "").lower()
        if cc == "multicolor" and item_color == "multicolor": return False
        return cc in compatible_colors or cc in ["black", "white", "beige", "grey", "navy"]

    suggestions, used = [], set()
    for category in [c for c in ["Top", "Bottom", "Footwear", "Outerwear"] if c != item_category]:
        candidates = [i for i in wardrobe if i.get("category") == category and is_compatible(i)]
        pool = [c for c in candidates if c.get("style") == item_style] or candidates
        for candidate in pool:
            cname = candidate.get("item") or candidate.get("garment_type", "")
            if cname not in used:
                used.add(cname)
                suggestions.append({"item": cname, "category": candidate.get("category"), "color": candidate.get("color")})
                break

    outfits = []
    if len(suggestions) >= 2:
        outfits.append({"pieces": [suggestions[0], suggestions[1]], "label": "Clean & classic"})
    if len(suggestions) >= 3:
        outfits.append({"pieces": [suggestions[0], suggestions[2]], "label": "Elevated everyday"})
        outfits.append({"pieces": [suggestions[1], suggestions[2]], "label": "Fresh pairing"})
    elif len(suggestions) == 1:
        outfits.append({"pieces": [suggestions[0]], "label": "Simple pairing"})
    return outfits[:3]

def get_revival_gemini_prompt(forgotten_item, wardrobe):
    item_name = forgotten_item.get("item", "this item")
    item_color = forgotten_item.get("color", "")
    item_category = forgotten_item.get("category", "")
    item_style = forgotten_item.get("style", "")
    worn_label = forgotten_item.get("worn_label", "rarely worn")
    wardrobe_summary = ", ".join(
        f"{i.get('color')} {i.get('category')}" for i in wardrobe[:10] if i.get("item") != item_name
    )
    return f"""You are StyleSync, a personal AI stylist. Help rediscover a forgotten wardrobe item.

The user has a {item_color} {item_category} called "{item_name}" ({item_style} style). It has been {worn_label}.
Their wardrobe includes: {wardrobe_summary}.

Give exactly 3 specific, creative outfit suggestions using this item. Each suggestion should:
- Be 1-2 sentences max
- Name specific items from their wardrobe where possible
- Feel like real stylist advice
- Start with "Style it with..." or "Pair it with..."

Format as a numbered list. Be specific and encouraging."""

def render_revival_section(wardrobe, history):
    st.markdown("""
    <div class="section-title">✨ Rediscover Your Wardrobe</div>
    <div class="section-subtitle">Items you haven't worn in a while — with fresh ways to style them.</div>
    """, unsafe_allow_html=True)

    if not wardrobe:
        st.info("Add items to your wardrobe to see revival suggestions.")
        return

    forgotten = get_forgotten_items(wardrobe, history)

    if not forgotten:
        st.markdown("""
        <div style="background:#e8f5e9;border:1.5px solid #a5d6a7;border-radius:12px;
            padding:20px;text-align:center;box-shadow:0 0 14px rgba(129,199,132,0.25);">
            <div style="font-size:1.8rem;margin-bottom:6px;">🎉</div>
            <div style="font-size:1rem;font-weight:700;color:#0a0a0a;">
                Your wardrobe is fully active — everything's been worn recently!
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    for idx, item in enumerate(forgotten[:3]):
        item_name = item.get("item", "Unknown Item")
        color = item.get("color", "")
        category = item.get("category", "")
        worn_label = item.get("worn_label", "Never worn")
        badge_bg = "#fce4ec" if worn_label == "Never worn" else "#fff8e1"
        badge_border = "#ef9a9a" if worn_label == "Never worn" else "#ffe082"
        outfits = generate_revival_outfits(item, wardrobe)

        st.markdown(f"""
        <div class="revival-card">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:12px;">
                <div>
                    <div style="font-size:1.05rem;font-weight:700;color:#0a0a0a;margin-bottom:2px;">
                        {color.title()} {category}
                    </div>
                    <div style="font-size:0.82rem;color:#4a4a5a;">{item_name}</div>
                </div>
                <span style="background:{badge_bg};color:#0a0a0a;font-size:0.72rem;font-weight:600;
                    padding:3px 10px;border-radius:6px;border:1.5px solid {badge_border};
                    letter-spacing:1px;text-transform:uppercase;white-space:nowrap;">
                    {worn_label}
                </span>
            </div>
        """, unsafe_allow_html=True)

        if outfits:
            st.markdown("""
            <div style="font-size:0.65rem;font-weight:600;letter-spacing:2px;
                text-transform:uppercase;color:#7986cb;margin-bottom:8px;">
                Fresh ways to wear it
            </div>
            """, unsafe_allow_html=True)
            for outfit in outfits:
                pieces_text = " + ".join(
                    f"{p.get('color', '')} {p.get('item', p.get('category', ''))}"
                    for p in outfit["pieces"]
                )
                st.markdown(f"""
                <div style="padding:8px 12px;background:#f1f8f1;
                    border-left:3px solid #a5d6a7;border-radius:0 6px 6px 0;
                    margin-bottom:6px;font-size:0.85rem;color:#0a0a0a;">
                    <span style="font-weight:600;color:#2e7d32;">{outfit['label']}:</span>
                    &nbsp;{item_name} + {pieces_text}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        ai_key = f"ai_revival_{idx}_{item_name.replace(' ', '_')}"
        if st.button(f"✨ Get AI styling ideas for {item_name}", key=ai_key):
            with st.spinner("Your AI stylist is thinking..."):
                try:
                    from dotenv import load_dotenv
                    from google import genai
                    load_dotenv()
                    api_key = os.getenv("GEMINI_API_KEY")
                    client = genai.Client(api_key=api_key)
                    prompt = get_revival_gemini_prompt(item, wardrobe)
                    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                    st.session_state[ai_key + "_result"] = response.text
                except Exception as e:
                    st.session_state[ai_key + "_result"] = f"Couldn't fetch AI suggestions: {e}"

        if st.session_state.get(ai_key + "_result"):
            st.markdown(f"""
            <div style="background:#f1f8f1;border:1.5px solid #a5d6a7;border-radius:10px;
                padding:14px 16px;margin-top:8px;font-size:0.88rem;color:#0a0a0a;
                line-height:1.6;white-space:pre-wrap;">
                {st.session_state[ai_key + "_result"]}
            </div>
            """, unsafe_allow_html=True)