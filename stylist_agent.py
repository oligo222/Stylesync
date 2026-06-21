import os
import json
import re
import time
from dotenv import load_dotenv
from google import genai
from recommendation_engine import load_wardrobe, generate_outfits

# Load environment variables from the .env file
load_dotenv()

# Retrieve the Gemini API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini API client using the google-genai SDK format
# If the API key is not present, we will still instantiate client = None to allow graceful fallback
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

def score_and_explain(outfit, event_description, max_retries=2, retry_delay=3):
    """
    Asks Gemini to act as a fashion stylist, evaluates how well the given outfit
    suits the event description, and returns a JSON object with:
    - suitability_score (0-100)
    - confidence_score (0-100)
    - explanation (1-2 sentences)
    
    Retries up to max_retries times on transient API errors before falling
    back to a default evaluation.
    
    Parameters:
        outfit (dict): A dictionary with keys "top", "bottom", "footwear".
        event_description (str): A description of the event (e.g., "Interview tomorrow").
        max_retries (int): Number of attempts before falling back.
        retry_delay (int): Seconds to wait between retries.
        
    Returns:
        dict: A dictionary containing the score and explanation keys.
    """
    fallback_dict = {
        "suitability_score": 70,
        "confidence_score": 50,
        "explanation": "This outfit is a reasonable match based on style and color coordination."
    }
    
    if not client:
        return fallback_dict
        
    prompt = f"""You are a professional fashion stylist.
Evaluate how well the following outfit suits this event description: "{event_description}".

Outfit details:
- Top: {outfit.get("top")}
- Bottom: {outfit.get("bottom")}
- Footwear: {outfit.get("footwear")}

Return ONLY a JSON object with exactly these keys:
- "suitability_score": an integer from 0 to 100 representing suitability
- "confidence_score": an integer from 0 to 100 representing confidence in your evaluation
- "explanation": a 1-2 sentence string explaining your evaluation

Do not write any markdown code blocks, preamble, formatting, or commentary outside of the raw JSON object.
"""

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            response_text = response.text.strip()
            
            if response_text.startswith("```"):
                response_text = re.sub(r"^```(?:json)?\s*", "", response_text)
                response_text = re.sub(r"\s*```$", "", response_text)
                response_text = response_text.strip()
                
            result = json.loads(response_text)
            
            required_keys = ["suitability_score", "confidence_score", "explanation"]
            if all(key in result for key in required_keys):
                return result
            else:
                return fallback_dict
                
        except Exception as e:
            print(f"ACTUAL ERROR in stylist (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    print("Stylist: all retry attempts failed, using fallback score.")
    return fallback_dict

if __name__ == "__main__":
    # Load the wardrobe items
    wardrobe = load_wardrobe("data/wardrobe.json")
    
    # Generate outfit combinations suitable for a Formal event style
    outfits = generate_outfits(wardrobe, "Formal")
    
    # Process each outfit, score it, and print the combined result
    for outfit in outfits:
        evaluation = score_and_explain(outfit, "Interview tomorrow")
        
        # Combine the outfit details with the evaluation dictionary
        combined_result = {**outfit, **evaluation}
        
        # Print the formatted JSON object
        print(json.dumps(combined_result, indent=2))
        print()  # Add an extra newline for readability between outfits
