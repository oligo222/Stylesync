import os
import json
import re
import time
from dotenv import load_dotenv
from google import genai

# Load environment variables from the .env file
load_dotenv()

# Retrieve the Gemini API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini client using google-genai SDK
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None
def analyze_event(event_description, max_retries=2, retry_delay=3):
    """
    Analyzes a free-text event description and classifies its style and type.
    
    Uses Gemini 2.5 Flash to extract:
    - event_style: "Formal" or "Casual"
    - occasion_type: a short name like "Interview", "Wedding", etc.
    - reasoning: a single-sentence explanation.
    
    Retries up to max_retries times on transient API errors (e.g. 503)
    before falling back to a default dictionary.
    
    Parameters:
        event_description (str): Free-text description of the event.
        max_retries (int): Number of attempts before falling back.
        retry_delay (int): Seconds to wait between retries.
        
    Returns:
        dict: The analyzed event attributes.
    """
    fallback_dict = {
        "event_style": "Casual",
        "occasion_type": "General",
        "reasoning": "Defaulted to casual style due to an unrecognized or ambiguous event description."
    }
    
    if not client:
        return fallback_dict
        
    prompt = f"""You are a helpful fashion assistant.
Analyze the following event description and classify its formality and type.
Event description: "{event_description}"

Return ONLY a JSON object with exactly these keys:
- "event_style": Must be exactly either "Formal" or "Casual". Choose "Formal" for weddings, interviews, office meetings, or high-end dinners, and "Casual" for informal gatherings, sports events, or casual hangouts.
- "occasion_type": A short title for the type of occasion (e.g., "Interview", "Wedding", "Office Meeting", "Date Night", "Casual Outing", etc.).
- "reasoning": A 1-sentence explanation of why you selected this style.

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
            
            required_keys = ["event_style", "occasion_type", "reasoning"]
            if (all(key in result for key in required_keys) and 
                    result["event_style"] in ["Formal", "Casual"]):
                return result
            else:
                return fallback_dict
                
        except Exception as e:
            print(f"ACTUAL ERROR (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    print("All retry attempts failed, using fallback.")
    return fallback_dict