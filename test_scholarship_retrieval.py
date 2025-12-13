"""
Test the scholarship retrieval and context building
"""
import sys
sys.path.insert(0, '.')

from app import retrieve_top_k, build_context_from_docs

def test_scholarship_retrieval():
    """Test that scholarship queries retrieve the correct files"""
    
    print("=" * 80)
    print("SCHOLARSHIP RETRIEVAL TEST")
    print("=" * 80)
    
    test_queries = [
        "What is Kanyashree scholarship?",
        "Tell me about Aikyashree",
        "I am from minority community, which scholarship?",
        "Scholarship for sports students",
        "Nabanna scholarship eligibility",
        "What scholarships are available?",
        "Am I eligible for financial aid if my family income is 2 lakhs?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print(f"{'='*80}")
        
        # Get top documents
        docs = retrieve_top_k(query, k=3)
        
        print(f"\nTop 3 Retrieved Documents:")
        for i, doc in enumerate(docs, 1):
            print(f"\n  {i}. {doc['path']}")
            print(f"     Score: {doc['score']:.2f}")
            print(f"     Snippet: {doc['snippet'][:150]}...")
        
        # Check if detailed scholarship files are prioritized
        detailed_files = [d for d in docs if 'detailed scholarship' in d['path'].lower()]
        if detailed_files:
            print(f"\n  ✅ SUCCESS: {len(detailed_files)} detailed scholarship file(s) in top 3")
        else:
            print(f"\n  ⚠️  WARNING: No detailed scholarship files in top 3")
        
        # Build context
        context = build_context_from_docs(query)
        
        print(f"\n  Context Length: {len(context)} characters")
        
        # Check for personalization instructions
        if "PERSONALIZATION INSTRUCTIONS" in context:
            print(f"  ✅ Personalization instructions included")
        else:
            print(f"  ⚠️  No personalization instructions found")
        
        # Show a preview of the context
        print(f"\n  Context Preview (first 500 chars):")
        print(f"  {'-'*76}")
        print(f"  {context[:500]}...")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    test_scholarship_retrieval()
