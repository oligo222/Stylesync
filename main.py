import os
import json
from langgraph_workflow import workflow

def run_pipeline(event_description):
    """
    Runs the full recommendation pipeline by invoking the compiled
    LangGraph workflow (Wardrobe -> Context -> Stylist -> Insight).
    
    Parameters:
        event_description (str): Free-text description of the event.
        
    Returns:
        dict: A clean result containing event_analysis, recommendations, and insights.
    """
    initial_state = {"event_description": event_description}
    final_state = workflow.invoke(initial_state)
    
    # Return only the fields Module A actually needs to display
    return {
        "event_analysis": final_state.get("event_info", {}),
        "recommendations": final_state.get("recommendations", []),
        "insights": final_state.get("insights", {})
    }

if __name__ == "__main__":
    description = "Office meeting tomorrow"
    
    print(f"Running pipeline for event: '{description}'...\n")
    
    results = run_pipeline(description)
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file_path = os.path.join(output_dir, "recommendations.json")
    
    try:
        with open(output_file_path, "w") as out_file:
            json.dump(results, out_file, indent=2, default=str)
            
        print(f"\nSuccess! Saved {len(results['recommendations'])} outfit recommendations to:")
        print(os.path.abspath(output_file_path))
        
    except Exception as e:
        print(f"An error occurred while saving the recommendations: {e}")