"""
StyleSync AI Appearance Analyzer Module

Uses Gemini Vision to estimate user physical traits from their profile picture.
"""
import os
import sys
import json
import base64
from dotenv import load_dotenv
from google import genai

# Allow importing from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

def analyze_user_appearance(image_bytes) -> dict:
    """
    Sends the profile image to Gemini Vision to analyze physical characteristics.
    
    Returns:
        dict: A dictionary containing:
            - skin_tone: "Light" / "Medium" / "Dark" / "Olive" / "Unknown"
            - hair_color: "Black" / "Brown" / "Blonde" / "Grey" / "Red" / "White" / "Bald" / "Unknown"
            - hair_length: "Bald" / "Short" / "Medium" / "Long" / "Unknown"
            - hair_style: "Straight" / "Wavy" / "Curly" / "Coily" / "Bald" / "Unknown"
            - face_shape: "Oval" / "Round" / "Square" / "Heart" / "Diamond" / "Unknown"
    """
    # Load environment variables
    env_path = os.path.join(PROJECT_ROOT, ".env")
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Appearance Analyzer ERROR: No API key found.")
        return get_default_traits()
        
    prompt = """Analyze the person in this profile picture. Identify the following features and return them strictly in JSON format:
{
  "skin_tone": "One of: Light, Medium, Dark, Olive",
  "hair_color": "One of: Black, Brown, Blonde, Grey, Red, White, Bald",
  "hair_length": "One of: Bald, Short, Medium, Long",
  "hair_style": "One of: Straight, Wavy, Curly, Coily, Bald",
  "face_shape": "One of: Oval, Round, Square, Heart, Diamond"
}
Ensure confidence. If you cannot determine any attribute confidently, set its value to "Unknown".
Do not include any extra markdown formatting like ```json ... ``` or text explanations. Return ONLY the raw JSON string."""

    try:
        client = genai.Client(api_key=api_key)
        encoded_image = base64.b64encode(image_bytes).decode()
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "parts": [
                        {"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}},
                        {"text": prompt}
                    ]
                }
            ]
        )
        
        # Clean response string
        raw_text = response.text.strip()
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        
        data = json.loads(cleaned)
        
        # Validate values against standard lists, default to 'Unknown' if mismatch
        valid_options = {
            "skin_tone": ["Light", "Medium", "Dark", "Olive"],
            "hair_color": ["Black", "Brown", "Blonde", "Grey", "Red", "White", "Bald"],
            "hair_length": ["Bald", "Short", "Medium", "Long"],
            "hair_style": ["Straight", "Wavy", "Curly", "Coily", "Bald"],
            "face_shape": ["Oval", "Round", "Square", "Heart", "Diamond"]
        }
        
        sanitized = {}
        for key, options in valid_options.items():
            val = str(data.get(key, "")).strip().title()
            if val in options:
                sanitized[key] = val
            else:
                sanitized[key] = "Unknown"
                
        return sanitized
        
    except Exception as e:
        print(f"Error during AI appearance analysis: {e}")
        return get_default_traits()

def get_default_traits() -> dict:
    """Returns default 'Unknown' values for all appearance traits."""
    return {
        "skin_tone": "Unknown",
        "hair_color": "Unknown",
        "hair_length": "Unknown",
        "hair_style": "Unknown",
        "face_shape": "Unknown"
    }
