try:
    import numpy as np
    _HAS_NUMPY = True
except Exception:
    np = None
    _HAS_NUMPY = False

try:
    import faiss
    _HAS_FAISS = True
except Exception:
    faiss = None
    _HAS_FAISS = False

from .embeddings import embed


class VectorIndex:
    def __init__(self):
        self.texts = []
        self.index = None
        self.vectors = None

    def build(self, texts):
        self.texts = texts
        vectors = embed(texts)
        # vectors expected as numpy array
        if _HAS_FAISS:
            dim = vectors.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            self.index.add(vectors)
        else:
            # fallback: store vectors and do numpy or pure-Python dot-product search
            if _HAS_NUMPY:
                self.vectors = np.array(vectors, dtype=np.float32)
            else:
                # keep as list of lists
                self.vectors = [list(map(float, v)) for v in vectors]

    def search(self, query, k=5):
        q_vec = embed([query])
        results = []
        if _HAS_FAISS and self.index is not None:
            scores, idxs = self.index.search(q_vec, k)
            for i in idxs[0]:
                if i < len(self.texts):
                    results.append(self.texts[i])
            return results
        else:
            if self.vectors is None:
                return []
            # numpy-based similarity
            if _HAS_NUMPY:
                q = np.array(q_vec[0], dtype=np.float32)
                sims = np.dot(self.vectors, q)
                idxs = np.argsort(-sims)[:k]
                for i in idxs:
                    if int(i) < len(self.texts):
                        results.append(self.texts[int(i)])
                return results
            # pure-Python similarity (safe fallback)
            q = [float(x) for x in q_vec[0]]
            sims = []
            for v in self.vectors:
                # dot product
                s = 0.0
                for a, b in zip(v, q):
                    s += a * b
                sims.append(s)
            # get top-k indices
            idxs = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:k]
            for i in idxs:
                if i < len(self.texts):
                    results.append(self.texts[i])
            return results
