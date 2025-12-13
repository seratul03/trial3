import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_url = os.environ.get('GEMINI_API_URL')
api_key = os.environ.get('GEMINI_API_KEY')

print(f"API URL: {api_url}")
print(f"API KEY: {api_key[:20]}...")

# Simple test
test_prompt = """You are a campus assistant.

AVAILABLE KNOWLEDGE:
[Source: sem_explain/sem_01/BSCM101.json]
Subject: Semiconductor Physics
Code: BSCM101
Summary: Semiconductor Physics introduces the quantum mechanical principles governing modern electronic devices.
Modules (5):
  - Module 1: Introduction to Quantum Mechanics
  - Module 2: Electronic materials
  - Module 3: Semiconductors

USER QUESTION: Tell me about BSCM101

Answer based ONLY on the provided knowledge base above."""

headers = {
    'Content-Type': 'application/json',
    'X-goog-api-key': api_key
}

payload = {
    "contents": [
        {
            "parts": [
                {"text": test_prompt}
            ]
        }
    ]
}

print("\nSending request to Gemini...")
print(f"Prompt length: {len(test_prompt)} chars")

try:
    response = requests.post(api_url, headers=headers, json=payload, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    
    result = response.json()
    print(f"\nFull Response:")
    print(json.dumps(result, indent=2)[:1000])
    
    # Extract answer
    candidates = result.get('candidates', [])
    if candidates and 'content' in candidates[0] and 'parts' in candidates[0]['content']:
        answer = candidates[0]['content']['parts'][0].get('text', '')
        print(f"\n✓ Extracted Answer ({len(answer)} chars):")
        print(answer)
    else:
        print("\n✗ No answer found in response")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
