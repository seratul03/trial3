"""
Retriever – Deterministic, authority-safe document retrieval for
Brainware University Campus Assistant.

RULES ENFORCED:
- Authoritative queries NEVER use vector search
- Files are selected BEFORE retrieval
- Vector search is allowed ONLY for general / vague queries
"""

import re
from pathlib import Path
from typing import List

from app.core.document_parser import parse_documents
from app.core.context_extractor import extract_relevant_context
from app.core.resource_map import RESOURCE_MAP, JSON_PATH


# --------------------------------------------------
# LOW-LEVEL FILE LOADER
# --------------------------------------------------

def _load_files(file_paths: List[Path]) -> List[str]:
    """Load raw text from a list of file paths."""
    docs = []

    for path in file_paths:
        if not path.exists():
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                docs.append(f.read())
        except Exception:
            continue

    return docs


# --------------------------------------------------
# SUBJECT CODE RESOLUTION (BSCM / ESCM / PCC / PEC)
# --------------------------------------------------

def _resolve_subject_file(query: str) -> List[str]:
    """
    Resolve subject JSON dynamically from subject code.
    Example: BSCM301 → BSCM301.json
    """
    match = re.search(r"\b(bscm|escm|pcc|pec)[-\s]?\d+\b", query.lower())
    if not match:
        return []

    code = match.group(0).upper().replace(" ", "")
    file_path = JSON_PATH / f"{code}.json"

    if file_path.exists():
        return _load_files([file_path])

    return []


# --------------------------------------------------
# MAIN RETRIEVER (AUTHORITATIVE)
# --------------------------------------------------

def retrieve(query: str, intent: str, vector_index=None, fallback_docs=None):
    """
    Retrieve context for a query based on strict authority rules.

    NOTE:
    - fallback_docs is intentionally accepted for backward compatibility
    - fallback_docs is NOT used for authoritative queries
    """

    raw_docs = []

    # --------------------------------------------------
    # 1. AUTHORITATIVE INTENT → FIXED FILES
    # --------------------------------------------------
    if intent in RESOURCE_MAP and RESOURCE_MAP[intent]:
        raw_docs = _load_files(RESOURCE_MAP[intent])

    # --------------------------------------------------
    # 2. SUBJECT CODE → DYNAMIC FILE
    # --------------------------------------------------
    elif intent == "subject":
        raw_docs = _resolve_subject_file(query)

    # --------------------------------------------------
    # 3. GENERAL / NON-AUTHORITATIVE → VECTOR SEARCH
    # --------------------------------------------------
    elif intent == "general" and vector_index is not None:
        semantic_results = vector_index.search(query, k=5)
        if semantic_results:
            raw_docs = semantic_results

        # optional fallback (only for general intent)
        elif fallback_docs:
            raw_docs = fallback_docs

    # --------------------------------------------------
    # 4. NO DATA FOUND
    # --------------------------------------------------
    if not raw_docs:
        return []

    # --------------------------------------------------
    # 5. CONTEXT EXTRACTION FIRST (needs raw JSON for faculty/HOD)
    # --------------------------------------------------
    extracted_docs = extract_relevant_context(query, raw_docs)

    if not extracted_docs:
        return []

    # --------------------------------------------------
    # 6. PARSE TO HUMAN-READABLE TEXT FOR THE LLM
    # --------------------------------------------------
    return parse_documents(extracted_docs)
