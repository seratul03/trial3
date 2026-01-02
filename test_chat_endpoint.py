"""
Quick test to verify the /chat endpoint returns scholarship data correctly
Run this while the server is running on port 8081
"""

import requests
import json

# Test queries
test_queries = [
    "tell me about post matric scholarship",
    "what is mcm?",
    "general query about college"
]

print("=" * 70)
print("TESTING /chat ENDPOINT FOR SCHOLARSHIP RESPONSES")
print("=" * 70)
print("\nMake sure the server is running: python new_app.py")
print("Testing endpoint: http://localhost:8081/chat")
print()

for query in test_queries:
    print(f"\n📝 Query: '{query}'")
    print("-" * 70)
    
    try:
        response = requests.post(
            "http://localhost:8081/chat",
            json={"query": query},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"   Intent: {data.get('intent')}")
            print(f"   Has Link: {data.get('has_scholarship_link', False)}")
            
            if data.get('has_scholarship_link'):
                print(f"   Slug: {data.get('scholarship_slug')}")
                print(f"   Name: {data.get('scholarship_name')}")
                print(f"   Response Preview: {data.get('response', '')[:100]}...")
                print("\n   🎯 SCHOLARSHIP LINK SHOULD BE SHOWN!")
            else:
                print(f"   Response Preview: {data.get('response', '')[:100]}...")
                print("\n   📄 Regular response (no special link)")
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server!")
        print("   Make sure the server is running: python new_app.py")
        break
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print("\nIf scholarship queries show 'Has Link: True', the backend is working!")
print("If links still don't show in browser, check browser console for errors.")
