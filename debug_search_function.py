"""
Debug the vector search function - see what indices it returns
"""
import sys
sys.path.insert(0, '.')
from new_app import VECTOR_INDEX
from app.vectorstore.embeddings import embed
import numpy as np
import faiss

query = "Who is our HOD?"

print(f"Query: {query}")
print(f"Total texts in index: {len(VECTOR_INDEX.texts)}")
print(f"Has FAISS: {faiss is not None if 'faiss' in dir() else False}")
print(f"Has numpy: {np is not None}")

# Do manual search to see indices
q_vec = embed([query])
print(f"\nQuery vector shape: {q_vec.shape if hasattr(q_vec, 'shape') else len(q_vec)}")

if VECTOR_INDEX.index is not None:
    print("\nUsing FAISS search")
    scores, idxs = VECTOR_INDEX.index.search(q_vec, 5)
    print(f"Scores: {scores}")
    print(f"Indices: {idxs}")
    print(f"Indices[0]: {idxs[0]}")
    
    for i in idxs[0]:
        print(f"\nIndex {i}:")
        print(f"  i < len(texts): {i < len(VECTOR_INDEX.texts)}")
        if i < len(VECTOR_INDEX.texts):
            text = VECTOR_INDEX.texts[i]
            print(f"  Text length: {len(text)}")
            print(f"  Preview: {text[:200]}")
        else:
            print(f"  ⚠️ INDEX OUT OF BOUNDS!")

# Also test the search method directly
print("\n" + "="*80)
print("Testing VECTOR_INDEX.search() method")
print("="*80)
results = VECTOR_INDEX.search(query, k=5)
print(f"Got {len(results)} results")
for i, r in enumerate(results):
    print(f"\nResult {i}: {len(r)} chars")
    print(f"Preview: {r[:200]}")
