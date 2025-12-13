import requests
import json
import time

# Wait for server to be ready
print("Waiting for server to start...")
for i in range(10):
    try:
        requests.get("http://127.0.0.1:8000/knowledge-files", timeout=2)
        print("Server is ready!")
        break
    except:
        time.sleep(1)
        print(f"  Waiting... {i+1}/10")
else:
    print("Server not responding. Please start it manually.")
    exit(1)

# Test the knowledge files endpoint
print("\n" + "=" * 60)
print("Testing /knowledge-files endpoint...")
print("=" * 60)

try:
    response = requests.get("http://127.0.0.1:8000/knowledge-files")
    result = response.json()
    print(f"✓ Total files loaded: {result.get('count', 0)}")
    print(f"✓ Prompt file: {result.get('prompt_file', 'N/A')}")
    
    # Find BSCM101
    bscm_files = [f for f in result.get('files', []) if 'BSCM101' in f.get('path', '')]
    if bscm_files:
        print(f"✓ Found BSCM101 files: {[f['path'] for f in bscm_files]}")
    else:
        print("✗ BSCM101 not found in loaded files!")
except Exception as e:
    print(f"✗ Error: {e}")

# Test query-knowledge endpoint
print("\n" + "=" * 60)
print("Testing /query-knowledge endpoint...")
print("=" * 60)

try:
    response = requests.post(
        "http://127.0.0.1:8000/query-knowledge",
        json={"q": "BSCM101", "max_results": 3},
        timeout=5
    )
    result = response.json()
    print(f"✓ Query: {result.get('query')}")
    print(f"✓ Results found: {len(result.get('results', []))}")
    for i, res in enumerate(result.get('results', [])[:3], 1):
        print(f"\n  {i}. {res['path']} (score: {res['score']})")
        print(f"     Snippet: {res['snippet'][:100]}...")
except Exception as e:
    print(f"✗ Error: {e}")

# Test chat endpoint
print("\n" + "=" * 60)
print("Testing Chat Endpoint...")
print("=" * 60)

test_queries = [
    "Tell me about BSCM101",
    "What are the modules in BSCM101?",
]

for query in test_queries:
    print(f"\n📝 Query: {query}")
    print("-" * 60)
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"query": query},
            timeout=30
        )
        result = response.json()
        
        if 'response' in result:
            answer = result['response']
            print(f"🤖 Response ({len(answer)} chars):")
            print(f"   {answer[:300]}...")
            
            if 'sources' in result:
                print(f"\n📚 Sources: {result['sources']}")
        else:
            print(f"✗ No response field in result: {result}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)

