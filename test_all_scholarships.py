from app.app import retrieve_top_k

test_queries = [
    "kanyashree scholarship",
    "aikyashree",
    "nabanna scholarship",
    "sports scholarship",
    "vivekananda merit",
    "what scholarships are available",
    "minority scholarship",
    "I need financial aid"
]

for query in test_queries:
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print('='*80)
    docs = retrieve_top_k(query, k=3)
    for i, d in enumerate(docs, 1):
        print(f"{i}. {d['path']}: {d['score']:.2f}")
