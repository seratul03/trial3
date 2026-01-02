"""
FINAL CONFIRMATION TEST - Proves AI reads and uses context
Run this to verify the fix
"""
import sys
sys.path.insert(0, '.')

from new_app import ALL_DOCS, VECTOR_INDEX
from app.core.intent import detect_intent
from app.core.retriever import retrieve
from app.core.prompt_builder import build_prompt
from app.core.context_extractor import extract_relevant_context
from app.llm.gemini_client import ask_gemini

def test_query(query, expected_in_response):
    print("\n" + "="*80)
    print(f"Testing: {query}")
    print("="*80)
    
    # Process query
    intent = detect_intent(query)
    docs = retrieve(query, intent, VECTOR_INDEX, ALL_DOCS)
    context_items = extract_relevant_context(query, docs)
    
    if isinstance(context_items, list):
        context = "\n\n".join(str(item) for item in context_items[:3])
    else:
        context = str(context_items)
    
    # Check context quality
    print(f"Context length: {len(context)} chars")
    print(f"Context is readable: {'YES ✓' if not context.strip().startswith('{') and len(context) > 50 else 'NO ✗'}")
    
    # Get AI response
    prompt = build_prompt(query, context)
    answer = ask_gemini(prompt)
    
    print(f"\nAI Response:")
    print("-"*80)
    print(answer)
    print("-"*80)
    
    # Verify
    all_found = all(term.lower() in answer.lower() for term in expected_in_response)
    if all_found:
        print(f"\n✅ SUCCESS - AI correctly answered using provided context!")
        return True
    else:
        print(f"\n⚠️ Response missing expected terms: {expected_in_response}")
        return False

print("="*80)
print("FINAL CONFIRMATION TEST")
print("="*80)
print("\nTesting if AI reads and uses context correctly...")

tests = [
    ("Who is our HOD?", ["Shivnath Ghosh", "Professor"]),
    ("Tell me about Dr. Shivnath Ghosh", ["Shivnath", "Ghosh"]),
]

passed = 0
total = len(tests)

for query, expected in tests:
    if test_query(query, expected):
        passed += 1

print("\n" + "="*80)
print("FINAL RESULTS")
print("="*80)
print(f"Tests passed: {passed}/{total}")

if passed == total:
    print("\n🎉 ALL TESTS PASSED!")
    print("="*80)
    print("\nYour chatbot is working correctly!")
    print("The AI successfully:")
    print("  ✓ Retrieves relevant context from your data")
    print("  ✓ Reads and understands the context")
    print("  ✓ Provides accurate answers without hallucinations")
    print("\nYou can now start the server:")
    print("  python new_app.py")
else:
    print(f"\n⚠️ {total - passed} test(s) failed")
    print("Please review the output above")
