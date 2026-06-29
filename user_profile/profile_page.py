"""
StyleSync Profile Page UI Module

Provides the complete profile management and avatar generation interface.
"""
import os
import sys
import streamlit as st

# Allow importing from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.profile_db import update_user_profile
from .image_processor import process_and_save_profile_pic, process_and_save_3d_avatar_image
from .appearance_analyzer import analyze_user_appearance
from .avatar_generator import generate_avatar_image
from .avatar_viewer import render_interactive_avatar_viewer, render_avatar_angle_selector
from authentication.auth_utils import require_login

def _load_image_bytes(path: str):
    if not path:
        return None
    absolute_path = os.path.join(PROJECT_ROOT, path)
    if not os.path.exists(absolute_path):
        return None
    with open(absolute_path, "rb") as f:
        return f.read()


def _save_generated_avatar_bytes(user_id: str, image_bytes: bytes, angle_suffix: str = "") -> str:
    data_dir = os.path.join(PROJECT_ROOT, "data")
    avatars_dir = os.path.join(data_dir, "avatars")
    os.makedirs(avatars_dir, exist_ok=True)
    output_path = os.path.join(avatars_dir, f"{user_id}{angle_suffix}_3d_generated.jpg")
    with open(output_path, "wb") as f:
        f.write(image_bytes)
    return f"data/avatars/{user_id}{angle_suffix}_3d_generated.jpg"


def _delete_user_images(user_id: str) -> dict:
    deleted: list[str] = []
    errors: list[str] = []

    user_state = st.session_state.get("user", {})
    candidate_relative_paths = [
        user_state.get("profile_image_path"),
        user_state.get("avatar_image_path"),
        user_state.get("avatar_3d_image_path"),
    ]

    avatars_dir = os.path.join(PROJECT_ROOT, "data", "avatars")
    if os.path.isdir(avatars_dir):
        for fname in os.listdir(avatars_dir):
            if fname.startswith(str(user_id)) and fname.endswith("_3d_generated.jpg"):
                candidate_relative_paths.append(f"data/avatars/{fname}")

    for rel_path in candidate_relative_paths:
        if not rel_path:
            continue
        abs_path = os.path.join(PROJECT_ROOT, rel_path)
        if os.path.isfile(abs_path):
            try:
                os.remove(abs_path)
                deleted.append(rel_path)
            except OSError as exc:
                errors.append(f"Could not delete {rel_path}: {exc}")

    user_pics_dir = os.path.join(PROJECT_ROOT, "data", "profile_pics", str(user_id))
    if os.path.isdir(user_pics_dir):
        try:
            if not os.listdir(user_pics_dir):
                os.rmdir(user_pics_dir)
        except OSError:
            pass

    session_keys_to_clear = [
        "avatar_3d_upload",
        "avatar_3d_upload_bytes",
        "avatar_3d_upload_filename",
        "current_avatar_angle",
        "detected_appearance",  # clear cached detection too
    ]
    for key in session_keys_to_clear:
        st.session_state.pop(key, None)

    if st.session_state.get("user"):
        for field in ("profile_image_path", "avatar_image_path", "avatar_3d_image_path"):
            st.session_state["user"][field] = None

    if user_id:
        update_user_profile(
            user_id,
            {
                "profile_image_path": None,
                "avatar_image_path": None,
                "avatar_3d_image_path": None,
            },
        )

    return {"deleted": deleted, "errors": errors}


def _generate_and_persist_3d_avatar(user_id, avatar_3d_image_path, detected_traits, manual_appearance=None, angle="front"):
    image_bytes = st.session_state.get("avatar_3d_upload_bytes")
    filename = st.session_state.get("avatar_3d_upload_filename")

    if image_bytes is None and avatar_3d_image_path:
        image_bytes = _load_image_bytes(avatar_3d_image_path)
        filename = filename or os.path.basename(avatar_3d_image_path)

    if not image_bytes or not filename:
        raise ValueError("Please upload a front-facing full-body image before generating a 3D avatar.")

    generated_bytes = generate_avatar_image(
        uploaded_image_bytes=image_bytes,
        filename=filename,
        detected_appearance=detected_traits,
        manual_appearance=manual_appearance or detected_traits,
        angle=angle,
    )

    angle_suffix = f"_{angle}" if angle != "front" else ""
    avatar_path = _save_generated_avatar_bytes(user_id, generated_bytes, angle_suffix)

    st.session_state["current_avatar_angle"] = angle
    update_user_profile(user_id, {"avatar_image_path": avatar_path})
    st.session_state["user"]["avatar_image_path"] = avatar_path
    return avatar_path


def _render_3d_avatar_section(user_id, avatar_3d_image_path, detected_traits):
    st.write("### 3D Avatar")
    with st.container():
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown('<div class="preview-label">3D Avatar Preview</div>', unsafe_allow_html=True)

        if avatar_3d_image_path and os.path.exists(os.path.join(PROJECT_ROOT, avatar_3d_image_path)):
            st.image(os.path.join(PROJECT_ROOT, avatar_3d_image_path), use_container_width=True)
        else:
            st.markdown(
                """
                <div class="preview-box">
                    <span style="font-size: 2.5rem; color: #9ca3af;">🧍‍♂️</span>
                    <span style="font-size: 0.95rem; color: #6b7280; margin-top: 8px;">Upload a front-facing full-body image to preview your 3D avatar input.</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        if detected_traits and any(val != "Unknown" for val in detected_traits.values()):
            detected_items = "".join(
                f"<div style='min-width: 120px; padding: 10px 12px; border: 1px solid #e5e7eb; border-radius: 12px; background: #ffffff;'>"
                f"<div style='font-size:0.75rem; font-weight:700; color:#4b5563;'>{label}</div>"
                f"<div style='font-size:0.95rem; color:#111827; margin-top:4px;'>{value}</div>"
                f"</div>"
                for label, value in [
                    ("Skin Tone", detected_traits.get("skin_tone", "Unknown")),
                    ("Hair Color", detected_traits.get("hair_color", "Unknown")),
                    ("Hair Length", detected_traits.get("hair_length", "Unknown")),
                    ("Hair Style", detected_traits.get("hair_style", "Unknown")),
                    ("Body Type", detected_traits.get("body_type", "Unknown"))
                ]
            )
            st.markdown(
                f"""
                <div style='margin: 18px 0; padding: 16px; border: 1px solid #e5e7eb; border-radius: 16px; background: #f8fafc;'>
                    <div style='font-size: 0.95rem; font-weight: 700; color: #111827; margin-bottom: 12px;'>Detected Attributes</div>
                    <div style='display:flex; flex-wrap:wrap; gap:12px;'>{detected_items}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        uploaded_3d_image = st.file_uploader(
            "Upload a front-facing full-body image",
            type=["jpg", "jpeg", "png"],
            key="avatar_3d_upload",
            help="Upload one front-facing full-body image for 3D avatar creation."
        )

        image_uploaded = any([
            uploaded_3d_image is not None,
            st.session_state.get("avatar_3d_upload_bytes") is not None,
            st.session_state.get("avatar_3d_upload_filename") is not None,
            avatar_3d_image_path,
        ])

        if image_uploaded:
            if st.button("Remove Image", key="clear_3d_avatar_upload_btn", use_container_width=True):
                if avatar_3d_image_path:
                    abs_3d = os.path.join(PROJECT_ROOT, avatar_3d_image_path)
                    if os.path.isfile(abs_3d):
                        try:
                            os.remove(abs_3d)
                        except OSError:
                            pass
                    user_pics_dir = os.path.join(PROJECT_ROOT, "data", "profile_pics", str(user_id))
                    if os.path.isdir(user_pics_dir) and not os.listdir(user_pics_dir):
                        try:
                            os.rmdir(user_pics_dir)
                        except OSError:
                            pass
                for state_key in ("avatar_3d_upload", "avatar_3d_upload_bytes", "avatar_3d_upload_filename"):
                    st.session_state.pop(state_key, None)
                if user_id and st.session_state.get("user"):
                    st.session_state["user"]["avatar_3d_image_path"] = None
                    update_user_profile(user_id, {"avatar_3d_image_path": None})
                st.rerun()

        if uploaded_3d_image is not None:
            try:
                with st.spinner("Saving and analysing full-body image..."):
                    bytes_data = uploaded_3d_image.getvalue()
                    saved_path = process_and_save_3d_avatar_image(bytes_data, uploaded_3d_image.name, user_id)
                    analysis = analyze_user_appearance(bytes_data)

                    if user_id and st.session_state.get("user"):
                        st.session_state["user"]["avatar_3d_image_path"] = saved_path
                        st.session_state["avatar_3d_upload_bytes"] = bytes_data
                        st.session_state["avatar_3d_upload_filename"] = uploaded_3d_image.name
                        for trait in ("skin_tone", "hair_color", "hair_length", "hair_style", "body_type", "face_shape"):
                            st.session_state["user"][trait] = analysis.get(trait, "Unknown")
                        update_user_profile(user_id, {
                            "avatar_3d_image_path": saved_path,
                            **{t: analysis.get(t, "Unknown") for t in ("skin_tone", "hair_color", "hair_length", "hair_style", "body_type", "face_shape")}
                        })

                    avatar_3d_image_path = saved_path
                    detected_traits = analysis
                    st.success("✅ Image uploaded — appearance auto-detected from your photo.")
            except Exception as exc:
                st.error(str(exc))

        btn_col1, btn_col2 = st.columns([1, 1], gap="medium")
        with btn_col1:
            if st.button("Generate 3D Avatar", key="generate_3d_avatar_btn", use_container_width=True, disabled=not avatar_3d_image_path):
                try:
                    _generate_and_persist_3d_avatar(user_id, avatar_3d_image_path, detected_traits, angle="front")
                    st.success("3D avatar generated successfully.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        with btn_col2:
            if st.button("Regenerate Avatar", key="regenerate_3d_avatar_btn", use_container_width=True, disabled=not avatar_3d_image_path):
                try:
                    _generate_and_persist_3d_avatar(user_id, avatar_3d_image_path, detected_traits, angle="front")
                    st.success("3D avatar regenerated successfully.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        avatar_pic = avatar_3d_image_path
        if avatar_pic and os.path.exists(os.path.join(PROJECT_ROOT, avatar_pic)):
            st.markdown('<hr style="margin: 20px 0;"/>', unsafe_allow_html=True)
            render_interactive_avatar_viewer(avatar_pic, viewer_height=500)

            if "current_avatar_angle" not in st.session_state:
                st.session_state["current_avatar_angle"] = "front"

            def on_generate_angle(angle):
                try:
                    with st.spinner(f"Generating {angle} view..."):
                        _generate_and_persist_3d_avatar(user_id, avatar_3d_image_path, detected_traits, angle=angle)
                    st.success(f"Avatar {angle} view generated!")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

            render_avatar_angle_selector(user_id, st.session_state["current_avatar_angle"], on_generate_angle)

        st.markdown('</div>', unsafe_allow_html=True)


def render_profile_page():
    require_login()

    css_path = os.path.join(PROJECT_ROOT, "streamlit_app", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .profile-title-container { margin-bottom: 24px; }
        .info-card {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 24px;
        }
        .preview-box {
            text-align: center;
            padding: 12px;
            background-color: #f9fafb;
            border: 1px dashed #d1d5db;
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 180px;
        }
        .preview-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: #4b5563;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .auto-detected-badge {
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 600;
            background: #d1fae5;
            color: #065f46;
            border-radius: 6px;
            padding: 2px 8px;
            margin-left: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if "editing_profile" not in st.session_state:
        st.session_state["editing_profile"] = False

    user = st.session_state.get("user", {})
    user_id = user.get("id")
    name = user.get("name", "User")
    age = user.get("age", 25)
    gender = user.get("gender", "Prefer not to say")
    email = user.get("email", "")

    profile_pic = user.get("profile_image_path")
    avatar_pic = user.get("avatar_image_path")
    avatar_3d_image_path = user.get("avatar_3d_image_path")
    skin_tone = user.get("skin_tone", "Unknown")
    hair_color = user.get("hair_color", "Unknown")
    hair_length = user.get("hair_length", "Unknown")
    hair_style = user.get("hair_style", "Unknown")
    body_type = user.get("body_type", "Unknown")
    height = user.get("height") or "Unknown"
    face_shape = user.get("face_shape", "Unknown")
    detected_traits = {
        "skin_tone": skin_tone,
        "hair_color": hair_color,
        "hair_length": hair_length,
        "hair_style": hair_style,
        "body_type": body_type,
        "face_shape": face_shape,
    }

    st.markdown(
        """
        <div class="profile-title-container">
            <h1 style="font-weight: 700; margin-bottom: 4px;">👤 Profile & Persona</h1>
            <p style="color: #6b7280; font-size: 1.1rem; margin: 0;">
                Manage your account, customize appearance details, and generate your AI avatar.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("---")

    col_left, col_right = st.columns([1.2, 2], gap="large")

    with col_left:
        st.write("### My Persona")

        with st.container():
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            p_col1, p_col2 = st.columns(2, gap="medium")

            with p_col1:
                st.markdown('<div class="preview-label">Profile Photo</div>', unsafe_allow_html=True)
                if profile_pic and os.path.exists(os.path.join(PROJECT_ROOT, profile_pic)):
                    st.image(os.path.join(PROJECT_ROOT, profile_pic), use_container_width=True)
                else:
                    st.markdown(
                        """
                        <div class="preview-box">
                            <span style="font-size: 2.5rem; color: #9ca3af;">📷</span>
                            <span style="font-size: 0.8rem; color: #6b7280; margin-top: 4px;">No Photo Uploaded</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            with p_col2:
                st.markdown('<div class="preview-label">AI Avatar</div>', unsafe_allow_html=True)
                if avatar_pic and os.path.exists(os.path.join(PROJECT_ROOT, avatar_pic)):
                    st.image(os.path.join(PROJECT_ROOT, avatar_pic), use_container_width=True)
                else:
                    st.markdown(
                        """
                        <div class="preview-box">
                            <span style="font-size: 2.5rem; color: #9ca3af;">✨</span>
                            <span style="font-size: 0.8rem; color: #6b7280; margin-top: 4px;">Avatar Not Generated</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown('</div>', unsafe_allow_html=True)

        st.write("#### Avatar Settings")
        can_generate = bool(avatar_3d_image_path or st.session_state.get("avatar_3d_upload_bytes"))
        col_gen, col_upload, col_delete = st.columns([1.2, 1, 1])

        with col_gen:
            regen_btn = st.button(
                "✨ Regenerate Avatar",
                use_container_width=True,
                disabled=not can_generate,
                help="Re-run avatar generator using your appearance settings."
            )
            if regen_btn:
                try:
                    with st.spinner("Generating stylized AI avatar..."):
                        _generate_and_persist_3d_avatar(user_id, avatar_3d_image_path, detected_traits)
                        st.success("Avatar generated successfully!")
                        st.rerun()
                except NotImplementedError:
                    st.warning("3D avatar generation backend is not implemented yet.")
                except Exception as exc:
                    st.error(str(exc))

        with col_upload:
            if not st.session_state["editing_profile"]:
                if st.button("✏️ Edit Profile", use_container_width=True):
                    st.session_state["editing_profile"] = True
                    st.rerun()
            else:
                if st.button("❌ Cancel Edit", use_container_width=True):
                    st.session_state["editing_profile"] = False
                    st.rerun()

        with col_delete:
            has_any_image = bool(
                user.get("profile_image_path")
                or user.get("avatar_image_path")
                or user.get("avatar_3d_image_path")
                or st.session_state.get("avatar_3d_upload_bytes")
            )
            if st.button(
                "🗑️ Clear All Images",
                use_container_width=True,
                disabled=not has_any_image,
                key="clear_all_images_btn",
            ):
                result = _delete_user_images(user_id)
                if result["errors"]:
                    for err in result["errors"]:
                        st.warning(err)
                if result["deleted"]:
                    st.success(f"Removed {len(result['deleted'])} image file(s) successfully.")
                else:
                    st.info("No image files were found on disk to remove.")
                st.rerun()

    with col_right:
        if st.session_state["editing_profile"]:
            st.write("### Edit Profile Details")

            # ── Check if a profile pic is being uploaded so we can auto-detect ──
            # We use a two-step approach: uploader outside the form to detect
            # traits before the form renders, so dropdowns are pre-filled.
            st.markdown("**Replace Profile Picture**")
            uploaded_pic = st.file_uploader(
                "Upload a face photo — appearance will be auto-detected",
                type=["jpg", "jpeg", "png"],
                key="edit_profile_pic_uploader",
            )

            # Auto-detect from uploaded pic and cache in session
            if uploaded_pic is not None:
                pic_key = f"detected_from_{uploaded_pic.name}_{uploaded_pic.size}"
                if st.session_state.get("_last_detected_key") != pic_key:
                    with st.spinner("🔍 Detecting appearance from photo..."):
                        pic_bytes = uploaded_pic.getvalue()
                        auto = analyze_user_appearance(pic_bytes)
                    st.session_state["detected_appearance"] = auto
                    st.session_state["_last_detected_key"] = pic_key
                    st.success("✅ Appearance auto-detected! Dropdowns updated below.")

            # Use auto-detected values if available, else fall back to saved values
            auto = st.session_state.get("detected_appearance", {})
            eff_skin   = auto.get("skin_tone",   skin_tone)   if auto.get("skin_tone")   not in (None, "Unknown") else skin_tone
            eff_hcol   = auto.get("hair_color",  hair_color)  if auto.get("hair_color")  not in (None, "Unknown") else hair_color
            eff_hlen   = auto.get("hair_length",  hair_length) if auto.get("hair_length") not in (None, "Unknown") else hair_length
            eff_hsty   = auto.get("hair_style",  hair_style)  if auto.get("hair_style")  not in (None, "Unknown") else hair_style
            eff_body   = auto.get("body_type",   body_type)   if auto.get("body_type")   not in (None, "Unknown") else body_type
            eff_face   = auto.get("face_shape",  face_shape)  if auto.get("face_shape")  not in (None, "Unknown") else face_shape

            with st.form("edit_profile_form", clear_on_submit=False):
                name_val = st.text_input("Full Name", value=name)
                age_val = st.number_input("Age", min_value=1, max_value=120, value=int(age))
                gender_opts = ["Female", "Male", "Non-binary", "Prefer not to say"]
                gender_val = st.selectbox(
                    "Gender", gender_opts,
                    index=gender_opts.index(gender) if gender in gender_opts else 3
                )

                st.write("#### Appearance")
                st.caption("Auto-detected from your photo. You can adjust any value manually.")

                skin_opts = ["Unknown", "Light", "Medium", "Dark", "Olive"]
                skin_val = st.selectbox("Skin Tone", skin_opts,
                    index=skin_opts.index(eff_skin) if eff_skin in skin_opts else 0)

                hair_col_opts = ["Unknown", "Black", "Brown", "Blonde", "Grey", "Red", "White", "Bald"]
                hair_col_val = st.selectbox("Hair Color", hair_col_opts,
                    index=hair_col_opts.index(eff_hcol) if eff_hcol in hair_col_opts else 0)

                hair_len_opts = ["Unknown", "Bald", "Short", "Medium", "Long"]
                hair_len_val = st.selectbox("Hair Length", hair_len_opts,
                    index=hair_len_opts.index(eff_hlen) if eff_hlen in hair_len_opts else 0)

                hair_sty_opts = ["Unknown", "Straight", "Wavy", "Curly", "Coily", "Bald"]
                hair_sty_val = st.selectbox("Hair Style", hair_sty_opts,
                    index=hair_sty_opts.index(eff_hsty) if eff_hsty in hair_sty_opts else 0)

                body_type_opts = ["Unknown", "Slim", "Athletic", "Average", "Curvy", "Stocky"]
                body_type_val = st.selectbox("Body Type", body_type_opts,
                    index=body_type_opts.index(eff_body) if eff_body in body_type_opts else 0)

                height_val = st.text_input("Height", value=str(height))

                face_opts = ["Unknown", "Oval", "Round", "Square", "Heart", "Diamond"]
                face_val = st.selectbox("Face Shape", face_opts,
                    index=face_opts.index(eff_face) if eff_face in face_opts else 0)

                save_btn = st.form_submit_button("Save Profile & Generate Avatar", use_container_width=True)

            if save_btn:
                if not name_val:
                    st.error("Full name cannot be empty.")
                else:
                    updates = {
                        "name": name_val.strip(),
                        "age": age_val,
                        "gender": gender_val,
                        "skin_tone": skin_val,
                        "hair_color": hair_col_val,
                        "hair_length": hair_len_val,
                        "hair_style": hair_sty_val,
                        "body_type": body_type_val,
                        "height": height_val,
                        "face_shape": face_val,
                    }

                    if uploaded_pic is not None:
                        with st.spinner("Processing profile photo..."):
                            pic_bytes = uploaded_pic.getvalue()
                            saved_path = process_and_save_profile_pic(pic_bytes, uploaded_pic.name, user_id)
                            updates["profile_image_path"] = saved_path

                    if avatar_3d_image_path or st.session_state.get("avatar_3d_upload_bytes"):
                        with st.spinner("Creating stylized AI avatar..."):
                            try:
                                avatar_path = _generate_and_persist_3d_avatar(
                                    user_id, avatar_3d_image_path, detected_traits,
                                    manual_appearance={
                                        "skin_tone": skin_val,
                                        "hair_color": hair_col_val,
                                        "hair_length": hair_len_val,
                                        "hair_style": hair_sty_val,
                                        "body_type": body_type_val,
                                        "face_shape": face_val,
                                    }
                                )
                                updates["avatar_image_path"] = avatar_path
                            except NotImplementedError:
                                st.warning("Avatar generation not implemented yet. Profile saved.")
                            except Exception as exc:
                                st.error(str(exc))
                    else:
                        st.info("No 3D full-body image yet — profile saved without avatar generation.")

                    update_user_profile(user_id, updates)
                    for key, val in updates.items():
                        user[key] = val
                    st.session_state["user"] = user
                    st.session_state["editing_profile"] = False
                    st.session_state.pop("detected_appearance", None)
                    st.session_state.pop("_last_detected_key", None)

                    st.success("Profile saved successfully!")
                    st.rerun()

        else:
            st.write("### Account Details")
            st.markdown(
                f"""
                <div class="info-card">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 12px 0; font-weight: 600; color: #4b5563;">Full Name</td>
                            <td style="padding: 12px 0; text-align: right; color: #111827;">{name}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 12px 0; font-weight: 600; color: #4b5563;">Age</td>
                            <td style="padding: 12px 0; text-align: right; color: #111827;">{age} years old</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 0; font-weight: 600; color: #4b5563;">Gender</td>
                            <td style="padding: 12px 0; text-align: right; color: #111827;">{gender}</td>
                        </tr>
                    </table>
                </div>
                """,
                unsafe_allow_html=True
            )

            _render_3d_avatar_section(user_id, avatar_3d_image_path, detected_traits)

            st.write("### Appearance Attributes")
            has_any_trait = any(v != "Unknown" for v in detected_traits.values())
            st.markdown(
                f"""
                <div class="info-card">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 12px 0; font-weight: 600; color: #4b5563;">Skin Tone</td>
                            <td style="padding: 12px 0; text-align: right; color: #111827;">{skin_tone}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 12px 0; font-weight: 600; color: #4b5563;">Hair Color</td>
                            <td style="padding: 12px 0; text-align: right; color: #111827;">{hair_color}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 12px 0; font-weight: 600; color: #4b5563;">Hair Length</td>
                            <td style="padding: 12px 0; text-align: right; color: #111827;">{hair_length}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 12px 0; font-weight: 600; color: #4b5563;">Hair Style</td>
                            <td style="padding: 12px 0; text-align: right; color: #111827;">{hair_style}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 12px 0; font-weight: 600; color: #4b5563;">Body Type</td>
                            <td style="padding: 12px 0; text-align: right; color: #111827;">{body_type}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 12px 0; font-weight: 600; color: #4b5563;">Height</td>
                            <td style="padding: 12px 0; text-align: right; color: #111827;">{height}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 0; font-weight: 600; color: #4b5563;">Face Shape</td>
                            <td style="padding: 12px 0; text-align: right; color: #111827;">{face_shape}</td>
                        </tr>
                    </table>
                    {"<p style='font-size:0.8rem;color:#6b7280;margin-top:12px;'>💡 Upload a photo in Edit Profile to auto-detect these.</p>" if not has_any_trait else ""}
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("✏️ Edit Profile Details", key="read_mode_edit_btn", use_container_width=True):
                st.session_state["editing_profile"] = True
                st.rerun()