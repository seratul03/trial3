"""
Test script for scholarship matching functionality
Run this to verify keyword matching works correctly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.scholarship_matcher import match_scholarship, get_scholarship_response

# Test queries
test_queries = [
    "tell me about post matric scholarship",
    "what is aikyashree?",
    "mcm scholarship details",
    "I want to know about vivekananda scholarship",
    "nabanna scholarship information",
    "kanyashree k2 details",
    "virtusa scholarship",
    "reliance foundation scholarship",
    "merit cum means",
    "wb post matric",
    "central sector scholarship",
    "ishan uday",
    "random query that should not match"
]

print("=" * 70)
print("SCHOLARSHIP MATCHER TEST")
print("=" * 70)

for query in test_queries:
    print(f"\n📝 Query: {query}")
    matched = match_scholarship(query)
    
    if matched:
        response = get_scholarship_response(matched)
        if response:
            intro, slug, name = response
            print(f"✅ MATCHED!")
            print(f"   Scholarship: {name}")
            print(f"   Slug: {slug}")
            print(f"   Intro: {intro[:80]}...")
            print(f"   URL: /scholarship?highlight={slug}")
    else:
        print(f"❌ NO MATCH - Will use default AI response")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
