"""Test the complete agent graph"""
import json
from datetime import datetime
from dotenv import load_dotenv

from src.agent.graph import agent
from src.agent.state import TicketState

load_dotenv()

def test_full_agent(ticket_data: dict):
    """Run complete agent flow on a ticket"""
    
    print("\n" + "="*70)
    print(f"🎫 PROCESSING TICKET: {ticket_data['ticket_id']}")
    print("="*70)
    
    # Create initial state
    initial_state: TicketState = {
        "ticket_id": ticket_data["ticket_id"],
        "user_id": ticket_data["user_id"],
        "query": ticket_data["query"],
        "user_email": ticket_data.get("user_email"),
        "user_name": ticket_data.get("user_name"),
        "intent": None,
        "confidence": None,
        "reasoning": None,
        "entities": None,
        "context": None,
        "action": None,
        "team": None,
        "priority": None,
        "response": None,
        "timestamp": datetime.now().isoformat(),
        "model_used": "",
        "total_tokens": 0
    }
    
    # Run the agent graph
    # This single invoke() call runs ALL steps in sequence
    final_state = agent.invoke(initial_state)
    
    print("\n" + "="*70)
    print("📋 FINAL RESULT")
    print("="*70)
    print(f"Intent: {final_state['intent']} ({final_state['confidence']:.0%})")
    print(f"Action: {final_state['action']}")
    if final_state['team']:
        print(f"Team: {final_state['team']}")
    print(f"Priority: {final_state['priority']}")
    print("="*70 + "\n")
    
    return final_state

def test_multiple_tickets():
    """Test agent on multiple tickets"""
    
    # Load test data
    with open("src/data/test_tickets.json", "r") as f:
        test_tickets = json.load(f)
    
    results = []
    
    # Test first 3 tickets
    for ticket in test_tickets[:3]:
        result = test_full_agent(ticket)
        results.append({
            "ticket_id": ticket["ticket_id"],
            "query": ticket["query"],
            "intent_predicted": result["intent"],
            "intent_actual": ticket["intent"],
            "action": result["action"],
            "team": result["team"],
            "priority": result["priority"]
        })
        
        print("\n" + "-"*70 + "\n")
    
    # Save results
    with open("full_agent_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Results saved to full_agent_results.json")
    print(f"🔍 View traces at: https://smith.langchain.com/")

if __name__ == "__main__":
    test_multiple_tickets()