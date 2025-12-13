from app import retrieve_top_k

docs = retrieve_top_k('kanyashree scholarship', k=10)
for d in docs:
    print(f"{d['path']}: {d['score']}")
