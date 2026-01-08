import json
import re
from pathlib import Path
from typing import Optional, Dict

# -------------------------
# LOAD SCHOLARSHIP DATA
# -------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
with open(BASE_DIR / "scholarship_quick_ans.json", "r", encoding="utf-8") as f:
    SCHOLARSHIPS = json.load(f)


# -------------------------
# NORMALIZE QUERY
# -------------------------
def normalize(text: str) -> str:
    """Normalize text but keep spaces for better matching"""
    return text.lower().strip()


# -------------------------
# DETECT INTENT
# -------------------------
# def detect_intent(query: str) -> str:
#     q = query.lower()

#     if re.search(r"\b(scholarship|stipend|grant|svmcm|mcm|nabanna|aikyashree|kanyashree)\b", q):
#         return "scholarship"

#     if re.search(r"\b(canteen|mess|food|cafeteria)\b", q):
#         return "canteen"

#     if re.search(r"\b(rule|policy|fine|banned|allowed)\b", q):
#         return "rules"

#     if re.search(r"\b(holiday|vacation|leave|break)\b", q):
#         return "holiday"

#     return "general"
def detect_intent(query: str) -> str:
    q = query.lower()

    if re.search(r"\b(hod|faculty|professor|teacher|dr\.)\b", q):
        return "faculty"

    if re.search(r"\b(bscm|escm|pcc|pec)[-\s]?\d+\b", q):
        return "subject"

    # Expand scholarship trigger words so named schemes (e.g., kanyashree, svmcm) hit the scholarship intent
    if re.search(r"\b(scholarship|stipend|grant|svmcm|kanyashree|nabanna|aikyashree|mcm)\b", q):
        return "scholarship"

    if re.search(r"\b(holiday|vacation|leave)\b", q):
        return "holiday"

    if re.search(r"\b(exam|attendance)\b", q):
        return "exam"

    if re.search(r"\b(library|reading room)\b", q):
        return "library"

    if re.search(r"\b(rule|policy|fine|allowed|banned)\b", q):
        return "rules"

    if re.search(r"\b(brainware university|chancellor|vice chancellor|vc|founder|campus|address|location|established)\b", q):
        return "about"

    return "general"



# -------------------------
# FIND SCHOLARSHIP (CORE FIX)
# -------------------------
# Mapping scholarship_id to slug
SCHOLARSHIP_ID_TO_SLUG = {
    "1-POST_MATRIC_SCHOLARS": "post-matric-minority",
    "2-MERIT_CUM_MEANS_SCHO": "mcm-scholarship",
    "3-SWAMI_VIVEKANANADA_M": "svmcm",
    "4-SWAMI_VIVEKANANADA_M": "svmcm-dpi",
    "5-WEST_BENGAL_CHIEF_MI": "nabanna",
    "6-POST_MATRIC_SC_ST_OBC": "post-matric-sc-st-obc",
    "7-POST_MATRIC_MINORITY_CS": "central-minority",
    "8-MERIT_CUM_MEANS_CS": "mcm-professional",
    "9-POST_MATRIC_DISABILITY": "disability-scholarship",
    "10-BEEDI_CINE_WORKERS": "beedi-cine-workers",
    "11-CENTRAL_SECTOR": "central-sector",
    "22-ISHAN_UDAY": "ishan-uday",
    "24-KANNYASHREE_K2": "kanyashree",
    "VIRTUSA_ENGINEERING": "virtusa",
    "RELIANCE_FOUNDATION": "reliance"
}

def find_all_scholarships(query: str) -> list:
    """Find ALL scholarships matching the query"""
    q_norm = normalize(query)
    matches = []
    seen_ids = set()

    # PRIORITY: longer keywords first
    sorted_scholarships = sorted(
        SCHOLARSHIPS,
        key=lambda s: max(len(k) for k in s["keywords"]),
        reverse=True
    )

    for scholarship in sorted_scholarships:
        scholarship_id = scholarship["scholarship_id"]
        
        # Skip if already added
        if scholarship_id in seen_ids:
            continue
            
        for kw in scholarship["keywords"]:
            if normalize(kw) in q_norm or q_norm in normalize(kw):
                scholarship_slug = SCHOLARSHIP_ID_TO_SLUG.get(scholarship_id, "")
                
                matches.append({
                    **scholarship,
                    "slug": scholarship_slug
                })
                seen_ids.add(scholarship_id)
                break  # Found a match for this scholarship, move to next
    
    return matches

def find_scholarship(query: str) -> Optional[Dict]:
    """Find single scholarship (backward compatibility)"""
    matches = find_all_scholarships(query)
    return matches[0] if matches else None


# -------------------------
# MAIN HANDLER
# -------------------------
def handle_query(query: str) -> Dict:
    intent = detect_intent(query)

    if intent != "scholarship":
        return {
            "intent": intent,
            "response": "This query is not related to scholarships."
        }

    scholarship = find_scholarship(query)

    if scholarship:
        scholarship_id = scholarship["scholarship_id"]
        scholarship_slug = SCHOLARSHIP_ID_TO_SLUG.get(scholarship_id, "")
        
        return {
            "intent": "scholarship",
            "matched": True,
            "scholarship": scholarship["scholarship_name"],
            "intro": scholarship["intro"],
            "slug": scholarship_slug,
            "url": f"/scholarship?highlight={scholarship_slug}"
        }

    return {
        "intent": "scholarship",
        "matched": False,
        "response": "I couldn't find an exact scholarship match. Please visit the scholarship portal."
    }
