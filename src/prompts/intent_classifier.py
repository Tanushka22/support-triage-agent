"""Prompts for intent classification"""

INTENT_CLASSIFICATION_SYSTEM = """You are an expert customer support ticket classifier.

Your job is to classify incoming support tickets into one of these categories:

**billing** - Payment issues, refunds, invoices, subscription changes, pricing questions
**technical** - Bugs, errors, performance issues, feature not working, API problems  
**account** - Login issues, password resets, profile changes, account deletion
**sales** - Pricing inquiries, plan comparisons, upgrades, demos, pre-sales questions
**general** - Everything else, vague requests, or unclear intent

Important guidelines:
- Choose the MOST SPECIFIC category that fits
- If a ticket mentions multiple issues, pick the PRIMARY concern
- For ambiguous tickets, default to "general"
- Provide a confidence score (0.0 to 1.0)
- Explain your reasoning briefly

Respond in JSON format:
{
  "intent": "category_name",
  "confidence": 0.95,
  "reasoning": "Brief explanation of why you chose this category"
}"""

def get_classification_prompt(query: str, user_context: dict = None) -> str:
    """
    Generate the user prompt for classification.
    
    Args:
        query: The support ticket text
        user_context: Optional user info (for future use)
    """
    prompt = f"""Classify this support ticket:

Ticket: "{query}"
"""
    
    # In future phases, we'll add user context here:
    # if user_context:
    #     prompt += f"\nUser tier: {user_context.get('tier')}"
    #     prompt += f"\nPrevious tickets: {user_context.get('ticket_count')}"
    
    prompt += "\nProvide your classification in JSON format."
    
    return prompt