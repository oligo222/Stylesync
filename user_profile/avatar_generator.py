"""
StyleSync Avatar Generator Interface
"""
import os
import sys
import re
import json
from typing import Dict
from dotenv import load_dotenv
from google import genai
from google.genai import types

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

AvatarAppearance = Dict[str, str]
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def _validate_uploaded_image(filename: str) -> None:
    _, ext = os.path.splitext(filename.lower())
    if ext not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError("Uploaded image must be JPG, JPEG, or PNG.")


def _mime_type_from_filename(filename: str) -> str:
    ext = os.path.splitext(filename.lower())[1]
    if ext == ".png":
        return "image/png"
    return "image/jpeg"


def extract_appearance_traits(image_bytes: bytes, mime_type: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)
    prompt = """
    Extract appearance traits from this full-body image.
    Return ONLY valid JSON:
    {
      "skin_tone": "",
      "hair_color": "",
      "hair_length": "",
      "hair_style": "",
      "body_type": "",
      "face_shape": ""
    }
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(
                parts=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    types.Part.from_text(text=prompt),
                ]
            )
        ]
    )

    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "")
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("Invalid JSON from model")
    return json.loads(match.group())


def _build_avatar_prompt(appearance_traits: Dict[str, str], angle: str = "front"):
    angles = {
        "front": "full-body front view, standing naturally, eye-level camera",
        "side": "full-body right side profile, natural pose",
        "back": "full-body back view, showing hairstyle and posture"
    }

    prompt = f"""
Ultra-realistic full-body avatar portrait.

Style:
- hyper realistic
- cinematic studio lighting
- natural skin texture
- detailed hair strands
- DSLR-quality photograph
- NOT cartoon, NOT anime, NOT illustration

Pose:
{angles.get(angle, angles["front"])}

Identity traits:
"""
    for k, v in appearance_traits.items():
        if v and str(v).lower() != "unknown":
            prompt += f"- {k}: {v}\n"

    prompt += "\nOutput: a single realistic full-body portrait image."
    return prompt


def _create_avatar_image(uploaded_image_bytes, filename, appearance_traits, angle="front"):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)
    prompt = _build_avatar_prompt(appearance_traits, angle)
    mime_type = _mime_type_from_filename(filename)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_bytes(data=uploaded_image_bytes, mime_type=mime_type),
                        types.Part.from_text(text=prompt),
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return part.inline_data.data

        raise RuntimeError("No image was returned by the model.")

    except Exception as e:
        raise RuntimeError(f"Avatar generation failed: {e}")


def generate_avatar_image(
    uploaded_image_bytes: bytes,
    filename: str,
    detected_appearance: Dict[str, str],
    manual_appearance: Dict[str, str],
    angle: str = "front",
) -> bytes:

    _validate_uploaded_image(filename)

    if not detected_appearance:
        mime_type = _mime_type_from_filename(filename)
        detected_appearance = extract_appearance_traits(
            uploaded_image_bytes,
            mime_type
        )

    final_traits = {**detected_appearance}
    for k, v in (manual_appearance or {}).items():
        if v and v.lower() != "unknown":
            final_traits[k] = v

    return _create_avatar_image(
        uploaded_image_bytes,
        filename,
        final_traits,
        angle
    )


def generate_avatar(*args, **kwargs):
    return generate_avatar_image(*args, **kwargs)


def generate_all_views(image_bytes, filename, traits):
    return {
        "front": _create_avatar_image(image_bytes, filename, traits, "front"),
        "side": _create_avatar_image(image_bytes, filename, traits, "side"),
        "back": _create_avatar_image(image_bytes, filename, traits, "back"),
    }