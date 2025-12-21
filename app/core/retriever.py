import json
import re


def keyword_retrieve(query, docs, k=5, intent="general"):
    """Tokenized keyword fallback retrieval with intent-based prioritization.

    Instead of requiring the whole query string to appear as a substring,
    split the query into word tokens and score documents by how many
    tokens they contain. This helps with questions like "Who is our HOD?"
    where punctuation and stopwords previously prevented matches.
    
    Intent-based prioritization boosts documents that match the query intent.
    """
    q = query.lower()
    tokens = [t for t in re.findall(r"\w+", q) if len(t) > 1]
    if not tokens:
        return []

    # Intent-specific boost keywords
    intent_keywords = {
        "holiday": ["holiday", "vacation", "leave", "closed", "break", "_metadata"],
        "scholarship": ["scholarship", "stipend", "grant", "financial"],
        "canteen": ["canteen", "food", "mess", "cafeteria"],
        "rules": ["rule", "policy", "allowed", "banned", "penalty"]
    }

    scored = []
    for text in docs:
        lt = text.lower()
        score = 0
        
        # Base score from query tokens
        for tok in tokens:
            score += lt.count(tok)
        
        # Intent boost: if document contains intent-specific keywords, multiply score
        if intent in intent_keywords:
            has_intent_keyword = any(kw in lt for kw in intent_keywords[intent])
            if has_intent_keyword:
                score *= 10  # Significant boost for intent match
        
        if score > 0:
            scored.append((score, text))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:k]]

def retrieve(query, intent, vector_index, fallback_docs):
    # semantic search first
    semantic = vector_index.search(query, k=5)
    if semantic:
        return semantic

    # fallback keyword search with intent prioritization
    return keyword_retrieve(query, fallback_docs, k=5, intent=intent)
