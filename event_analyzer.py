import os
import json
import re
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

def analyze_event(event_description):
    """
    Analyzes a free-text event description and classifies its style and type.
    
    Uses Gemini 2.5 Flash to extract:
    - event_style: "Formal" or "Casual"
    - occasion_type: a short name like "Interview", "Wedding", etc.
    - reasoning: a single-sentence explanation.
    
    If the API call fails, JSON parsing fails, or the event_style is invalid,
    it returns a default fallback dictionary.
    
    Parameters:
        event_description (str): Free-text description of the event.
        
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
        print(f"ACTUAL ERROR: {e}")
        return fallback_dict

if __name__ == "__main__":
    import time
    
    test_events = [
        "Interview tomorrow",
        "Casual dinner with friends",
        "Wedding next week"
    ]
    
    print("Testing event analyzer...\n")
    for event in test_events:
        print(f"Event: '{event}'")
        analysis = analyze_event(event)
        print(json.dumps(analysis, indent=2))
        print("-" * 40)
        time.sleep(2)