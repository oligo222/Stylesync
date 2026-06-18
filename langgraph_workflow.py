import json
from typing import TypedDict
from langgraph.graph import StateGraph, END

# Import existing functions from our project modules
from event_analyzer import analyze_event
from recommendation_engine import load_wardrobe, generate_outfits
from stylist_agent import score_and_explain
from insights_engine import load_usage_history, save_usage_history, generate_insights

# =====================================================================
# WHAT IS A STATEGRAPH?
#
# A StateGraph is a way to define workflows as a graph of nodes.
# - Each node represents a function that does some work.
# - The Graph has a central "State" object (defined by TypedDict below).
# - When a node runs, it takes the current State as input, performs logic,
#   and returns a dictionary specifying which state keys it wants to update.
# - The graph then merges those updates into the State and routes execution
#   to the next node according to defined edges.
# =====================================================================

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
# Each function receives the current state, processes it, and returns an updated dictionary.

def wardrobe_node(state: GraphState) -> dict:
    """
    Node 1: Loads the wardrobe data from the JSON file.
    Updates the 'wardrobe' key in the graph state.
    """
    print("[Node: Wardrobe] Loading wardrobe items...")
    wardrobe = load_wardrobe("data/wardrobe.json")
    return {"wardrobe": wardrobe}

def context_node(state: GraphState) -> dict:
    """
    Node 2: Classifies the event description to identify style (Formal/Casual).
    Updates the 'event_info' key in the graph state.
    """
    print(f"[Node: Context] Analyzing event: '{state['event_description']}'...")
    event_info = analyze_event(state["event_description"])
    return {"event_info": event_info}

def stylist_node(state: GraphState) -> dict:
    """
    Node 3: Generates outfits matching the style and evaluates them using Gemini.
    Updates the 'recommendations' key in the graph state.
    """
    event_style = state["event_info"]["event_style"]
    print(f"[Node: Stylist] Generating recommendations for style: {event_style}...")
    
    # Generate matching combinations
    outfits = generate_outfits(state["wardrobe"], event_style)
    
    combined_outfits = []
    # Score and explain each generated outfit
    for outfit in outfits:
        evaluation = score_and_explain(outfit, state["event_description"])
        combined = {**outfit, **evaluation}
        combined_outfits.append(combined)
        
    # Sort recommendations by suitability score descending
    combined_outfits.sort(key=lambda x: x.get("suitability_score", 0), reverse=True)
    return {"recommendations": combined_outfits}

def insight_node(state: GraphState) -> dict:
    """
    Node 4: Updates the persistent history with the top-scoring outfit
    and compiles wardrobe insights.
    Updates the 'insights' key in the graph state.
    """
    print("[Node: Insight] Updating usage history and compiling statistics...")
    
    recommendations = state.get("recommendations", [])
    
    # Save top recommendation to history if any exists
    if recommendations:
        top_outfit = recommendations[0]
        # Gather non-None item names to persist in usage history
        items_to_save = [
            top_outfit[key]
            for key in ["top", "bottom", "footwear"]
            if top_outfit.get(key) is not None
        ]
        save_usage_history(items_to_save)
        
    # Load history and generate statistics/insights
    history = load_usage_history()
    insights = generate_insights(state["wardrobe"], history)
    return {"insights": insights}

# 3. Construct the graph workflow
# Initialize the state graph with our defined state schema
builder = StateGraph(GraphState)

# Add all node functions as graph vertices
builder.add_node("wardrobe_node", wardrobe_node)
builder.add_node("context_node", context_node)
builder.add_node("stylist_node", stylist_node)
builder.add_node("insight_node", insight_node)

# Set the starting node of the workflow
builder.set_entry_point("wardrobe_node")

# Wire the nodes together sequentially
builder.add_edge("wardrobe_node", "context_node")
builder.add_edge("context_node", "stylist_node")
builder.add_edge("stylist_node", "insight_node")

# Link the final node to the END symbol to terminate the workflow
builder.add_edge("insight_node", END)

# Compile the workflow builder into an executable graph
workflow = builder.compile()

# 4. Main block for execution and testing
if __name__ == "__main__":
    # Define initial inputs for the graph state
    initial_inputs = {
        "event_description": "Interview tomorrow"
    }
    
    print("Starting LangGraph Wardrobe Workflow...\n")
    
    # Run the compiled StateGraph workflow synchronously
    final_state = workflow.invoke(initial_inputs)
    
    print("\n--- Final Graph State ---")
    # Print state formatted as JSON, using default=str as a fallback for any non-serializable objects
    print(json.dumps(final_state, indent=2, default=str))
