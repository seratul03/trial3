"""
COMPREHENSIVE TEST - Verify AI reads and uses provided context correctly
This test proves the context is being sent and the AI can use it
"""
import sys
sys.path.insert(0, '.')

from app.core.intent import detect_intent
from app.core.retriever import retrieve
from app.core.prompt_builder import build_prompt
from app.vectorstore.index import VectorIndex
from app.llm.gemini_client import ask_gemini
from new_app import ALL_DOCS, VECTOR_INDEX
import json

print("="*80)
print("COMPREHENSIVE CONTEXT VERIFICATION TEST")
print("="*80)

# Test Query
test_query = "Who is our HOD?"

print(f"\n[STEP 1] Query: {test_query}")
print("-"*80)

# Detect Intent
intent = detect_intent(test_query)
print(f"✓ Intent detected: {intent}")

# Retrieve Documents
print("\n[STEP 2] Retrieving relevant documents...")
print("-"*80)
docs = retrieve(
    query=test_query,
    intent=intent,
    vector_index=VECTOR_INDEX,
    fallback_docs=ALL_DOCS
)
print(f"✓ Retrieved {len(docs)} documents")
print(f"\nFirst document preview (first 300 chars):")
print(docs[0][:300] if docs else "No docs")

# Extract Relevant Context
print("\n[STEP 3] Extracting relevant context...")
print("-"*80)
context_items = docs if docs is not None else []
print(f"✓ Extracted {len(context_items) if isinstance(context_items, list) else 1} context items")

# Build final context
if isinstance(context_items, list):
    context = "\n\n".join(str(item) for item in context_items[:3])
else:
    context = str(context_items)

print(f"\n[STEP 4] Final context to be sent to AI ({len(context)} characters):")
print("-"*80)
print(context)
print("-"*80)

# Build prompt
print("\n[STEP 5] Building full prompt...")
print("-"*80)
prompt = build_prompt(test_query, context)
print(f"✓ Prompt built ({len(prompt)} characters)")
print(f"\nPrompt includes context: {'YES ✓' if 'Shivnath Ghosh' in prompt else 'NO ✗'}")
print(f"Context section preview:")
print(prompt[prompt.find("CONTEXT:"):prompt.find("CONTEXT:")+500] if "CONTEXT:" in prompt else "Context not found!")

# Ask AI
print("\n[STEP 6] Sending to Gemini AI...")
print("-"*80)
answer = ask_gemini(prompt)
print("AI Response:")
print("="*80)
print(answer)
print("="*80)

# Verification
print("\n[STEP 7] VERIFICATION")
print("="*80)
verification_checks = [
    ("Context contains HOD info", "HOD" in context and "Shivnath Ghosh" in context),
    ("Context is readable (not raw JSON)", not context.strip().startswith('{')),
    ("Context is concise (<1000 chars)", len(context) < 1000),
    ("Prompt contains context", "CONTEXT:" in prompt and len(context) > 0),
    ("AI response is not empty", len(answer.strip()) > 0),
    ("AI mentions Dr. Shivnath Ghosh", "Shivnath Ghosh" in answer or "shivnath ghosh" in answer.lower()),
    ("AI mentions HOD position", "HOD" in answer or "Head of Department" in answer.lower())
]

all_passed = True
for check_name, result in verification_checks:
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"{status}: {check_name}")
    if not result:
        all_passed = False

print("\n" + "="*80)
if all_passed:
    print("🎉 SUCCESS - AI IS READING AND USING CONTEXT CORRECTLY!")
    print("="*80)
    print("\nThe AI:")
    print("  ✓ Receives parsed, human-readable context")
    print("  ✓ Gets only relevant information (not 78KB of JSON)")
    print("  ✓ Successfully extracts and uses the information")
    print("  ✓ Provides accurate, non-hallucinated answers")
else:
    print("⚠️ SOME CHECKS FAILED - Review the results above")
    print("="*80)

print("\n[RECOMMENDATION]")
print("="*80)
print("If all checks passed, your chatbot is working correctly!")
print("Start the server with: python new_app.py")
print("Test with queries like:")
print("  • 'Who is our HOD?'")
print("  • 'Tell me about Dr. Shivnath Ghosh'")
print("  • 'What scholarships are available?'")
