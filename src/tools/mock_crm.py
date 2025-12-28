"""Mock CRM system for testing"""
import time
import random
from typing import Dict, Optional
from langsmith import traceable

# Mock user database
MOCK_USERS = {
    "user_1234": {
        "user_id": "user_1234",
        "name": "John Doe",
        "email": "john@example.com",
        "tier": "pro",
        "account_status": "active",
        "total_tickets": 3,
        "last_ticket_date": "2024-12-15",
        "lifetime_value": 1200,
        "current_plan": "Pro Monthly ($99/mo)"
    },
    "user_5678": {
        "user_id": "user_5678",
        "name": "Jane Smith",
        "email": "jane@example.com",
        "tier": "enterprise",
        "account_status": "active",
        "total_tickets": 12,
        "last_ticket_date": "2024-12-20",
        "lifetime_value": 15000,
        "current_plan": "Enterprise Annual ($199/mo)"
    },
    "user_9012": {
        "user_id": "user_9012",
        "name": "Bob Johnson",
        "email": "bob@example.com",
        "tier": "free",
        "account_status": "active",
        "total_tickets": 1,
        "last_ticket_date": "2024-12-01",
        "lifetime_value": 0,
        "current_plan": "Free Plan"
    }
}

# Mock order history
MOCK_ORDERS = {
    "user_1234": [
        {"order_id": "12345", "amount": 99, "date": "2024-12-01", "status": "completed"},
        {"order_id": "12346", "amount": 99, "date": "2024-11-01", "status": "completed"},
    ],
    "user_5678": [
        {"order_id": "12347", "amount": 199, "date": "2024-12-01", "status": "completed"},
    ]
}

@traceable(name="crm_get_user")
def get_user_profile(user_id: str) -> Optional[Dict]:
    """
    Fetch user profile from CRM.
    This is traced as a separate step in LangSmith.
    """
    # Simulate API latency
    time.sleep(random.uniform(0.1, 0.3))
    
    print(f"  📊 Fetching CRM data for {user_id}...")
    
    user = MOCK_USERS.get(user_id)
    
    if user:
        print(f"     ✓ Found user: {user['name']} ({user['tier']} tier)")
        return user
    else:
        print(f"     ⚠️  User not found in CRM")
        # Return minimal data for unknown users
        return {
            "user_id": user_id,
            "name": "Unknown User",
            "tier": "free",
            "account_status": "unknown",
            "total_tickets": 0
        }

@traceable(name="crm_get_orders")
def get_order_history(user_id: str) -> list:
    """
    Fetch user's order history.
    """
    time.sleep(random.uniform(0.05, 0.15))
    
    print(f"  💳 Fetching order history for {user_id}...")
    
    orders = MOCK_ORDERS.get(user_id, [])
    
    if orders:
        print(f"     ✓ Found {len(orders)} orders")
    else:
        print(f"     ⚠️  No orders found")
    
    return orders

@traceable(name="crm_get_ticket_history")
def get_ticket_history(user_id: str) -> list:
    """
    Fetch user's previous support tickets.
    """
    time.sleep(random.uniform(0.05, 0.15))
    
    print(f"  🎫 Fetching ticket history for {user_id}...")
    
    # Mock recent tickets
    mock_tickets = [
        {"ticket_id": "old_001", "intent": "billing", "resolved": True, "date": "2024-12-10"},
        {"ticket_id": "old_002", "intent": "technical", "resolved": True, "date": "2024-12-15"},
    ]
    
    print(f"     ✓ Found {len(mock_tickets)} previous tickets")
    
    return mock_tickets