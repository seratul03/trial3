# Scholarship/app.py

from flask import Flask, render_template, request, abort
import os
import json

# Try importing the chart generator
try:
    from charts.chart_generator import generate_scholarship_charts
except ImportError:
    generate_scholarship_charts = None

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'detailed scholarship')

from data.scholarships import scholarships

# --- MASTER MAPPING ---
# Every slug now points to a unique, dedicated JSON file.
SLUG_TO_FILE = {
    # West Bengal Schemes
    "post-matric-minority": "post-matric-minority.json",
    "mcm-scholarship": "mcm-scholarship.json",
    "svmcm": "vivekananda.json",
    "svmcm-dpi": "vivekananda.json",
    "nabanna": "nabanna.json",
    "post-matric-sc-st-obc": "oasis.json",
    "kanyashree": "kanyashree.json",
    "aikyashree": "aikyashree.json",
    "oasis": "oasis.json",

    # Central Schemes
    "central-sector": "central_sector.json",
    "ishan-uday": "ishan_uday.json",
    "central-minority": "post-matric-minority.json", # Can share file or create distinct if content differs significantly
    "mcm-professional": "mcm-scholarship.json",
    "disability-scholarship": "disability_scholarship.json", # NEW
    "beedi-cine-workers": "beedi_cine_workers.json",       # NEW

    # Northeast & Other States
    "assam-sc-obc": "assam_sc_obc.json",           # NEW
    "tripura-st": "tripura_st.json",               # NEW
    "tripura-sc-obc": "tripura_sc_obc.json",       # NEW
    "ambedkar-ebc": "ambedkar_ebc.json",           # NEW
    "umbrella-st": "umbrella_st.json",             # NEW
    "arunachal-st": "arunachal_st.json",           # NEW
    "mizoram-st": "mizoram_st.json",               # NEW
    "nagaland-minority": "nagaland_minority.json", # NEW
    "sikkim-merit": "sikkim_merit.json",           # NEW
    
    # Other States
    "bihar-scholarship": "bihar_scholarship.json",     # NEW
    "ekalyan-jharkhand": "ekalyan_jharkhand.json",     # NEW
    "nec-merit": "nec_merit.json",

    # Private & Corporate
    "virtusa": "virtusa.json",
    "tata-engineering": "tata_engineering.json",
    "ongc": "ongc.json",
    "hdfc-parivartan": "hdfc_parivartan.json",
    "arvind": "arvind.json",
    "commonwealth": "commonwealth.json",
    "jk-tyre": "jk_tyre.json",
    "reliance": "reliance.json",
    "ffe": "ffe.json",

    # AICTE
    "pragati": "pragati.json",
    "saksham": "saksham.json",
    "swanath": "swanath.json",

    # Legacy / Archive
    "vidyalankar": "vidyalankar.json",
    "medha": "medha_britti.json",
    "creditcard": "credit_card.json",
    "sports": "sports.json"
}

@app.route("/")
def index():
    return render_template("sc_index.html", scholarships=scholarships)

@app.route("/detail")
def detail():
    s_id = request.args.get('id')
    
    # 1. Validate ID
    if not s_id or s_id not in SLUG_TO_FILE:
        return render_template("sc_detail.html", error=f"Scholarship '{s_id}' not found."), 404
    
    filename = SLUG_TO_FILE[s_id]
    file_path = os.path.join(DATA_DIR, filename)

    data = {}
    charts = {}
    
    # 2. Load Data
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 3. Generate Charts (if module exists)
        if generate_scholarship_charts:
            charts = generate_scholarship_charts(data)
        
    except FileNotFoundError:
        return render_template("sc_detail.html", error=f"Data file '{filename}' is missing.")
    except json.JSONDecodeError:
        return render_template("sc_detail.html", error="Error reading scholarship data file.")
    except Exception as e:
        print(f"Error: {e}")
        return render_template("sc_detail.html", error="An unexpected error occurred.")

    return render_template("sc_detail.html", data=data, charts=charts)

if __name__ == "__main__":
    app.run(debug=True)
