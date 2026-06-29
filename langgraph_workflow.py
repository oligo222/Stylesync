import json
from typing import TypedDict
from langgraph.graph import StateGraph, END

from event_analyzer import analyze_event
from recommendation_engine import load_wardrobe, generate_outfits
from wardrobe_adapter import load_and_adapt
from stylist_agent import score_and_explain
from insights_engine import load_usage_history, save_usage_history, generate_insights

class GraphState(TypedDict):
    event_description: str
    event_info: dict
    wardrobe: list
    recommendations: list
    insights: dict

def wardrobe_node(state: GraphState) -> dict:
    print("[Node: Wardrobe] Loading and adapting wardrobe items...")
    scanned = load_and_adapt("wardrobe.json")["items"]
    print(f"[Node: Wardrobe] Loaded {len(scanned)} items from scanned wardrobe.")
    return {"wardrobe": scanned}

def context_node(state: GraphState) -> dict:
    print(f"[Node: Context] Analyzing event: '{state['event_description']}'...")
    event_info = analyze_event(state["event_description"])
    return {"event_info": event_info}

def stylist_node(state: GraphState) -> dict:
    event_style = state["event_info"]["event_style"]
    print(f"[Node: Stylist] Generating recommendations for style: {event_style}...")

    # Increased from 3 to 6
    outfits = generate_outfits(state["wardrobe"], event_style, max_outfits=6)

    combined_outfits = []
    for outfit in outfits:
        evaluation = score_and_explain(outfit, state["event_description"])
        combined_outfits.append({**outfit, **evaluation})

    combined_outfits.sort(key=lambda x: x.get("suitability_score", 0), reverse=True)
    return {"recommendations": combined_outfits}

def insight_node(state: GraphState) -> dict:
    print("[Node: Insight] Updating usage history and compiling statistics...")

    recommendations = state.get("recommendations", [])
    if recommendations:
        top_outfit = recommendations[0]
        items_to_save = [
            top_outfit[key]
            for key in ["top", "bottom", "footwear"]
            if top_outfit.get(key) is not None
        ]
        save_usage_history(items_to_save, score=top_outfit.get("suitability_score"))

    history = load_usage_history()
    insights = generate_insights(state["wardrobe"], history)
    return {"insights": insights}

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

if __name__ == "__main__":
    initial_inputs = {"event_description": "Weekend brunch with friends"}
    print("Starting LangGraph Wardrobe Workflow...\n")
    final_state = workflow.invoke(initial_inputs)
    print("\n--- Final Graph State ---")
    print(json.dumps(final_state, indent=2, default=str))