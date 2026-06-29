"""
StyleSync Reusable Wardrobe Components
"""
import os
import json
import streamlit as st

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WARDROBE_PATH = os.path.join(_PROJECT_ROOT, "wardrobe.json")

CATEGORIES = ["Top", "Bottom", "Outerwear", "Dress", "Footwear", "Accessory", "Bag", "Loungewear", "Other"]
STYLES     = ["Casual", "Formal", "Smart Casual", "Ethnic", "Activewear", "Other"]

def _load_wardrobe_raw() -> list:
    if os.path.exists(WARDROBE_PATH):
        with open(WARDROBE_PATH, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else data.get("items", [])
    return []

def _save_wardrobe(items: list):
    with open(WARDROBE_PATH, "w") as f:
        json.dump(items, f, indent=2)

def _delete_item(item_index_in_raw: int):
    items = _load_wardrobe_raw()
    if 0 <= item_index_in_raw < len(items):
        items.pop(item_index_in_raw)
        _save_wardrobe(items)

def _update_item(item_index_in_raw: int, category: str, style: str):
    items = _load_wardrobe_raw()
    if 0 <= item_index_in_raw < len(items):
        items[item_index_in_raw]["category"] = category
        items[item_index_in_raw]["style"]    = style
        _save_wardrobe(items)

def render_clothing_card(item: dict, raw_index: int = None):
    """
    Renders a clothing card with optional delete + edit buttons.
    Pass raw_index (position in wardrobe.json) to enable editing.
    """
    with st.container(border=True):
        # Image
        if item.get("image"):
            st.image(item["image"], use_container_width=True)
        else:
            st.header("👕")

        # Title + tags
        st.subheader(item.get("type", "Unknown Item"), divider="gray")
        tags = [
            f"**Color:** {item.get('color')}" if item.get("color") else None,
            item.get("season"),
            item.get("style"),
            item.get("occasion"),
        ]
        st.markdown("  •  ".join(filter(None, tags)))

        # Only show controls if we know which raw item this is
        if raw_index is None:
            return

        edit_key   = f"editing_{raw_index}"
        confirm_key = f"confirm_delete_{raw_index}"

        # ── Delete flow ──────────────────────────────────────────
        if st.session_state.get(confirm_key):
            st.warning("Remove this item?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Yes, delete", key=f"yes_{raw_index}", use_container_width=True, type="primary"):
                    _delete_item(raw_index)
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
            with c2:
                if st.button("Cancel", key=f"cancel_del_{raw_index}", use_container_width=True):
                    st.session_state.pop(confirm_key, None)
                    st.rerun()

        # ── Edit flow ────────────────────────────────────────────
        elif st.session_state.get(edit_key):
            current_cat   = item.get("type", "Other")
            current_style = item.get("style", "Casual")
            cat_idx   = CATEGORIES.index(current_cat)   if current_cat   in CATEGORIES else 0
            style_idx = STYLES.index(current_style)     if current_style in STYLES     else 0

            new_cat   = st.selectbox("Category", CATEGORIES, index=cat_idx,   key=f"cat_{raw_index}")
            new_style = st.selectbox("Style",    STYLES,     index=style_idx, key=f"sty_{raw_index}")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Save", key=f"save_{raw_index}", use_container_width=True, type="primary"):
                    _update_item(raw_index, new_cat, new_style)
                    st.session_state.pop(edit_key, None)
                    st.rerun()
            with c2:
                if st.button("Cancel", key=f"cancel_edit_{raw_index}", use_container_width=True):
                    st.session_state.pop(edit_key, None)
                    st.rerun()

        # ── Default buttons ──────────────────────────────────────
        else:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✏️ Edit", key=f"edit_{raw_index}", use_container_width=True):
                    st.session_state[edit_key] = True
                    st.rerun()
            with c2:
                if st.button("🗑️ Delete", key=f"del_{raw_index}", use_container_width=True):
                    st.session_state[confirm_key] = True
                    st.rerun()