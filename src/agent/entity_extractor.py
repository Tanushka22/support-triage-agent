"""Extract entities from support tickets"""
import json
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langsmith import traceable

from src.agent.state import TicketState

load_dotenv()

llm = ChatAnthropic(
    model=os.getenv("DEFAULT_MODEL", "claude-sonnet-4-20250514"),
    temperature=0,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

ENTITY_EXTRACTION_SYSTEM = """You are an expert at extracting structured information from support tickets.

Extract the following entities if present:
- order_id: Order or transaction numbers (format: #12345 or 12345)
- amount: Dollar amounts mentioned (format: $99 or 99)
- product_name: Specific products or features mentioned
- error_message: Specific error codes or messages
- urgency_keywords: Words indicating urgency (urgent, asap, emergency, critical, down)

Return JSON format:
{
  "order_id": "12345" or null,
  "amount": 99.00 or null,
  "product_name": "string" or null,
  "error_message": "string" or null,
  "urgency_keywords": ["urgent", "critical"] or [],
  "has_urgent_language": true/false
}"""

@traceable(name="extract_entities", metadata={"step": "entity_extraction"})
def extract_entities(state: TicketState) -> TicketState:
    """
    Extract structured entities from the ticket query.
    """
    print(f"\n{'='*60}")
    print(f"🔍 Extracting entities from ticket...")
    print(f"{'='*60}\n")
    
    messages = [
        SystemMessage(content=ENTITY_EXTRACTION_SYSTEM),
        HumanMessage(content=f"Extract entities from: \"{state['query']}\"")
    ]
    
    try:
        response = llm.invoke(messages)
        
        # Parse JSON
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
        
        entities = json.loads(content)
        
        print(f"✅ Entities extracted:")
        for key, value in entities.items():
            if value:
                print(f"   {key}: {value}")
        
        # Add entities to state
        state["entities"] = entities
        
        return state
        
    except Exception as e:
        print(f"❌ Entity extraction error: {e}")
        state["entities"] = {}
        return state