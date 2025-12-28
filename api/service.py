"""FastAPI service for support triage agent"""
import os
import time
import uuid
from datetime import datetime
from typing import Optional
from contextvars import ContextVar

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langsmith import Client
from langsmith.run_helpers import get_current_run_tree

from api.models import TicketRequest, TicketResponse, HealthResponse, ErrorResponse
from src.agent.graph import agent
from src.agent.state import TicketState

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Support Triage Agent API",
    description="AI-powered customer support ticket classification and routing with full observability",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LangSmith client
langsmith_client = Client() if os.getenv("LANGCHAIN_API_KEY") else None

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "Support Triage Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    
    # Check if LangSmith is configured
    langsmith_configured = bool(
        os.getenv("LANGCHAIN_API_KEY") and 
        os.getenv("LANGCHAIN_TRACING_V2") == "true"
    )
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        langsmith_connected=langsmith_configured
    )

def get_trace_url(run_id: str) -> Optional[str]:
    """Construct LangSmith trace URL from run ID"""
    if not run_id or not langsmith_client:
        return None
    
    project_name = os.getenv("LANGCHAIN_PROJECT", "support-triage-agent")
    
    # LangSmith trace URL format
    return f"https://smith.langchain.com/public/{run_id}/r"

@app.post("/triage", response_model=TicketResponse, tags=["Triage"])
async def triage_ticket(ticket: TicketRequest):
    """
    Triage a support ticket
    
    This endpoint:
    1. Classifies the ticket intent
    2. Extracts entities (amounts, order IDs, etc.)
    3. Retrieves relevant context from CRM and knowledge base
    4. Makes routing decision (auto-resolve vs escalate)
    5. Returns complete triage results
    
    All processing is automatically traced in LangSmith for observability.
    """
    
    start_time = time.time()
    
    # Generate ticket ID if not provided
    ticket_id = ticket.ticket_id or f"ticket_{uuid.uuid4().hex[:8]}"
    
    try:
        # Create initial state
        initial_state: TicketState = {
            "ticket_id": ticket_id,
            "user_id": ticket.user_id,
            "query": ticket.query,
            "user_email": ticket.user_email,
            "user_name": ticket.user_name,
            "intent": None,
            "confidence": None,
            "reasoning": None,
            "entities": None,
            "context": None,
            "action": None,
            "team": None,
            "priority": None,
            "response": None,
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": "",
            "total_tokens": 0
        }
        
        # Run the agent graph with metadata
        config = {
            "metadata": {
                "ticket_id": ticket_id,
                "user_id": ticket.user_id,
                "api_version": "1.0.0"
            },
            "tags": ["api", "production"]
        }
        
        final_state = agent.invoke(initial_state, config=config)
        
        # Try to get the trace URL
        trace_url = None
        try:
            run_tree = get_current_run_tree()
            if run_tree and run_tree.id:
                trace_url = get_trace_url(str(run_tree.id))
        except:
            # If we can't get run tree, that's okay
            pass
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Build response
        response = TicketResponse(
            ticket_id=final_state["ticket_id"],
            user_id=final_state["user_id"],
            intent=final_state["intent"],
            confidence=final_state["confidence"],
            reasoning=final_state["reasoning"],
            entities=final_state.get("entities", {}),
            action=final_state["action"],
            team=final_state.get("team"),
            priority=final_state["priority"],
            timestamp=final_state["timestamp"],
            processing_time_ms=processing_time_ms,
            trace_url=trace_url
        )
        
        return response
        
    except Exception as e:
        # Log error and return 500
        print(f"Error processing ticket {ticket_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process ticket: {str(e)}"
        )

@app.post("/triage/batch", tags=["Triage"])
async def triage_batch(tickets: list[TicketRequest]):
    """
    Triage multiple tickets in batch
    
    Processes up to 10 tickets at once.
    """
    
    if len(tickets) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 tickets per batch request"
        )
    
    results = []
    
    for ticket in tickets:
        try:
            result = await triage_ticket(ticket)
            results.append(result)
        except Exception as e:
            # Continue processing other tickets even if one fails
            results.append({
                "ticket_id": ticket.ticket_id or "unknown",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    return {
        "total": len(tickets),
        "processed": len(results),
        "results": results
    }

@app.get("/metrics", tags=["Observability"])
async def get_metrics():
    """
    Get basic metrics
    
    In production, this would connect to your metrics store.
    For now, it returns static info.
    """
    
    return {
        "message": "Detailed metrics available in LangSmith",
        "langsmith_project": os.getenv("LANGCHAIN_PROJECT"),
        "langsmith_url": "https://smith.langchain.com/",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "api.service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )