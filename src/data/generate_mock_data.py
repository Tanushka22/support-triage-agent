"""Generate mock support tickets for testing"""
from faker import Faker
import json
import random

fake = Faker()

INTENTS = ["billing", "technical", "account", "sales", "general"]

TICKET_TEMPLATES = {
    "billing": [
        "Why was I charged ${amount} when my plan is ${plan_price}?",
        "I need a refund for order #{order_id}",
        "My payment method declined but I was still charged",
        "Can I get an invoice for last month?",
        "I was double charged on {date}",
    ],
    "technical": [
        "I'm getting a 500 error when I try to login",
        "The dashboard won't load",
        "My API calls are timing out",
        "I can't upload files larger than 10MB",
        "Getting 'permission denied' error",
    ],
    "account": [
        "I can't reset my password",
        "How do I change my email address?",
        "I need to delete my account",
        "Can you help me update my profile?",
        "I'm locked out of my account",
    ],
    "sales": [
        "What's the difference between Pro and Enterprise plans?",
        "Do you offer non-profit discounts?",
        "Can I get a demo?",
        "I want to upgrade to annual billing",
        "What features are included in the Business plan?",
    ],
    "general": [
        "This isn't working",
        "I have a question",
        "Can someone help me?",
        "I need assistance",
        "What's your refund policy?",
    ]
}

def generate_ticket(intent=None):
    """Generate a single mock ticket"""
    if not intent:
        intent = random.choice(INTENTS)
    
    template = random.choice(TICKET_TEMPLATES[intent])
    
    # Fill in template variables
    query = template.format(
        amount=random.randint(50, 500),
        plan_price=random.choice([49, 99, 199]),
        order_id=random.randint(10000, 99999),
        date=fake.date_this_month()
    )
    
    return {
        "ticket_id": fake.uuid4(),
        "user_id": f"user_{random.randint(1000, 9999)}",
        "query": query,
        "intent": intent,  # Ground truth
        "created_at": fake.date_time_this_month().isoformat(),
        "user_email": fake.email(),
        "user_name": fake.name()
    }

def generate_test_set(num_tickets=20):
    """Generate a balanced test set"""
    tickets = []
    tickets_per_intent = num_tickets // len(INTENTS)
    
    for intent in INTENTS:
        for _ in range(tickets_per_intent):
            tickets.append(generate_ticket(intent))
    
    return tickets

if __name__ == "__main__":
    # Generate 20 test tickets
    test_tickets = generate_test_set(20)
    
    # Save to JSON
    with open("src/data/test_tickets.json", "w") as f:
        json.dump(test_tickets, f, indent=2)
    
    print(f"✓ Generated {len(test_tickets)} test tickets")
    print(f"✓ Saved to src/data/test_tickets.json")
    
    # Print sample
    print("\nSample ticket:")
    print(json.dumps(test_tickets[0], indent=2))