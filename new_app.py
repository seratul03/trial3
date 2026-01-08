from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for
from flask_cors import CORS
# Import Jinja2 loaders to handle multiple template folders without conflicts
from jinja2 import ChoiceLoader, FileSystemLoader, PrefixLoader
import json
import os
from pathlib import Path
from datetime import datetime
import requests

# Import core chatbot modules
from app.core.intent import (
    detect_intent,
    find_scholarship,
    find_all_scholarships,
    SCHOLARSHIPS,
    SCHOLARSHIP_ID_TO_SLUG,
)
from app.core.retriever import retrieve
from app.core.prompt_builder import build_prompt
from app.vectorstore.index import VectorIndex
from app.llm.gemini_client import ask_gemini

# Import blueprints
from login.app import login_bp

app = Flask(__name__)
CORS(app)

# Set secret key for sessions
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key_change_this_in_production')

BASE_DIR = Path(__file__).resolve().parent

# ============================================================================
# TEMPLATE CONFIGURATION (Fix for Folder Structure)
# ============================================================================
# This configuration allows us to keep your files in "Scholarship/templates"
# without moving them or renaming them. We mount that folder with the prefix "sc/".
app.jinja_loader = ChoiceLoader([
    # 1. Standard templates folder (for home, notice, etc.)
    FileSystemLoader(str(BASE_DIR / 'templates')),
    # 2. Scholarship templates folder (accessed via "sc/filename.html")
    PrefixLoader({
        'sc': FileSystemLoader(str(BASE_DIR / 'Scholarship' / 'templates'))
    })
])

# ============================================================================
# CHATBOT BACKEND - Vector Index & Document Loading
# ============================================================================

def load_docs():
    """Load all JSON documents for the chatbot"""
    docs = []
    seen = set()

    # Prefer structured Resources folder
    resources = BASE_DIR / 'Resources'
    if resources.exists():
        # load .json files
        for p in resources.rglob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    obj = json.load(f)
                    s = json.dumps(obj, ensure_ascii=False)
                    if s not in seen:
                        docs.append(s)
                        seen.add(s)
            except Exception:
                continue

        # load .jsonl files - treat as regular JSON
        # (Previous implementation treated each line separately, causing fragments)
        for p in resources.rglob("*.jsonl"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    obj = json.load(f)
                    s = json.dumps(obj, ensure_ascii=False)
                    if s not in seen:
                        docs.append(s)
                        seen.add(s)
            except Exception:
                continue

        # extract text from PDFs (if PyPDF2 is installed)
        for p in resources.rglob("*.pdf"):
            try:
                try:
                    import PyPDF2
                    reader = PyPDF2.PdfReader(str(p))
                    pages = []
                    for page in reader.pages:
                        try:
                            t = page.extract_text() or ""
                        except Exception:
                            t = ""
                        pages.append(t)
                    text = "\n\n".join(pages).strip()
                    if text:
                        payload = json.dumps({"source": str(p.name), "text": text}, ensure_ascii=False)
                        if payload not in seen:
                            docs.append(payload)
                            seen.add(payload)
                except Exception:
                    # if extraction unavailable, store filename as hint
                    hint = json.dumps({"source": str(p.name), "note": "pdf-not-extracted"}, ensure_ascii=False)
                    if hint not in seen:
                        docs.append(hint)
                        seen.add(hint)
            except Exception:
                continue

    # Fallback: include any other JSONs across repo (keeps previous behavior)
    for p in BASE_DIR.rglob("*.json"):
        try:
            with open(p, "r", encoding="utf-8") as f:
                s = json.dumps(json.load(f), ensure_ascii=False)
                if s not in seen:
                    docs.append(s)
                    seen.add(s)
        except Exception:
            continue

    return docs

print("[INFO] Loading chatbot knowledge base...")
ALL_DOCS = load_docs()
print(f"[INFO] Loaded {len(ALL_DOCS)} documents")

# Build vector index ONCE
print("[INFO] Building vector search index (this may take a minute on first run)...")
VECTOR_INDEX = VectorIndex()
VECTOR_INDEX.build(ALL_DOCS)
print("[INFO] Vector index ready!")


# ============================================================================
# CHATBOT API ENDPOINT
# ============================================================================

@app.route("/chat", methods=["POST"])
def chat():
    """Main chatbot endpoint for AI queries"""
    # check admin backend to see if chatbot is enabled
    try:
        r = requests.get("http://localhost:8000/api/chatbot/settings", timeout=2)
        if r.status_code == 200:
            js = r.json()
            if js.get('success') and js.get('data'):
                settings = js['data']
                # Check if maintenance mode is enabled
                if settings.get('maintenance_mode', False):
                    return jsonify({
                        "intent": "maintenance",
                        "response": settings.get('maintenance_message', 
                                                "The chatbot is currently under maintenance. Please check back later.")
                    }), 200
                # Check if chatbot is disabled
                if not settings.get('enabled', True):
                    return jsonify({
                        "intent": "disabled",
                        "response": "Chatbot has been disabled by the admin."
                    }), 200
    except Exception as e:
        # if admin backend unreachable, assume enabled (fail-open)
        print(f"[WARNING] Could not connect to admin panel: {e}")
        pass

    data = request.get_json(force=True)
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Empty query"}), 400

    intent = detect_intent(query)

    # If user mentions a known scholarship keyword (e.g., kanyashree, svmcm, nabanna)
    # but intent classifier missed it, force scholarship flow so UI gets link payload.
    prelim_matches = find_all_scholarships(query)
    if prelim_matches and intent != "scholarship":
        intent = "scholarship"

    # Check if this is a scholarship query
    if intent == "scholarship":
        print(f"[DEBUG] Scholarship intent detected for query: {query}")
        
        # Find all matching scholarships
        matched_scholarships = find_all_scholarships(query)
        print(f"[DEBUG] Found {len(matched_scholarships)} matching scholarships")
        
        if len(matched_scholarships) > 1:
            # Multiple matches - need disambiguation
            print(f"[DEBUG] Multiple matches found, sending disambiguation")
            
            options = []
            for idx, sch in enumerate(matched_scholarships, 1):
                options.append({
                    "number": idx,
                    "name": sch.get("scholarship_name", ""),
                    "slug": sch.get("slug", ""),
                    "id": sch.get("scholarship_id", "")
                })
            
            return jsonify({
                "intent": intent,
                "needs_disambiguation": True,
                "options": options,
                "response": "I found multiple scholarships matching your query. Please choose the one you want to know about:"
            })
        
        elif len(matched_scholarships) == 1:
            # Single match - return directly
            matched_scholarship = matched_scholarships[0]
            intro = matched_scholarship.get("intro", "")
            scholarship_slug = matched_scholarship.get("slug", "")
            scholarship_name = matched_scholarship.get("scholarship_name", "")
            scholarship_url = f"/scholarship?highlight={scholarship_slug}" if scholarship_slug else ""
            
            print(f"[DEBUG] Single match - slug: {scholarship_slug}, name: {scholarship_name}")
            
            # Format response with intro and link
            response_text = (
                f"{intro}\n\n"
                "Please go through our scholarship portal for more details.\n"
                f"🔗 View {scholarship_name} Details: {scholarship_url}"
            )
            
            response_data = {
                "intent": intent,
                "response": response_text,
                "scholarship_slug": scholarship_slug,
                "scholarship_name": scholarship_name,
                "scholarship_url": scholarship_url,
                "has_scholarship_link": True
            }
            print(f"[DEBUG] Returning response with slug: {scholarship_slug}")
            return jsonify(response_data)

    # Default AI response flow
    docs = retrieve(
        query=query,
        intent=intent,
        vector_index=VECTOR_INDEX,
        fallback_docs=ALL_DOCS
    )

    # Retriever already filters and parses context; just join for the prompt
    context_items = docs if docs is not None else []

    if isinstance(context_items, list):
        context = "\n\n".join(str(item) for item in context_items[:3])
    else:
        context = str(context_items)
    
    prompt = build_prompt(query, context)
    answer = ask_gemini(prompt)

    return jsonify({
        "intent": intent,
        "response": answer
    })


@app.route("/scholarship-by-slug", methods=["POST"])
def get_scholarship_by_slug():
    """Get specific scholarship details by slug"""
    data = request.get_json(force=True)
    slug = data.get("slug", "").strip()
    
    if not slug:
        return jsonify({"error": "Slug required"}), 400
    
    # Find scholarship by slug using authoritative mapping
    for sch in SCHOLARSHIPS:
        sid = sch.get("scholarship_id", "")
        mapped_slug = SCHOLARSHIP_ID_TO_SLUG.get(sid, "")
        if mapped_slug == slug:
            intro = sch.get("intro", "")
            scholarship_name = sch.get("scholarship_name", "")
            scholarship_url = f"/scholarship?highlight={slug}" if slug else ""

            response_text = (
                f"{intro}\n\n"
                "Please go through our scholarship portal for more details.\n"
                f"🔗 View {scholarship_name} Details: {scholarship_url}"
            )

            return jsonify({
                "intent": "scholarship",
                "response": response_text,
                "scholarship_slug": slug,
                "scholarship_name": scholarship_name,
                "scholarship_url": scholarship_url,
                "has_scholarship_link": True,
            })

    return jsonify({"error": "Scholarship not found"}), 404


# ============================================================================
# MAIN FRONTEND - Homepage & Faculty
# ============================================================================

@app.route("/")
def home():
    """Main homepage with chatbot interface"""
    # Uses templates/index.html
    return render_template("index.html")

@app.route("/faculty")
def faculty():
    """Faculty page"""
    return render_template("faculty.html")

@app.route("/faculty-data")
def faculty_data():
    """API endpoint to get faculty data"""
    try:
        faculty_file = BASE_DIR / 'Faculty' / 'brainware_cse_ai_faculty.json'
        with open(faculty_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Convert faculty dict to list for easier frontend consumption
            faculty_list = []
            for key, value in data.get('faculty', {}).items():
                # include stable key/id so frontends can reference specific faculty
                obj = dict(value)
                obj['key'] = key
                faculty_list.append(obj)
            return jsonify(faculty_list)
    except Exception as e:
        return jsonify([]), 500

@app.route("/holiday-data")
def holiday_data():
    """API endpoint to get holiday data"""
    try:
        holiday_file = BASE_DIR / 'Resources' / 'json' / 'holiday.json'
        with open(holiday_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Return just the holidays array if data has that structure
            if isinstance(data, dict) and 'holidays' in data:
                return jsonify(data['holidays'])
            # Otherwise return as-is (backward compatible)
            return jsonify(data)
    except Exception as e:
        print(f"Error loading holiday data: {e}")
        return jsonify([]), 500

@app.route("/holiday/<path:filename>")
def serve_holiday_files(filename):
    """Serve files from the Holiday directory"""
    # Map 'holiday.pdf' to 'Holiday List.pdf'
    if filename.lower() == 'holiday.pdf':
        filename = 'Holiday List.pdf'
    return send_from_directory(BASE_DIR / 'Holiday', filename)

@app.route("/exam-data")
def exam_data():
    """API endpoint to get exam calendar data"""
    try:
        exam_file = BASE_DIR / 'Resources' / 'json' / 'exam.json'
        with open(exam_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return jsonify(data)
    except Exception as e:
        print(f"Error loading exam data: {e}")
        return jsonify({}), 500


# Serve the standalone faculty cards viewer and its assets
@app.route('/faculty_card/')
def faculty_card_index():
    return send_from_directory(BASE_DIR / 'faculty_card', 'index.html')


@app.route('/faculty_card/<path:filename>')
def faculty_card_static(filename):
    return send_from_directory(BASE_DIR / 'faculty_card', filename)


# ============================================================================
# STATIC FILES - Main static folder
# ============================================================================

@app.route("/static/<path:filename>")
def serve_main_static(filename):
    """Serve files from main static folder"""
    return send_from_directory(BASE_DIR / "static", filename)

@app.route('/Faculty/<path:filename>')
def serve_faculty_files(filename):
    """Serve files from the Faculty directory."""
    return send_from_directory(BASE_DIR / 'Faculty', filename)

@app.route('/intro/<path:filename>')
def serve_intro_files(filename):
    """Serve files from the intro directory."""
    return send_from_directory(BASE_DIR / 'intro', filename)

# ============================================================================
# SEMESTER & SUBJECTS API
# ============================================================================

@app.route("/semesters")
def get_semesters():
    """API endpoint to get all semesters"""
    try:
        sem_json_dir = BASE_DIR / 'sem_json'
        semesters = []
        
        for i in range(1, 6):  # Assuming 5 semesters
            sem_file = sem_json_dir / f'sem_{i}.json'
            if sem_file.exists():
                with open(sem_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    semesters.append({
                        'id': i,
                        'name': data.get('semester', f'Semester {i}'),
                        'subject_count': len(data.get('subjects', []))
                    })
        
        return jsonify(semesters)
    except Exception as e:
        return jsonify([]), 500

@app.route("/semester/<int:sem_id>/subjects")
def get_semester_subjects(sem_id):
    """API endpoint to get subjects for a specific semester"""
    try:
        sem_file = BASE_DIR / 'sem_json' / f'sem_{sem_id}.json'
        if not sem_file.exists():
            return jsonify({"error": "Semester not found"}), 404
        
        with open(sem_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Error loading semester data"}), 500


# ============================================================================
# SYLLABUS MODULE
# ============================================================================

@app.route("/syllabus")
def syllabus():
    """Syllabus page"""
    return send_from_directory(BASE_DIR / "syllabus", "syllabus.html")

@app.route("/syllabus/<path:filename>")
def serve_syllabus_static(filename):
    """Serve syllabus static files"""
    return send_from_directory(BASE_DIR / "syllabus", filename)


# ============================================================================
# NOTICE BOARD MODULE
# ============================================================================

def parse_notice_filename(fn):
    """Parse notice PDF filename to extract metadata"""
    name = os.path.splitext(fn)[0]
    parts = name.split('--')

    obj = {
        'filename': fn,
        'title': name,
        'category': 'General',
        'date': None
    }

    try:
        if len(parts) >= 3:
            obj['category'] = parts[0].strip()
            obj['title'] = parts[1].strip()
            dt = datetime.strptime(parts[2].strip(), "%Y-%m-%d")
            obj['date'] = dt.strftime("%Y-%m-%d")
        elif len(parts) == 2:
            obj['category'] = parts[0].strip()
            obj['title'] = parts[1].strip()
    except:
        pass

    try:
        path = os.path.join(BASE_DIR / 'notice' / 'pdfs', fn)
        mtime = os.path.getmtime(path)
        dt = datetime.fromtimestamp(mtime)
        if obj['date'] is None:
            obj['date'] = dt.strftime("%Y-%m-%d")
    except:
        obj['date'] = "1970-01-01"

    return obj


@app.route("/notice")
def notice():
    """Notice board page"""
    return render_template("notice/index.html")

@app.route("/notice/api/notices")
def get_notices():
    """API endpoint to get all notices"""
    pdf_folder = BASE_DIR / 'notice' / 'pdfs'
    if not pdf_folder.exists():
        return jsonify([])
    
    files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    notices = [parse_notice_filename(f) for f in files]
    notices.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify(notices)

@app.route("/notice/pdfs/<path:filename>")
def serve_notice_pdf(filename):
    """Serve notice PDF files"""
    return send_from_directory(BASE_DIR / 'notice' / 'pdfs', filename)

@app.route("/notice/static/<path:filename>")
def serve_notice_static(filename):
    """Serve notice static files"""
    return send_from_directory(BASE_DIR / 'notice' / 'static', filename)


# ============================================================================
# SCHOLARSHIP MODULE (NO IMAGES / TEXT ONLY)
# ============================================================================

# 1. Import Data
try:
    from Scholarship.data.scholarships import scholarships
except ImportError:
    scholarships = []

# 2. Define Configurations Locally to avoid relative import errors
SCHOLARSHIP_DATA_DIR = BASE_DIR / 'Scholarship' / 'data' / 'detailed scholarship'

# Mapping slugs to actual JSON filenames
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
    "central-minority": "post-matric-minority.json",
    "mcm-professional": "mcm-scholarship.json",
    "disability-scholarship": "disability_scholarship.json",
    "beedi-cine-workers": "beedi_cine_workers.json",
    # Northeast & Other States
    "assam-sc-obc": "assam_sc_obc.json",
    "tripura-st": "tripura_st.json",
    "tripura-sc-obc": "tripura_sc_obc.json",
    "ambedkar-ebc": "ambedkar_ebc.json",
    "umbrella-st": "umbrella_st.json",
    "arunachal-st": "arunachal_st.json",
    "mizoram-st": "mizoram_st.json",
    "nagaland-minority": "nagaland_minority.json",
    "sikkim-merit": "sikkim_merit.json",
    "bihar-scholarship": "bihar_scholarship.json",
    "ekalyan-jharkhand": "ekalyan_jharkhand.json",
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

@app.route("/scholarship")
def scholarship():
    """Scholarship listing page"""
    # Renders Scholarship/templates/sc_index.html via 'sc/' prefix
    return render_template("sc/sc_index.html", scholarships=scholarships)

@app.route("/scholarship/detail")
def scholarship_detail():
    """Scholarship detail page"""
    s_id = request.args.get('id')

    # Validate ID
    if not s_id or s_id not in SLUG_TO_FILE:
        # Renders Scholarship/templates/sc_detail.html
        return render_template("sc/sc_detail.html", error="Scholarship not found")

    filename = SLUG_TO_FILE[s_id]
    # Ensure SCHOLARSHIP_DATA_DIR is a Path object for '/' operator
    file_path = Path(SCHOLARSHIP_DATA_DIR) / filename

    data = {}
    
    # CHARTS DISABLED: We are not generating images anymore.
    # The template will simply render text data instead.
    charts = {} 

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
    except FileNotFoundError:
        return render_template("sc/sc_detail.html", error="Data file missing")
    except Exception as e:
        print(f"Error loading scholarship: {e}")
        return render_template("sc/sc_detail.html", error="Error loading data")

    return render_template("sc/sc_detail.html", data=data, charts=charts)

@app.route("/scholarship/static/<path:filename>")
def serve_scholarship_static(filename):
    """Serve scholarship static files (CSS, JS)"""
    scholarship_static = BASE_DIR / 'Scholarship' / 'static'
    
    # Try direct file
    direct_path = scholarship_static / filename
    if direct_path.exists() and direct_path.is_file():
        return send_from_directory(scholarship_static, filename)
    
    # Try in subdirectories
    for subdir in ['css', 'js', 'images']:
        sub_path = scholarship_static / subdir
        if (sub_path / filename).exists():
            return send_from_directory(sub_path, filename)
    
    return send_from_directory(scholarship_static, filename)


# ============================================================================
# LOGIN MODULE (Blueprint)
# ============================================================================

app.register_blueprint(login_bp, url_prefix="/login")


# ============================================================================
# ADMIN PANEL MODULE
# ============================================================================

@app.route("/admin")
def admin_home():
    """Admin panel homepage"""
    return send_from_directory(BASE_DIR / 'Admin Panel' / 'frontend', 'index.html')

@app.route("/admin/<page>")
def admin_page(page):
    """Serve admin panel pages"""
    valid_pages = ['dashboard', 'analytics', 'announcements', 'feedback', 'kb', 'logs', 'settings']
    if page in valid_pages:
        return send_from_directory(BASE_DIR / 'Admin Panel' / 'frontend', f'{page}.html')
    return redirect(url_for('admin_home'))

@app.route("/admin/assets/<path:filename>")
def serve_admin_assets(filename):
    """Serve admin panel assets"""
    return send_from_directory(BASE_DIR / 'Admin Panel' / 'frontend' / 'assets', filename)


# ============================================================================
# USER PROFILE MODULE
# ============================================================================

@app.route("/profile")
def user_profile():
    """User profile card page"""
    return send_from_directory(
        BASE_DIR / 'UserProfileCard_02' / 'UserProfileCard_02',
        'index.html'
    )

@app.route("/profile/<path:filename>")
def serve_profile_static(filename):
    """Serve user profile static files"""
    return send_from_directory(
        BASE_DIR / 'UserProfileCard_02' / 'UserProfileCard_02',
        filename
    )


# ============================================================================
# LOGO & ASSETS
# ============================================================================

@app.route("/logo/<path:filename>")
def serve_logo(filename):
    """Serve logo files"""
    return send_from_directory(BASE_DIR / 'logo', filename)

@app.route("/sidebar/<path:filename>")
def serve_sidebar(filename):
    """Serve sidebar assets"""
    return send_from_directory(BASE_DIR / 'sidebar', filename)

@app.route("/intro/<path:filename>")
def serve_intro(filename):
    """Serve intro video files"""
    return send_from_directory(BASE_DIR / 'intro', filename)


# ============================================================================
# API STATUS ENDPOINT
# ============================================================================

@app.route("/api/status")
def api_status():
    """API status check"""
    return jsonify({
        "status": "running",
        "message": "College Chatbot Server",
        "endpoints": {
            "chatbot": "/chat",
            "main": "/",
            "faculty": "/faculty",
            "syllabus": "/syllabus",
            "notice": "/notice",
            "scholarship": "/scholarship",
            "login": "/login",
            "admin": "/admin",
            "profile": "/profile"
        }
    })


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Page not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 College Chatbot Server Starting...")
    print("=" * 60)
    print(f"Main Homepage:     http://localhost:8081/")
    print(f"Faculty Page:      http://localhost:8081/faculty")
    print(f"Syllabus:          http://localhost:8081/syllabus")
    print(f"Notice Board:      http://localhost:8081/notice")
    print(f"Scholarships:      http://localhost:8081/scholarship")
    print(f"Login:             http://localhost:8081/login")
    print(f"Admin Panel:       http://localhost:8081/admin")
    print(f"User Profile:      http://localhost:8081/profile")
    print(f"API Status:        http://localhost:8081/api/status")
    print(f"Chatbot API:       http://localhost:8081/chat (POST)")
    print(f"Faculty Data API:  http://localhost:8081/faculty-data")
    print(f"Semesters API:     http://localhost:8081/semesters")
    print("=" * 60)
    
    app.run(debug=True, port=8081, host='0.0.0.0')