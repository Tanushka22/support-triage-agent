"""Complete agent graph using LangGraph"""
from langgraph.graph import StateGraph, END
from src.agent.state import TicketState
from src.agent.classifier import classify_intent
from src.agent.entity_extractor import extract_entities
from src.agent.context_retriever import retrieve_context
from src.agent.router import route_ticket

def build_agent_graph():
    """
    Build the complete support triage agent graph.
    
    Flow:
    START → classify → extract → retrieve → route → END
    """
    
    # Create graph
    workflow = StateGraph(TicketState)
    
    # Add nodes
    workflow.add_node("classify", classify_intent)
    workflow.add_node("extract", extract_entities)
    workflow.add_node("retrieve", retrieve_context)
    workflow.add_node("route", route_ticket)
    
    # Define edges (sequential flow for now)
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "extract")
    workflow.add_edge("extract", "retrieve")
    workflow.add_edge("retrieve", "route")
    workflow.add_edge("route", END)
    
    # Compile
    agent = workflow.compile()
    
    return agent

# Create the agent instance
agent = build_agent_graph()