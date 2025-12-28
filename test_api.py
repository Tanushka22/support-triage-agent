"""Test the API endpoints"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*70)
    print("Testing /health endpoint")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_single_ticket():
    """Test single ticket triage"""
    print("\n" + "="*70)
    print("Testing /triage endpoint (single ticket)")
    print("="*70)
    
    ticket = {
        "user_id": "user_1234",
        "query": "Why was I charged $199 when my plan is $99?",
        "user_email": "john@example.com",
        "user_name": "John Doe"
    }
    
    response = requests.post(f"{BASE_URL}/triage", json=ticket)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
        
        print(f"\n✅ Ticket Triaged:")
        print(f"   Intent: {result['intent']} ({result['confidence']:.0%})")
        print(f"   Action: {result['action']}")
        print(f"   Team: {result.get('team', 'N/A')}")
        print(f"   Priority: {result['priority']}")
        print(f"   Processing time: {result['processing_time_ms']:.0f}ms")
    else:
        print(f"Error: {response.text}")

def test_batch():
    """Test batch triage"""
    print("\n" + "="*70)
    print("Testing /triage/batch endpoint")
    print("="*70)
    
    tickets = [
        {
            "user_id": "user_1234",
            "query": "I need a refund for order #12345"
        },
        {
            "user_id": "user_5678",
            "query": "The dashboard won't load"
        },
        {
            "user_id": "user_9012",
            "query": "How do I reset my password?"
        }
    ]
    
    response = requests.post(f"{BASE_URL}/triage/batch", json=tickets)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total: {result['total']}, Processed: {result['processed']}")
        
        for i, ticket_result in enumerate(result['results'], 1):
            print(f"\n  Ticket {i}:")
            print(f"    Intent: {ticket_result['intent']}")
            print(f"    Action: {ticket_result['action']}")
            print(f"    Priority: {ticket_result['priority']}")
    else:
        print(f"Error: {response.text}")

def test_invalid_request():
    """Test error handling"""
    print("\n" + "="*70)
    print("Testing error handling")
    print("="*70)
    
    # Missing required field
    invalid_ticket = {
        "user_id": "user_1234"
        # Missing 'query' field
    }
    
    response = requests.post(f"{BASE_URL}/triage", json=invalid_ticket)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("\n🧪 API Testing Suite")
    print("Make sure the API is running: python run_api.py")
    print()
    
    try:
        test_health()
        test_single_ticket()
        test_batch()
        test_invalid_request()
        
        print("\n" + "="*70)
        print("✅ All tests completed!")
        print("="*70 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("   Make sure the server is running: python run_api.py")
        print()
