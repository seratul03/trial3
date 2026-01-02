"""
Debug script to test what context is being retrieved for a query
"""
import json
from pathlib import Path
from app.core.intent import detect_intent
from app.core.retriever import retrieve
from app.core.prompt_builder import build_prompt
from app.vectorstore.index import VectorIndex

BASE_DIR = Path(__file__).resolve().parent

# Load all JSON documents
def load_docs():
    docs = []
    for p in BASE_DIR.rglob("*.json"):
        if '.venv' in str(p) or 'node_modules' in str(p):
            continue
        try:
            with open(p, "r", encoding="utf-8") as f:
                content = json.dumps(json.load(f))
                docs.append(content)
                print(f"✓ Loaded: {p.name}")
        except Exception as e:
            print(f"✗ Failed: {p.name} - {e}")
    return docs

print("=" * 80)
print("LOADING ALL JSON DOCUMENTS")
print("=" * 80)
ALL_DOCS = load_docs()
print(f"\n✓ Total documents loaded: {len(ALL_DOCS)}")

print("\n" + "=" * 80)
print("BUILDING VECTOR INDEX")
print("=" * 80)
VECTOR_INDEX = VectorIndex()
VECTOR_INDEX.build(ALL_DOCS)
print("✓ Vector index built successfully")

# Test queries
test_queries = [
    "Who is our HOD?",
    "Who is Dr. Shivnath Ghosh?",
    "Tell me about scholarships",
    "What are the holidays?"
]

for query in test_queries:
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)
    
    # Detect intent
    intent = detect_intent(query)
    print(f"Intent: {intent}")
    
    # Retrieve context
    docs = retrieve(
        query=query,
        intent=intent,
        vector_index=VECTOR_INDEX,
        fallback_docs=ALL_DOCS
    )
    
    print(f"\nRetrieved {len(docs)} documents")
    
    # Show first retrieved document
    if docs:
        context = "\n\n".join(docs[:3])
        print(f"\nContext length: {len(context)} characters")
        print("\nFirst 500 characters of context:")
        print("-" * 80)
        print(context[:500])
        print("-" * 80)
        
        # Build full prompt
        prompt = build_prompt(query, context)
        print(f"\nFull prompt length: {len(prompt)} characters")
        print("\nPrompt preview (first 800 chars):")
        print("-" * 80)
        print(prompt[:800])
        print("-" * 80)
    else:
        print("\n⚠️ NO CONTEXT RETRIEVED!")

print("\n" + "=" * 80)
print("DEBUG COMPLETE")
print("=" * 80)
