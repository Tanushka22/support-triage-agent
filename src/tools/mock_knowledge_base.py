"""Mock knowledge base for FAQ retrieval"""
import time
import random
from typing import List, Dict
from langsmith import traceable

# Mock FAQ database
FAQ_DATABASE = {
    "billing": [
        {
            "question": "How do I get a refund?",
            "answer": "Refunds are processed within 5-7 business days. Contact billing@example.com with your order ID.",
            "relevance_score": 0.95
        },
        {
            "question": "Why was I charged twice?",
            "answer": "Double charges are usually pre-authorizations that drop off in 3-5 days. If not, contact us.",
            "relevance_score": 0.90
        },
        {
            "question": "How do I update my payment method?",
            "answer": "Go to Settings > Billing > Payment Methods to update your card.",
            "relevance_score": 0.85
        }
    ],
    "technical": [
        {
            "question": "Why am I getting a 500 error?",
            "answer": "500 errors usually indicate a server issue. Try clearing cache and cookies. If persists, contact support.",
            "relevance_score": 0.92
        },
        {
            "question": "Dashboard won't load",
            "answer": "Try hard refresh (Ctrl+Shift+R). Check if other pages work. May be a temporary outage.",
            "relevance_score": 0.88
        }
    ],
    "account": [
        {
            "question": "How do I reset my password?",
            "answer": "Click 'Forgot Password' on login page. Check your email for reset link.",
            "relevance_score": 0.98
        },
        {
            "question": "How do I change my email?",
            "answer": "Go to Settings > Account > Email to update. You'll need to verify the new email.",
            "relevance_score": 0.95
        }
    ],
    "sales": [
        {
            "question": "What's included in Pro plan?",
            "answer": "Pro includes: 10 projects, 100GB storage, priority support, API access.",
            "relevance_score": 0.93
        }
    ]
}

@traceable(name="kb_search")
def search_knowledge_base(intent: str, query: str, top_k: int = 3) -> List[Dict]:
    """
    Search knowledge base for relevant articles.
    Returns top K most relevant FAQs.
    """
    # Simulate vector search latency
    time.sleep(random.uniform(0.1, 0.2))
    
    print(f"  📚 Searching knowledge base for '{intent}' intent...")
    
    faqs = FAQ_DATABASE.get(intent, [])
    
    if not faqs:
        print(f"     ⚠️  No FAQs found for intent: {intent}")
        return []
    
    # Return top K results (in real system, would use vector similarity)
    results = faqs[:top_k]
    
    print(f"     ✓ Found {len(results)} relevant articles")
    for i, faq in enumerate(results, 1):
        print(f"       {i}. {faq['question']} (score: {faq['relevance_score']:.2f})")
    
    return results

@traceable(name="kb_get_article")
def get_full_article(article_id: str) -> Dict:
    """
    Fetch complete article content.
    """
    time.sleep(random.uniform(0.05, 0.1))
    
    # Mock article retrieval
    return {
        "article_id": article_id,
        "title": "Complete Guide to Refunds",
        "content": "Full article content here...",
        "last_updated": "2024-12-01"
    }