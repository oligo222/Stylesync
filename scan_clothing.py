from dotenv import load_dotenv
import os
from google import genai
from pathlib import Path
import json
import uuid
import base64

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

wardrobe_folder = Path("wardrobe")
wardrobe_file = Path("wardrobe.json")

if wardrobe_file.exists():
    wardrobe = json.loads(wardrobe_file.read_text())
else:
    wardrobe = []

already_scanned = [Path(item["image_path"]).name for item in wardrobe]

photos = list(wardrobe_folder.glob("*.jpg")) + list(wardrobe_folder.glob("*.png"))

if not photos:
    print("No photos found in wardrobe folder!")
else:
    for image_path in photos:
        if image_path.name in already_scanned:
            print(f"Skipping {image_path.name} — already scanned!")
            continue

        print(f"Scanning {image_path.name}...")
        image_bytes = image_path.read_bytes()

        prompt = """Analyze this clothing item and respond ONLY with a JSON object like this:
{
  "category": "...",
  "garment_type": "...",
  "color": "...",
  "pattern": "...",
  "style": "..."
}

For "category", you MUST choose exactly one of these four values: "Top", "Bottom", "Footwear", "Outerwear".
For "garment_type", describe the specific item naturally (e.g. "camisole", "blazer", "ankle boots", "wide-leg trousers").
For "style", you MUST choose exactly one of these two values: "Formal", "Casual".

No extra text, just the JSON."""

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[
                {
                    "parts": [
                        {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(image_bytes).decode()}},
                        {"text": prompt}
                    ]
                }
            ]
        )

        cleaned = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(cleaned)
        data["id"] = str(uuid.uuid4())
        data["image_path"] = str(image_path)

        wardrobe.append(data)
        print(f"✅ Saved {image_path.name}!")

    wardrobe_file.write_text(json.dumps(wardrobe, indent=2))
    print("\nAll done! Your wardrobe.json is updated!")
