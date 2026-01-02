"""
Check ALL_DOCS content
"""
import sys
sys.path.insert(0, '.')
from new_app import ALL_DOCS

print(f"Total docs: {len(ALL_DOCS)}")
print(f"\nDoc 1 length: {len(ALL_DOCS[0])} chars")
print(f"Doc 1 preview:\n{ALL_DOCS[0][:500]}\n")

print(f"\nDoc 2 length: {len(ALL_DOCS[1])} chars")
print(f"Doc 2 preview:\n{ALL_DOCS[1][:500]}\n")

# Find HOD docs
hod_docs = [d for d in ALL_DOCS if 'HOD' in d and 'Shivnath' in d]
print(f"\nDocs with HOD info: {len(hod_docs)}")
if hod_docs:
    print(f"\nHOD doc preview:\n{hod_docs[0][:800]}")
else:
    print("\n⚠️ NO HOD DOCUMENTS FOUND!")
    
# Check for faculty documents
faculty_docs = [d for d in ALL_DOCS if 'faculty' in d.lower() and len(d) > 1000]
print(f"\nLarge faculty documents: {len(faculty_docs)}")
if faculty_docs:
    print(f"\nFirst faculty doc length: {len(faculty_docs[0])}")
    print(f"Preview:\n{faculty_docs[0][:500]}")
