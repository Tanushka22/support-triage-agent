"""API request and response models"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TicketRequest(BaseModel):
    """Request model for ticket triage"""
    ticket_id: Optional[str] = Field(None, description="Unique ticket ID (auto-generated if not provided)")
    user_id: str = Field(..., description="User ID from your system")
    query: str = Field(..., min_length=1, max_length=5000, description="The support ticket text")
    user_email: Optional[str] = Field(None, description="User's email address")
    user_name: Optional[str] = Field(None, description="User's name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_1234",
                "query": "Why was I charged $199 when my plan is $99?",
                "user_email": "john@example.com",
                "user_name": "John Doe"
            }
        }

class TicketResponse(BaseModel):
    """Response model for ticket triage"""
    ticket_id: str
    user_id: str
    
    # Classification results
    intent: str = Field(..., description="Classified intent: billing, technical, account, sales, general")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Why this classification was chosen")
    
    # Extracted entities
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities from the query")
    
    # Routing decision
    action: str = Field(..., description="Action to take: auto_resolve or escalate")
    team: Optional[str] = Field(None, description="Team to escalate to (if action=escalate)")
    priority: str = Field(..., description="Priority: low, medium, high, critical")
    
    # Metadata
    timestamp: str
    processing_time_ms: float = Field(..., description="Time taken to process in milliseconds")
    
    # Observability
    trace_url: Optional[str] = Field(None, description="LangSmith trace URL for debugging")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "ticket_001",
                "user_id": "user_1234",
                "intent": "billing",
                "confidence": 0.95,
                "reasoning": "Clear billing inquiry about unexpected charge",
                "entities": {"amount": 199.0, "order_id": None},
                "action": "escalate",
                "team": "billing_tier1",
                "priority": "medium",
                "timestamp": "2024-12-28T10:30:00Z",
                "processing_time_ms": 1250.5,
                "trace_url": "https://smith.langchain.com/..."
            }
        }

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    langsmith_connected: bool

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: str