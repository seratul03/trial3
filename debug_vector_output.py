"""
Debug: Check what the vector index actually returns
"""
import sys
sys.path.insert(0, '.')

from new_app import ALL_DOCS, VECTOR_INDEX
import json

print("="*80)
print("DEBUGGING VECTOR INDEX OUTPUT")
print("="*80)

# Test query
query = "Who is our HOD?"

print(f"\nQuery: {query}")
print("-"*80)

# Search vector index
results = VECTOR_INDEX.search(query, k=3)

print(f"\nVector search returned {len(results)} results\n")

for i, doc in enumerate(results, 1):
    print(f"\n[Document {i}]")
    print("="*80)
    print(f"Type: {type(doc)}")
    print(f"Length: {len(doc)} characters")
    print(f"\nFirst 500 characters:")
    print("-"*80)
    print(doc[:500])
    print("-"*80)
    
    # Try to parse as JSON
    try:
        parsed = json.loads(doc)
        print(f"\n✓ Valid JSON")
        print(f"Keys: {list(parsed.keys())[:10]}")
        
        # Check if it's faculty data
        if "faculty" in parsed:
            print(f"✓ Faculty data found!")
            print(f"Number of faculty: {len(parsed['faculty'])}")
            print(f"Department: {parsed.get('department', 'N/A')}")
            
            # Check for HOD
            for fac_id, fac_info in parsed['faculty'].items():
                if 'HOD' in fac_info.get('position', ''):
                    print(f"\n✓✓✓ HOD FOUND: {fac_info.get('name')}")
                    print(f"Position: {fac_info.get('position')}")
                    break
    except json.JSONDecodeError:
        print("\n✗ Not valid JSON")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("The vector search is returning documents.")
print("Now checking if parse_documents works correctly...")

from app.core.document_parser import parse_documents

parsed_results = parse_documents(results)
print(f"\nAfter parsing: {len(parsed_results)} documents")

for i, doc in enumerate(parsed_results, 1):
    print(f"\n[Parsed Document {i}]")
    print("="*80)
    print(f"Type: {type(doc)}")
    print(f"Length: {len(doc)} characters")
    print(f"\nContent preview (first 500 chars):")
    print("-"*80)
    print(doc[:500])
    print("-"*80)
