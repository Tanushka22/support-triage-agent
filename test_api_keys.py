"""Test API keys directly"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("Checking API Keys...\n")

# Check Anthropic
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
print(f"ANTHROPIC_API_KEY: {anthropic_key[:15] if anthropic_key else 'NOT SET'}...")

if not anthropic_key:
    print("❌ ANTHROPIC_API_KEY is not set!")
elif not anthropic_key.startswith("sk-ant-"):
    print("❌ ANTHROPIC_API_KEY format looks wrong (should start with 'sk-ant-')")
else:
    print("✅ ANTHROPIC_API_KEY format looks correct")

# Check LangSmith
langsmith_key = os.getenv("LANGCHAIN_API_KEY")
print(f"\nLANGCHAIN_API_KEY: {langsmith_key[:15] if langsmith_key else 'NOT SET'}...")

if not langsmith_key:
    print("❌ LANGCHAIN_API_KEY is not set!")
elif not langsmith_key.startswith("lsv2_"):
    print("❌ LANGCHAIN_API_KEY format looks wrong (should start with 'lsv2_')")
else:
    print("✅ LANGCHAIN_API_KEY format looks correct")

# Test Anthropic API
print("\n" + "="*50)
print("Testing Anthropic API...")
print("="*50)

try:
    from anthropic import Anthropic
    client = Anthropic(api_key=anthropic_key)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=20,
        messages=[
            {"role": "user", "content": "Say 'API works' and nothing else"}
        ]
    )
    
    print(f"✅ Anthropic API working! Response: {message.content[0].text}")
    
except Exception as e:
    print(f"❌ Anthropic API error: {e}")

print("\n" + "="*50)
print("If both keys look correct, run: python test_classifier.py")
print("="*50)

