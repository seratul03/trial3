from app import retrieve_top_k

test_queries = [
    "Who is the HOD of CSE?",
    "Tell me about faculty",
    "What are the subjects in semester 1?",
    "Hostel rules",
    "Library timing",
    "Exam dates",
    "Holiday list"
]

for query in test_queries:
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print('='*80)
    docs = retrieve_top_k(query, k=3)
    for i, d in enumerate(docs, 1):
        print(f"{i}. {d['path']}: {d['score']:.2f}")
