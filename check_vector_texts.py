"""
Check if VECTOR_INDEX.texts contains correct data
"""
import sys
sys.path.insert(0, '.')
from new_app import VECTOR_INDEX

print(f"Total texts in vector index: {len(VECTOR_INDEX.texts)}")

print("\n[Checking first 10 texts]")
for i in range(min(10, len(VECTOR_INDEX.texts))):
    text = VECTOR_INDEX.texts[i]
    print(f"\nText {i}: {len(text)} chars")
    print(f"Preview: {text[:200]}")

# Find HOD text
print("\n[Searching for HOD in vector index]")
hod_texts = [(i, t) for i, t in enumerate(VECTOR_INDEX.texts) if 'HOD' in t and 'Shivnath' in t]
print(f"Found {len(hod_texts)} texts with HOD info")

if hod_texts:
    idx, text = hod_texts[0]
    print(f"\nHOD text index: {idx}")
    print(f"Length: {len(text)} chars")
    print(f"Preview:\n{text[:800]}")
else:
    print("\n⚠️ NO HOD INFO IN VECTOR INDEX!")
    print("This means the vector index is not storing complete documents")
