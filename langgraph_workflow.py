import json
from typing import TypedDict
from langgraph.graph import StateGraph, END

# Import existing functions from our project modules
from event_analyzer import analyze_event
from recommendation_engine import load_wardrobe, generate_outfits
from wardrobe_adapter import load_and_adapt
from stylist_agent import score_and_explain
from insights_engine import load_usage_history, save_usage_history, generate_insights

# 1. Define the State schema using TypedDict
class GraphState(TypedDict):
    """
    Defines the shared state of the workflow graph.
    Each key holds a piece of information that can be accessed and
    updated by different node functions.
    """
    event_description: str     # The user's input describing the event
    event_info: dict            # Style classification from event_analyzer
    wardrobe: list             # Loaded list of wardrobe items
    recommendations: list      # List of evaluated and sorted outfit recommendations
    insights: dict             # Rule-based insights generated from wardrobe/history

# 2. Define the node functions.
def wardrobe_node(state: GraphState) -> dict:
    """
    Node 1: Loads the wardrobe data and adapts it using the new adapter.
    Reads Module B's file ("wardrobe.json") and falls back to Module C's 
    mock data ("data/wardrobe.json") if categories are missing.
    """
    print("[Node: Wardrobe] Loading and adapting wardrobe items...")
    
    # Read from Module B's file path
    scanned = load_and_adapt("wardrobe.json")["items"]
    
    categories_present = {item["category"] for item in scanned}
    required = {"Top", "Bottom", "Footwear"}
    
    if required.issubset(categories_present):
        print("[Node: Wardrobe] Using scanned wardrobe.")
        return {"wardrobe": scanned}
        
    print("[Node: Wardrobe] Scanned wardrobe incomplete, falling back to mock data.")
    # Fallback to Module C's mock data path
    wardrobe = load_wardrobe("data/wardrobe.json")
    return {"wardrobe": wardrobe}

def context_node(state: GraphState) -> dict:
    """
    Node 2: Classifies the event description to identify style (Formal/Casual).
    """
    print(f"[Node: Context] Analyzing event: '{state['event_description']}'...")
    event_info = analyze_event(state["event_description"])
    return {"event_info": event_info}

def stylist_node(state: GraphState) -> dict:
    """
    Node 3: Generates outfits matching the style and evaluates them using Gemini.
    """
    event_style = state["event_info"]["event_style"]
    print(f"[Node: Stylist] Generating recommendations for style: {event_style}...")
    
    outfits = generate_outfits(state["wardrobe"], event_style)
    
    combined_outfits = []
    for outfit in outfits:
        evaluation = score_and_explain(outfit, state["event_description"])
        combined = {**outfit, **evaluation}
        combined_outfits.append(combined)
        
    combined_outfits.sort(key=lambda x: x.get("suitability_score", 0), reverse=True)
    return {"recommendations": combined_outfits}

def insight_node(state: GraphState) -> dict:
    """
    Node 4: Updates the persistent history with the top-scoring outfit
    and compiles wardrobe insights.
    """
    print("[Node: Insight] Updating usage history and compiling statistics...")
    
    recommendations = state.get("recommendations", [])
    if recommendations:
        top_outfit = recommendations[0]
        items_to_save = [
            top_outfit[key]
            for key in ["top", "bottom", "footwear"]
            if top_outfit.get(key) is not None
         ]
        top_score = top_outfit.get("suitability_score")
        save_usage_history(items_to_save, score=top_score)
        
    history = load_usage_history()
    insights = generate_insights(state["wardrobe"], history)
    return {"insights": insights}

# 3. Construct the graph workflow
builder = StateGraph(GraphState)

builder.add_node("wardrobe_node", wardrobe_node)
builder.add_node("context_node", context_node)
builder.add_node("stylist_node", stylist_node)
builder.add_node("insight_node", insight_node)

builder.set_entry_point("wardrobe_node")

builder.add_edge("wardrobe_node", "context_node")
builder.add_edge("context_node", "stylist_node")
builder.add_edge("stylist_node", "insight_node")
builder.add_edge("insight_node", END)

workflow = builder.compile()

# 4. Main block for execution and testing
if __name__ == "__main__":
    initial_inputs = {
        "event_description": "Interview tomorrow"
    }
    
    print("Starting LangGraph Wardrobe Workflow...\n")
    final_state = workflow.invoke(initial_inputs)
    
    print("\n--- Final Graph State ---")
    print(json.dumps(final_state, indent=2, default=str))
