"""
Test the actual chatbot server with real queries
"""
import requests
import json

BASE_URL = "http://localhost:8082"

def test_query(query):
    print("\n" + "="*80)
    print(f"QUERY: {query}")
    print("="*80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nIntent: {data.get('intent', 'N/A')}")
            print(f"\nResponse:")
            print("-"*80)
            print(data.get('response', 'No response'))
            print("-"*80)
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server")
        print("   Please start the server first:")
        print("   python app/app.py")
    except Exception as e:
        print(f"❌ ERROR: {e}")

# Test queries
test_queries = [
    "Who is our HOD?",
    "Who is Dr. Shivnath Ghosh?",
    "Tell me about scholarships",
    "What are the holidays in January?"
]

print("="*80)
print("TESTING CHATBOT SERVER")
print("="*80)
print(f"Server URL: {BASE_URL}")

for query in test_queries:
    test_query(query)

print("\n" + "="*80)
print("✅ TEST COMPLETE")
print("="*80)
