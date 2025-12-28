"""State schema for the support triage agent"""
from typing import TypedDict, Literal, Optional, Dict, Any

class TicketState(TypedDict):
    """
    State that flows through the agent graph.
    """
    # Input data
    ticket_id: str
    user_id: str
    query: str
    user_email: Optional[str]
    user_name: Optional[str]
    
    # Classification results
    intent: Optional[str]
    confidence: Optional[float]
    reasoning: Optional[str]
    
    # NEW: Entity extraction results
    entities: Optional[Dict[str, Any]]
    
    # NEW: Retrieved context
    context: Optional[Dict[str, Any]]
    
    # NEW: Routing decision
    action: Optional[Literal["auto_resolve", "escalate"]]
    team: Optional[str]
    priority: Optional[str]
    response: Optional[str]
    
    # Metadata
    timestamp: str
    model_used: str
    total_tokens: int

IntentType = Literal["billing", "technical", "account", "sales", "general"]
ActionType = Literal["auto_resolve", "escalate"]