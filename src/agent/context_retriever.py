"""Retrieve context from CRM and knowledge base"""
from langsmith import traceable
from src.agent.state import TicketState
from src.tools.mock_crm import get_user_profile, get_order_history, get_ticket_history
from src.tools.mock_knowledge_base import search_knowledge_base

@traceable(name="retrieve_context", metadata={"step": "context_retrieval"})
def retrieve_context(state: TicketState) -> TicketState:
    """
    Fetch relevant context from CRM and knowledge base.
    All sub-calls (CRM, KB) are automatically traced.
    """
    print(f"\n{'='*60}")
    print(f"📊 Retrieving context...")
    print(f"{'='*60}\n")
    
    context = {}
    
    # Get user profile from CRM
    user_profile = get_user_profile(state["user_id"])
    context["user_profile"] = user_profile
    
    # Get order history if billing-related
    if state["intent"] == "billing":
        orders = get_order_history(state["user_id"])
        context["orders"] = orders
    
    # Get ticket history
    ticket_history = get_ticket_history(state["user_id"])
    context["ticket_history"] = ticket_history
    
    # Search knowledge base for relevant FAQs
    faqs = search_knowledge_base(
        intent=state["intent"],
        query=state["query"],
        top_k=2
    )
    context["relevant_faqs"] = faqs
    
    print(f"\n✅ Context retrieved:")
    print(f"   User tier: {user_profile.get('tier')}")
    print(f"   Previous tickets: {len(ticket_history)}")
    print(f"   Relevant FAQs: {len(faqs)}")
    
    # Add context to state
    state["context"] = context
    
    return state