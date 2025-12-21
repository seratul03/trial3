try:
    from sentence_transformers import SentenceTransformer
    _HAS_ST = True
except Exception:
    SentenceTransformer = None
    _HAS_ST = False

_model = None

def get_model():
    global _model
    if _model is None:
        print("📥 Downloading embedding model (all-MiniLM-L6-v2) for the first time...")
        print("   This may take a few minutes. The model will be cached for future use.")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✓ Model loaded successfully!")
    return _model

def embed(texts):
    """Return embeddings for a list of texts.
    Uses SentenceTransformer when available; otherwise falls back to a simple
    deterministic hashing-based embedding (128 dims) so the server can run
    without heavy ML dependencies.
    """
    if _HAS_ST:
        model = get_model()
        return model.encode(texts, normalize_embeddings=True)

    # Fallback: deterministic hashing-based vector (128 dims)
    import hashlib
    out = []
    for t in texts:
        h = hashlib.md5(t.encode('utf-8')).digest()
        # md5 gives 16 bytes; expand to 128 dims by repeating and scaling
        base = [b / 255.0 for b in h]
        vec = (base * 8)[:128]
        out.append([float(x) for x in vec])
    return out
