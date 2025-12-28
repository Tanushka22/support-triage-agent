"""Test the intent classifier with observability"""
import json
import os
from datetime import datetime
from dotenv import load_dotenv

from src.agent.state import TicketState
from src.agent.classifier import classify_intent, validate_classification

# Load environment variables
load_dotenv()

def test_single_ticket(ticket_data: dict):
    """Test classification on a single ticket"""
    
    # Create initial state
    state: TicketState = {
        "ticket_id": ticket_data["ticket_id"],
        "user_id": ticket_data["user_id"],
        "query": ticket_data["query"],
        "user_email": ticket_data.get("user_email"),
        "user_name": ticket_data.get("user_name"),
        "intent": None,
        "confidence": None,
        "reasoning": None,
        "timestamp": datetime.now().isoformat(),
        "model_used": "",
        "total_tokens": 0
    }
    
    # Run classification
    result_state = classify_intent(state)
    
    # Validate if ground truth available
    ground_truth = ticket_data.get("intent")
    if ground_truth:
        validation = validate_classification(result_state, ground_truth)
        return result_state, validation
    
    return result_state, None

def test_batch():
    """Test on batch of tickets from our test data"""
    
    print("\n" + "="*70)
    print("🧪 TESTING INTENT CLASSIFIER")
    print("="*70)
    
    # Load test tickets
    with open("src/data/test_tickets.json", "r") as f:
        test_tickets = json.load(f)
    
    results = []
    correct = 0
    total = 0
    
    # Test first 5 tickets
    for ticket in test_tickets[:5]:
        print("\n" + "-"*70)
        result_state, validation = test_single_ticket(ticket)
        
        results.append({
            "ticket_id": ticket["ticket_id"],
            "query": ticket["query"],
            "predicted": result_state["intent"],
            "actual": ticket["intent"],
            "confidence": result_state["confidence"],
            "correct": validation["correct"] if validation else None
        })
        
        if validation and validation["correct"]:
            correct += 1
        total += 1
    
    # Summary
    print("\n" + "="*70)
    print("📊 RESULTS SUMMARY")
    print("="*70)
    print(f"Accuracy: {correct}/{total} ({correct/total*100:.1f}%)")
    print(f"\nView detailed traces at: https://smith.langchain.com/")
    print(f"Project: {os.getenv('LANGCHAIN_PROJECT')}")
    print("="*70 + "\n")
    
    return results

if __name__ == "__main__":
    # Run batch test
    results = test_batch()
    
    # Save results
    output_file = "classification_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Results saved to {output_file}")