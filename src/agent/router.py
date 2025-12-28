"""Route tickets based on classification and context"""
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langsmith import traceable
import json

from src.agent.state import TicketState

load_dotenv()

llm = ChatAnthropic(
    model=os.getenv("DEFAULT_MODEL", "claude-sonnet-4-20250514"),
    temperature=0,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

ROUTING_SYSTEM = """You are a support ticket routing expert.

Based on the ticket information, decide:
1. Action: "auto_resolve" (can be handled automatically) or "escalate" (needs human)
2. If escalating, which team: "billing_tier1", "billing_tier2", "technical_tier1", "technical_tier2", "account", "sales"
3. Priority: "low", "medium", "high", "critical"

Consider:
- User tier (enterprise gets priority)
- Urgency keywords
- Complexity of issue
- Previous ticket history
- Confidence of classification

Return JSON:
{
  "action": "auto_resolve" or "escalate",
  "team": "team_name" or null,
  "priority": "low/medium/high/critical",
  "reasoning": "Why this decision"
}"""

@traceable(name="route_ticket", metadata={"step": "routing"})
def route_ticket(state: TicketState) -> TicketState:
    """
    Determine routing decision based on all available context.
    """
    print(f"\n{'='*60}")
    print(f"🎯 Making routing decision...")
    print(f"{'='*60}\n")
    
    # Prepare context summary
    user_tier = state["context"]["user_profile"].get("tier", "unknown")
    has_faqs = len(state["context"].get("relevant_faqs", [])) > 0
    has_urgent_language = state["entities"].get("has_urgent_language", False)
    
    context_summary = f"""
Ticket Info:
- Intent: {state['intent']} (confidence: {state['confidence']:.2f})
- User tier: {user_tier}
- Has relevant FAQs: {has_faqs}
- Urgent language: {has_urgent_language}
- Query: "{state['query']}"
"""
    
    messages = [
        SystemMessage(content=ROUTING_SYSTEM),
        HumanMessage(content=context_summary)
    ]
    
    try:
        response = llm.invoke(messages)
        
        # Parse JSON
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
        
        decision = json.loads(content)
        
        state["action"] = decision["action"]
        state["team"] = decision.get("team")
        state["priority"] = decision["priority"]
        
        print(f"✅ Routing decision:")
        print(f"   Action: {state['action']}")
        if state['team']:
            print(f"   Team: {state['team']}")
        print(f"   Priority: {state['priority']}")
        print(f"   Reasoning: {decision['reasoning']}")
        
        return state
        
    except Exception as e:
        print(f"❌ Routing error: {e}")
        # Safe fallback
        state["action"] = "escalate"
        state["team"] = "general"
        state["priority"] = "medium"
        return state