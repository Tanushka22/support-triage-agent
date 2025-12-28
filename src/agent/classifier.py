"""Intent classification node with observability"""
import json
import os
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langsmith import traceable

from src.agent.state import TicketState, IntentType
from src.prompts.intent_classifier import (
    INTENT_CLASSIFICATION_SYSTEM,
    get_classification_prompt
)

# Load environment variables FIRST
load_dotenv()

# NOW initialize the LLM after env vars are loaded
llm = ChatAnthropic(
    model=os.getenv("DEFAULT_MODEL", "claude-sonnet-4-20250514"),
    temperature=0,  # Deterministic for classification
    api_key=os.getenv("ANTHROPIC_API_KEY")  # Explicitly pass the key
)

@traceable(
    name="classify_intent",
    metadata={"step": "classification", "version": "v1.0"}
)
def classify_intent(state: TicketState) -> TicketState:
    """
    Classify the intent of a support ticket.
    
    This function is automatically traced by LangSmith via @traceable decorator.
    All LLM calls, inputs, outputs, and timing will be captured.
    """
    
    print(f"\n{'='*60}")
    print(f"🔍 Classifying ticket: {state['ticket_id']}")
    print(f"📝 Query: {state['query'][:100]}...")
    print(f"{'='*60}\n")
    
    # Prepare messages
    messages = [
        SystemMessage(content=INTENT_CLASSIFICATION_SYSTEM),
        HumanMessage(content=get_classification_prompt(state["query"]))
    ]
    
    try:
        # Invoke LLM - this call is automatically traced
        response = llm.invoke(messages)
        
        # Parse JSON response
        # Claude sometimes wraps JSON in markdown, so let's handle that
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        
        # Validate intent
        valid_intents = ["billing", "technical", "account", "sales", "general"]
        intent = result.get("intent", "general")
        if intent not in valid_intents:
            print(f"⚠️  Invalid intent '{intent}', defaulting to 'general'")
            intent = "general"
        
        confidence = float(result.get("confidence", 0.5))
        reasoning = result.get("reasoning", "No reasoning provided")
        
        # Log results
        print(f"✅ Classification complete:")
        print(f"   Intent: {intent}")
        print(f"   Confidence: {confidence:.2%}")
        print(f"   Reasoning: {reasoning}")
        
        # Update state with results
        state["intent"] = intent
        state["confidence"] = confidence
        state["reasoning"] = reasoning
        state["model_used"] = os.getenv("DEFAULT_MODEL", "claude-sonnet-4-20250514")
        
        # Track token usage from response metadata
        if hasattr(response, 'response_metadata'):
            usage = response.response_metadata.get('usage', {})
            state["total_tokens"] = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            print(f"   Tokens used: {state['total_tokens']}")
        
        return state
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        print(f"   Raw response: {response.content[:200]}...")
        
        # Fallback to general with low confidence
        state["intent"] = "general"
        state["confidence"] = 0.3
        state["reasoning"] = f"JSON parse error: {str(e)}"
        return state
        
    except Exception as e:
        print(f"❌ Classification error: {e}")
        
        # Fallback
        state["intent"] = "general"
        state["confidence"] = 0.0
        state["reasoning"] = f"Error: {str(e)}"
        return state

def validate_classification(state: TicketState, ground_truth: str = None) -> Dict:
    """
    Validate classification against ground truth.
    Used for evaluation and measuring accuracy.
    """
    if not ground_truth:
        return {"validated": False}
    
    is_correct = state["intent"] == ground_truth
    
    result = {
        "validated": True,
        "correct": is_correct,
        "predicted": state["intent"],
        "actual": ground_truth,
        "confidence": state["confidence"]
    }
    
    if is_correct:
        print(f"✅ Correct classification!")
    else:
        print(f"❌ Misclassification: predicted '{state['intent']}', actual '{ground_truth}'")
    
    return result