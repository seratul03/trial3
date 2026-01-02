import json
from pathlib import Path

# Mapping between scholarship_id and slug
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

def load_scholarship_quick_data():
    """Load scholarship quick answer data"""
    base_dir = Path(__file__).resolve().parent.parent.parent
    scholarship_file = base_dir / 'scholarship_quick_ans.json'
    
    try:
        with open(scholarship_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading scholarship quick data: {e}")
        return []

def match_scholarship(query):
    """
    Match user query with scholarship keywords and return matched scholarship data.
    Returns None if no match found.
    """
    scholarships = load_scholarship_quick_data()
    query_lower = query.lower()
    
    # Try to find a match based on keywords
    for scholarship in scholarships:
        keywords = scholarship.get('keywords', [])
        
        # Check if any keyword is in the query
        for keyword in keywords:
            if keyword.lower() in query_lower:
                return scholarship
    
    return None

def get_scholarship_response(scholarship_data):
    """
    Generate formatted response for scholarship query.
    Returns tuple: (intro_text, scholarship_slug, scholarship_name)
    """
    if not scholarship_data:
        return None
    
    intro = scholarship_data.get('intro', '')
    scholarship_id = scholarship_data.get('scholarship_id', '')
    scholarship_name = scholarship_data.get('scholarship_name', '')
    
    # Convert scholarship_id to slug
    scholarship_slug = SCHOLARSHIP_ID_TO_SLUG.get(scholarship_id, '')
    
    return (intro, scholarship_slug, scholarship_name)
