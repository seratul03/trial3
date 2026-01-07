"""
Context Extraction – Faculty-safe, deterministic extraction
"""

import json
import re


# --------------------------------------------------
# NAME NORMALIZATION
# --------------------------------------------------

def normalize_name(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\b(dr|sir|prof|professor|mr|ms|mrs)\.?\b", "", text)
    return re.sub(r"\s+", " ", text).strip()


# --------------------------------------------------
# FACULTY EXTRACTION (SINGLE RESPONSIBILITY)
# --------------------------------------------------

def extract_faculty_info(query, docs):
    """
    Rules:
    1. Name-based match ALWAYS has priority
    2. HOD match ONLY if explicitly asked
    3. Return type is ALWAYS dict
    """

    query_norm = normalize_name(query)
    want_hod = any(t in query.lower() for t in ["hod", "head of department", "head of dept"])

    for doc_text in docs:
        if not isinstance(doc_text, str):
            continue

        if not doc_text.strip().startswith("{"):
            continue

        try:
            data = json.loads(doc_text)
        except Exception:
            continue

        if "faculty" not in data:
            continue

        department = data.get("department", "Unknown Department")

        # -------------------------------
        # 1️⃣ NAME MATCH (HIGHEST PRIORITY)
        # -------------------------------
        for info in data["faculty"].values():
            faculty_name = info.get("name", "")
            if normalize_name(faculty_name) and normalize_name(faculty_name) in query_norm:
                return {
                    "matched": True,
                    "data": [format_faculty_member(info, department)]
                }

        # -------------------------------
        # 2️⃣ HOD MATCH (ONLY IF ASKED)
        # -------------------------------
        if want_hod:
            for info in data["faculty"].values():
                position = info.get("position", "").lower()
                if "hod" in position or "head" in position:
                    return {
                        "matched": True,
                        "data": [format_faculty_member(info, department)]
                    }

    # -------------------------------
    # ❌ NOTHING FOUND
    # -------------------------------
    return {
        "matched": False,
        "data": []
    }


# --------------------------------------------------
# FORMATTER
# --------------------------------------------------

def format_faculty_member(info, department):
    parts = [
        "=" * 60,
        f"Faculty Member: {info.get('name', 'Unknown')}",
        "=" * 60,
        f"Department: {department}",
        f"Position: {info.get('position', 'Not specified')}",
        f"Qualification: {info.get('qualification', 'Not specified')}",
    ]

    if "research_area" in info:
        ra = info["research_area"]
        if isinstance(ra, list):
            parts.append(f"Research Areas: {', '.join(ra)}")
        else:
            parts.append(f"Research Areas: {ra}")

    if "email" in info:
        parts.append(f"Email: {info['email']}")

    if "phone" in info:
        parts.append(f"Phone: {info['phone']}")

    return "\n".join(parts)


# --------------------------------------------------
# MAIN CONTEXT ENTRY
# --------------------------------------------------

def extract_relevant_context(query, docs):
    query_lower = query.lower()

    if any(t in query_lower for t in ["hod", "faculty", "professor", "teacher", "dr."]):
        result = extract_faculty_info(query, docs)
        return result["data"] if result["matched"] else []

    return docs
