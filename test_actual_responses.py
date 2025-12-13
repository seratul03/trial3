"""Test actual AI responses to various queries"""

import requests
import json

# Base URL for the Flask app
BASE_URL = "http://localhost:5000"

def test_query(query):
    """Send a query to the chat endpoint and show the response"""
    print(f"\n{'='*80}")
    print(f"QUERY: {query}")
    print(f"{'='*80}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"RESPONSE:\n{data.get('response', 'No response')}")
            print(f"\nSOURCES: {data.get('sources', [])}")
        else:
            print(f"ERROR: Status code {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Flask app. Make sure it's running on port 5000")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Test various query types
    queries = [
        "Who is the HOD of CSE?",
        "Tell me about faculty",
        "What are the subjects in semester 1?",
        "What are the hostel rules?",
        "Tell me about library timing",
        "When are the exams?",
        "Tell me about Kanyashree scholarship"
    ]
    
    print("="*80)
    print("TESTING ACTUAL AI RESPONSES")
    print("="*80)
    
    for query in queries:
        test_query(query)
    
    print(f"\n{'='*80}")
    print("TESTS COMPLETE")
    print("="*80)
