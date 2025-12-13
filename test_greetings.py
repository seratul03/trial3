"""
Test script to verify chatbot greeting responses
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_chat(query):
    """Send a chat query and get response"""
    url = f"{BASE_URL}/chat"
    payload = {"query": query}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'No response')
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# Test greetings
print("=" * 60)
print("TESTING CHATBOT GREETINGS")
print("=" * 60)

test_queries = [
    "hi",
    "hello",
    "hey",
    "good morning",
    "namaste",
    "Hi, how are you?",
    "Hello there",
]

for query in test_queries:
    print(f"\nQuery: {query}")
    print("-" * 60)
    response = test_chat(query)
    print(f"Response: {response}")
    print()

print("=" * 60)
print("Testing a knowledge-based question:")
print("=" * 60)
response = test_chat("What are the admission dates?")
print(f"Query: What are the admission dates?")
print(f"Response: {response}")
