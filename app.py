from flask import Flask, render_template, request, jsonify, send_from_directory, abort, make_response, redirect, url_for, session
from flask_cors import CORS
import json
import difflib
import os
import requests
from dotenv import load_dotenv
import glob
from pathlib import Path
import traceback
import uuid
import re
import sqlite3
from datetime import datetime


# Load environment variables from .env
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # allow cross-origin if needed
app.secret_key = os.environ.get('SECRET_KEY', 'change_this_secret_for_prod')

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
SYLLABUS_DIR = os.path.join(os.path.dirname(__file__), 'syllabus')

# Admin Panel Database Connection
ADMIN_DB_PATH = os.path.join(os.path.dirname(__file__), 'Admin Panel', 'college_chatbot.db')

def get_admin_db():
    """Get connection to admin panel database"""
    conn = sqlite3.connect(ADMIN_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_all_json_files(root_dir=None):
    """Recursively find and load all .json and .jsonl files under root_dir (project root by default)."""
    root = Path(root_dir or os.path.dirname(__file__)).resolve()
    # We'll include files in subfolders, but skip virtual envs and hidden folders
    skip_dirs = {'.venv', 'venv', '__pycache__', '.git'}
    loaded = {}
    for p in root.rglob('*'):
        try:
            if p.is_dir():
                # skip undesired directories
                if p.name in skip_dirs:
                    # do not descend into these
                    continue
                else:
                    continue
            if p.suffix.lower() not in {'.json', '.jsonl'}:
                continue
            # Skip some large expected files if needed (none by default)
            rel = p.relative_to(root).as_posix()
            try:
                if p.suffix.lower() == '.json':
                    with p.open('r', encoding='utf-8') as fh:
                        data = json.load(fh)
                    loaded[rel] = data
                else:  # .jsonl
                    items = []
                    with p.open('r', encoding='utf-8') as fh:
                        for line in fh:
                            line = line.strip()
                            if not line: 
                                continue
                            try:
                                items.append(json.loads(line))
                            except Exception:
                                # keep raw line if it isn't JSON
                                items.append(line)
                    loaded[rel] = items
            except Exception as e:
                loaded[rel] = {'_load_error': str(e)}
        except Exception:
            # safety: continue on any path errors
            continue
    return loaded

def load_university_rules():
    """Load and organize university rules from the university_rule folder."""
    rules_dir = Path(os.path.dirname(__file__)) / 'university_rule'
    rules = {}
    
    if not rules_dir.exists():
        return rules
    
    # Define the rule categories
    rule_categories = {
        'admissions_and_eligibility': 'Admissions & Eligibility',
        'attendance_and_examinations': 'Attendance & Examinations',
        'campus_rules_and_facilities': 'Campus Rules & Facilities',
        'conduct_and_discipline': 'Conduct & Discipline',
        'co-curricular_and_outreach': 'Co-curricular & Outreach',
        'finance_and_scholarships': 'Finance & Scholarships',
        'health_and_counselling': 'Health & Counselling',
        'laboratories_and_safety': 'Laboratories & Safety',
        'legal_and_jurisdiction': 'Legal & Jurisdiction',
        'library_and_reading_room': 'Library & Reading Room',
        'social_media_and_communication': 'Social Media & Communication',
        'university_vision_and_mission': 'University Vision & Mission',
        'other': 'Other Rules'
    }
    
    for file_key, display_name in rule_categories.items():
        file_path = rules_dir / f'{file_key}.json'
        if file_path.exists():
            try:
                with file_path.open('r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                    rules[display_name] = rules_data
            except Exception as e:
                print(f"[WARNING] Could not load {file_path}: {e}")
    
    return rules


# Serve files from the syllabus folder (HTML, JSON, etc.)
@app.route('/syllabus/<path:filename>')
def serve_syllabus_file(filename):
    """Serve static files placed in the local `syllabus/` directory."""
    safe_dir = SYLLABUS_DIR
    # Ensure the directory exists
    if not os.path.isdir(safe_dir):
        abort(404)
    # Prevent directory traversal by normalizing the path
    requested = os.path.normpath(os.path.join(safe_dir, filename))
    if not requested.startswith(os.path.normpath(safe_dir)):
        abort(403)
    if not os.path.exists(requested):
        abort(404)
    return send_from_directory(safe_dir, filename)

# Load on startup
try:
    LOADED_DOCS = load_all_json_files()
    UNIVERSITY_RULES = load_university_rules()
    print(f"[INFO] Loaded {len(UNIVERSITY_RULES)} university rule categories")
    
    # Debug: Log scholarship files specifically
    scholarship_files = [path for path in LOADED_DOCS.keys() if 'scholarship' in path.lower()]
    detailed_scholarship_files = [path for path in scholarship_files if 'detailed scholarship' in path.lower()]
    print(f"[INFO] Loaded {len(scholarship_files)} scholarship-related files")
    print(f"[INFO] Loaded {len(detailed_scholarship_files)} detailed scholarship files:")
    for sf in detailed_scholarship_files:
        print(f"  - {sf}")
except Exception as e:
    print(f"[ERROR] Failed to load files: {e}")
    LOADED_DOCS = {}
    UNIVERSITY_RULES = {}

def write_ai_prompt_file(prompt_path='ai_prompt.txt'):
    """Create a simple AI prompt file that lists loaded files and how the AI should use them."""
    try:
        root = Path(os.path.dirname(__file__)).resolve()
        p = root.joinpath(prompt_path)
        with p.open('w', encoding='utf-8') as fh:
            fh.write('AI PROMPT FILE\n')
            fh.write('================\n')
            fh.write('Instruction: You are an assistant that must answer user queries strictly using the provided project files listed below.\n')
            fh.write('When answering, cite the source file path(s) that support your answer. If the information is not available, say you do not know and optionally suggest where to look.\n\n')
            fh.write('Loaded files manifest:\n')
            for rel, content in LOADED_DOCS.items():
                fh.write(f'- {rel}\n')
                # write a tiny sample summary when possible
                try:
                    if isinstance(content, dict):
                        # list top-level keys
                        keys = list(content.keys())[:6]
                        fh.write(f'  top_keys: {keys}\n')
                    elif isinstance(content, list):
                        fh.write(f'  items: {len(content)}\n')
                    else:
                        fh.write(f'  type: {type(content)}\n')
                except Exception:
                    fh.write('  sample: (unable to display)\n')
            fh.write('\nPrompt template:\n')
            fh.write('Answer as the campus assistant. Include file citations like [sem_explain/sem_01/HSMCM101.json].\n')
        return str(p)
    except Exception:
        return None

# create the prompt file once at startup
PROMPT_FILE_PATH = write_ai_prompt_file()


# Load cleaned hostel rule book for context
with open('hostel-rule-book-2025-26.cleaned.txt', 'r', encoding='utf-8') as f:
    hostel_rules_text = f.read()

# Load holiday list
with open(os.path.join(STATIC_DIR, 'holiday.json'), 'r', encoding='utf-8') as f:
    holiday_json = json.load(f)
holiday_text = '\n'.join([
    f"{h['date']} ({h['day']}): {h['event']}" for h in holiday_json
])

# Load faculty details
with open(os.path.join(os.path.dirname(__file__), 'Faculty', 'brainware_cse_ai_faculty.json'), 'r', encoding='utf-8') as f:
    faculty_json = json.load(f)
faculty_text = f"Department: {faculty_json.get('department', '')}\n" + '\n'.join([
    f"{v['name']} - {v['position']}, {v['qualification']}. Research: {', '.join(v['research_area']) if v.get('research_area') else 'N/A'}" for v in faculty_json.get('faculty', {}).values()
])

# Load helplines data
with open(os.path.join(os.path.dirname(__file__), 'Helplines', 'helplines.json'), 'r', encoding='utf-8') as f:
    helplines_json = json.load(f)

# Load academic calendar
with open(os.path.join(os.path.dirname(__file__), 'academic.json'), 'r', encoding='utf-8') as f:
    academic_json = json.load(f)
academic_text = '\n'.join([f"{k}: {v}" for k, v in academic_json.items()])

# --- Session management for conversation history ---
CHAT_HISTORY = {}  # key: session_id, value: list of {role, content}
USER_PROFILES = {}  # key: session_id, value: profile dict (course, year, community, income)

def get_or_create_session():
    """Get or create a session ID from cookie."""
    session_id = request.cookies.get('chat_session_id')
    if not session_id or session_id not in CHAT_HISTORY:
        session_id = str(uuid.uuid4())
        CHAT_HISTORY[session_id] = []
    return session_id


@app.route('/api/profile', methods=['POST'])
def set_profile():
    """Set a small user profile (course, year, community, income) for personalization."""
    try:
        data = request.get_json(force=True) or {}
        session_id = get_or_create_session()
        # accept only expected keys
        profile = {
            'course': data.get('course'),
            'year': data.get('year'),
            'community': data.get('community'),
            'income': data.get('income')
        }
        # remove None values
        profile = {k: v for k, v in profile.items() if v is not None}
        USER_PROFILES[session_id] = profile
        resp = make_response(jsonify({'status': 'ok', 'profile': profile}))
        resp.set_cookie('chat_session_id', session_id, max_age=86400, httponly=True)
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def sanitize_text(text):
    """Remove markdown artifacts and control characters from text."""
    if not text:
        return text
    # Remove source citations like [sem_explain/sem_01/BSCM101.json]
    text = re.sub(r'\s*\[[\w\-_/\.]+\.json\]\s*', '', text)
    # Remove markdown bold/italic markers
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)      # *italic*
    text = re.sub(r'`([^`]+)`', r'\1', text)         # `code`
    # Remove control characters except newlines/tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    return text.strip()

def find_relevant_helpline(query):
    """Find the most relevant helpline contact based on the user query."""
    query_lower = query.lower()
    
    # Check each category for keyword matches
    for category in helplines_json.get('categories', []):
        keywords = category.get('keywords', [])
        for keyword in keywords:
            if keyword.lower() in query_lower:
                # Build contact response
                contact_info = f"\n\n📞 **Contact Information:**\n"
                
                if 'contact_persons' in category:
                    # Multiple contact persons
                    contact_info += f"Department: {category.get('department', 'N/A')}\n"
                    contact_info += "Contact persons:\n"
                    for person in category['contact_persons']:
                        contact_info += f"  • {person['name']}: {person['phone']}\n"
                else:
                    # Single contact person
                    contact_info += f"Contact: {category.get('contact_person', 'N/A')}\n"
                    if category.get('department'):
                        contact_info += f"Department: {category['department']}\n"
                    contact_info += f"Phone: {category.get('phone', 'N/A')}\n"
                
                contact_info += "\n⏰ **Office Hours:** 9:00 AM - 6:00 PM (Monday to Saturday)\n"
                contact_info += "📅 **Note:** Closed on Sundays and public holidays."
                
                return contact_info
    
    # No specific category matched - return fallback contact
    fallback = helplines_json.get('fallback_contact', {})
    contact_info = f"\n\n📞 **Contact Information:**\n"
    contact_info += f"For assistance, please contact:\n"
    contact_info += f"Contact: {fallback.get('name', 'Registrar\'s Office')}\n"
    contact_info += f"Phone: {fallback.get('phone', '033-69010507')}\n"
    contact_info += "\n⏰ **Office Hours:** 9:00 AM - 6:00 PM (Monday to Saturday)\n"
    contact_info += "📅 **Note:** Closed on Sundays and public holidays."
    
    return contact_info

def get_university_rules_context(query=None):
    """Build comprehensive context from university rules, optionally filtered by query."""
    if not UNIVERSITY_RULES:
        return ""
    
    # Keywords that indicate a rule-related query
    rule_keywords = [
        'rule', 'policy', 'regulation', 'allowed', 'prohibited', 'banned', 'can i', 'am i allowed',
        'discipline', 'attendance', 'exam', 'library', 'dress code', 'mobile', 'phone', 'laptop',
        'id card', 'uniform', 'smoking', 'alcohol', 'fine', 'penalty', 'suspension', 'canteen',
        'admission', 'eligibility', 'scholarship', 'fee', 'hostel', 'laboratory', 'safety',
        'conduct', 'ragging', 'health', 'counselling', 'vision', 'mission', 'legal', 'jurisdiction'
    ]
    
    context_parts = []
    
    # Check if this is a rule-related query
    is_rule_query = query and any(keyword in query.lower() for keyword in rule_keywords)
    
    if is_rule_query or query is None:
        context_parts.append("=== UNIVERSITY RULES & POLICIES ===\n")
        context_parts.append("The following comprehensive rules and policies are available:\n")
        
        # Add rules from each category
        for category, rules_list in UNIVERSITY_RULES.items():
            if not rules_list:
                continue
            
            # If query provided, filter rules relevant to the query
            if query:
                query_lower = query.lower()
                relevant_rules = []
                for rule in rules_list:
                    rule_text = f"{rule.get('title', '')} {rule.get('text', '')} {rule.get('section', '')}".lower()
                    # Check if any query word appears in this rule
                    query_words = query_lower.split()
                    if any(word in rule_text for word in query_words if len(word) > 3):
                        relevant_rules.append(rule)
                
                if relevant_rules:
                    context_parts.append(f"\n**{category}** ({len(relevant_rules)} relevant rules):")
                    for rule in relevant_rules[:5]:  # Top 5 relevant rules per category
                        context_parts.append(f"  - [{rule.get('section', 'General')}] {rule.get('title', 'N/A')}: {rule.get('text', 'N/A')}")
            else:
                # No query - provide summary of all categories
                context_parts.append(f"\n**{category}** ({len(rules_list)} rules available)")
                # Show first 2 rules as examples
                for rule in rules_list[:2]:
                    context_parts.append(f"  - {rule.get('title', 'N/A')}: {rule.get('text', 'N/A')[:100]}...")
    
    return '\n'.join(context_parts) if context_parts else ""

def retrieve_top_k(query, k=5):
    """Enhanced keyword-based retrieval from LOADED_DOCS with university rules priority."""
    query_lower = query.lower()
    scores = []
    
    # Extract potential course codes (e.g., BSCM101, PCC-CSM301)
    import re
    course_code_pattern = r'\b[A-Z]{2,}[-]?[A-Z]{0,3}\d{3}[A-Z]?\b'
    course_codes = re.findall(course_code_pattern, query.upper())
    
    # Build search terms: include original full query, extracted course codes, and individual words
    search_terms = [query_lower]
    # add course codes if found
    if course_codes:
        search_terms.extend([code.lower() for code in course_codes])
    # also include individual words (length>=3) to improve recall
    import re as _re_tmp
    words = _re_tmp.findall(r"\w{3,}", query_lower)
    for w in words:
        if w not in search_terms:
            search_terms.append(w)
    # synonyms map for common scholarship names
    synonyms = {
        'kanyashree': ['kanya shree', 'kanya-shree', 'kanyashree prakalpa', 'kanyashree prakalpa'],
        'aikyashree': ['aikyashree', 'aikya shree'],
        'kanya': ['kanyashree']
    }
    # expand search terms with synonyms
    for t in list(search_terms):
        for syn_key, vals in synonyms.items():
            if syn_key in t:
                for v in vals:
                    if v not in search_terms:
                        search_terms.append(v)
    
    # Check if this is a rule-related query
    rule_keywords = ['rule', 'policy', 'allowed', 'prohibited', 'banned', 'can i', 'discipline', 
                     'attendance', 'exam', 'library', 'dress code', 'mobile', 'fine', 'penalty']
    is_rule_query = any(keyword in query_lower for keyword in rule_keywords)
    # Detect scholarship-related queries to prefer scholarship files
    scholarship_keywords = ['scholarship', 'kanyashree', 'kanya', 'aikyashree', 'kanyashree prakalpa', 'k2', 'k3', 
                           'nabanna', 'vivekananda', 'vidyalankar', 'oasis', 'medha britti', 'credit card', 
                           'sports scholarship', 'financial aid', 'financial assistance', 'grant', 'stipend']
    is_scholarship_query = any(keyword in query_lower for keyword in scholarship_keywords)
    
    for rel_path, content in LOADED_DOCS.items():
        try:
            text = json.dumps(content) if isinstance(content, (dict, list)) else str(content)
            text_lower = text.lower()
            
            # Score based on all search terms
            total_count = 0
            for term in search_terms:
                total_count += text_lower.count(term)
            
            # Boost score for university_rule files if it's a rule query
            score_multiplier = 1.0
            if is_rule_query and 'university_rule' in rel_path:
                score_multiplier = 3.0  # 3x boost for rule files
            
            # If user asked about scholarships, prefer docs in scholarship folder or containing scholarship keywords
            if is_scholarship_query:
                # Check if filename contains any specific scholarship name from query
                filename = rel_path.split('/')[-1].lower().replace('.json', '')
                exact_match = False
                matched_term = ""
                for term in search_terms:
                    if term and len(term) > 3 and term in filename:
                        exact_match = True
                        matched_term = term
                        break
                
                # Highest priority for exact filename match in detailed scholarship folder
                if exact_match and 'scholarship/data/detailed scholarship' in rel_path.lower():
                    # Add base count for matched term to ensure it ranks high
                    total_count += 50  # Boost base count significantly
                    score_multiplier += 15.0  # Very high multiplier for exact matches
                # High priority for detailed scholarship folder
                elif 'scholarship/data/detailed scholarship' in rel_path.lower():
                    score_multiplier += 5.0
                # Medium priority for other scholarship-related files
                elif 'scholarship' in rel_path.lower() or any(sk in text_lower for sk in scholarship_keywords):
                    score_multiplier += 3.0
            # Slightly boost if the file path contains any search term (helps folder name matches)
            for term in search_terms:
                if term and term in rel_path.lower():
                    score_multiplier += 0.5
            # Fuzzy similarity boost between query and file path/name
            try:
                import difflib as _dif
                path_score = _dif.SequenceMatcher(None, query_lower, rel_path.lower()).ratio()
                if path_score > 0.45:
                    score_multiplier += path_score  # boost proportional to similarity
            except Exception:
                pass
            
            if total_count > 0:
                # Extract snippet around the first search term found
                pos = -1
                for term in search_terms:
                    pos = text_lower.find(term)
                    if pos >= 0:
                        break
                
                if pos >= 0:
                    start = max(0, pos - 100)
                    end = min(len(text), pos + 200)
                    snippet = text[start:end].replace('\n', ' ')
                else:
                    snippet = text[:200].replace('\n', ' ')
                
                scores.append({
                    'path': rel_path,
                    'score': total_count * score_multiplier,
                    'snippet': snippet,
                    'full_content': content
                })
        except Exception as e:
            print(f"[DEBUG] Error processing {rel_path}: {e}")
            continue
    
    # Sort by score descending
    scores.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"[DEBUG] retrieve_top_k: query='{query}', search_terms={search_terms}, found {len(scores)} docs")
    if scores:
        print(f"[DEBUG] Top 3: {[(s['path'], s['score']) for s in scores[:3]]}")
    
    return scores[:k]

def build_context_from_docs(query):
    """Build rich context from loaded JSON files based on query."""
    # Get relevant documents
    relevant_docs = retrieve_top_k(query, k=8)
    
    if not relevant_docs:
        return "No relevant information found in the knowledge base."

    # Helper: detect scholarship-like documents
    def is_scholarship_doc(p, c):
        if isinstance(c, dict):
            keys = set(k.lower() for k in c.keys())
            if 'scholarship_name' in keys or 'official_name' in keys or 'scholarship_id' in keys:
                return True
        # also check path for scholarship folder
        if isinstance(p, str) and 'scholarship' in p.lower():
            return True
        return False

    def format_scholarship_context(p, c):
        # Build a comprehensive, structured summary with full details for AI personalization
        parts = [f"\n[SCHOLARSHIP DATA - Source: {p}]\n"]
        parts.append("=" * 80 + "\n")
        
        # Basic Information
        name = c.get('scholarship_name') or c.get('official_name') or c.get('popular_name') or c.get('title')
        if name:
            parts.append(f"SCHOLARSHIP NAME: {name}\n")
        if c.get('scholarship_id'):
            parts.append(f"ID: {c.get('scholarship_id')}\n")
        if c.get('scholarship_type'):
            parts.append(f"TYPE: {c.get('scholarship_type')}\n")
        
        # Overview/Introduction
        intro = c.get('introduction') or c.get('overview', {}).get('description')
        if intro:
            parts.append(f"\nOVERVIEW:\n{intro}\n")
        
        # Eligibility Criteria (COMPREHENSIVE)
        elig = c.get('eligibility') or c.get('eligibility_criteria') or c.get('who_should_apply')
        if elig:
            parts.append("\nELIGIBILITY CRITERIA:\n")
            if isinstance(elig, dict):
                parts.append(json.dumps(elig, indent=2, ensure_ascii=False) + "\n")
            elif isinstance(elig, list):
                for item in elig:
                    parts.append(f"  - {item}\n")
            else:
                parts.append(f"{elig}\n")
        
        # Income Criteria
        if c.get('income_limit') or (isinstance(elig, dict) and elig.get('income_criteria')):
            income_info = c.get('income_limit') or elig.get('income_criteria')
            parts.append(f"\nINCOME LIMIT: {json.dumps(income_info, ensure_ascii=False) if isinstance(income_info, dict) else income_info}\n")
        
        # Target Group/Communities
        if c.get('target_group'):
            parts.append(f"\nTARGET GROUP: {c.get('target_group')}\n")
        if c.get('minority_communities_covered'):
            parts.append(f"COMMUNITIES COVERED: {', '.join(c.get('minority_communities_covered'))}\n")
        
        # Academic Levels
        if c.get('academic_level'):
            parts.append(f"\nACADEMIC LEVELS: {', '.join(c.get('academic_level')) if isinstance(c.get('academic_level'), list) else c.get('academic_level')}\n")
        if c.get('course_levels_supported'):
            parts.append(f"\nCOURSE LEVELS SUPPORTED:\n{json.dumps(c.get('course_levels_supported'), indent=2, ensure_ascii=False)}\n")
        
        # Benefits (COMPREHENSIVE)
        benefits = c.get('scholarship_benefits') or c.get('benefits')
        if benefits:
            parts.append("\nBENEFITS:\n")
            if isinstance(benefits, dict):
                parts.append(json.dumps(benefits, indent=2, ensure_ascii=False) + "\n")
            elif isinstance(benefits, list):
                for item in benefits:
                    parts.append(f"  - {item}\n")
            else:
                parts.append(f"{benefits}\n")
        
        # Application Process
        app = c.get('application_process') or c.get('how_to_apply') or c.get('application_steps')
        if app:
            parts.append("\nAPPLICATION PROCESS:\n")
            if isinstance(app, dict):
                parts.append(json.dumps(app, indent=2, ensure_ascii=False) + "\n")
            elif isinstance(app, list):
                for idx, step in enumerate(app, 1):
                    parts.append(f"  Step {idx}: {step}\n")
            else:
                parts.append(f"{app}\n")
        
        # Required Documents
        if c.get('required_documents'):
            parts.append("\nREQUIRED DOCUMENTS:\n")
            parts.append(json.dumps(c.get('required_documents'), indent=2, ensure_ascii=False) + "\n")
        
        # Important Dates/Deadlines
        if c.get('important_dates'):
            parts.append(f"\nIMPORTANT DATES:\n{json.dumps(c.get('important_dates'), indent=2, ensure_ascii=False)}\n")
        
        # FAQ
        if c.get('faq'):
            parts.append("\nFREQUENTLY ASKED QUESTIONS:\n")
            faq_data = c.get('faq')
            if isinstance(faq_data, list):
                parts.append(json.dumps(faq_data[:5], indent=2, ensure_ascii=False) + "\n")
            else:
                parts.append(str(faq_data) + "\n")
        
        # Contact/Source
        if c.get('data_source'):
            parts.append(f"\nDATA SOURCE: {c.get('data_source')}\n")
        if c.get('official_website'):
            parts.append(f"OFFICIAL WEBSITE: {c.get('official_website')}\n")
        
        parts.append("=" * 80 + "\n")
        parts.append("\n🎯 PERSONALIZATION INSTRUCTIONS FOR AI:\n")
        parts.append("- DO NOT copy-paste this data verbatim\n")
        parts.append("- READ and UNDERSTAND the eligibility, benefits, and requirements\n")
        parts.append("- PERSONALIZE your answer based on the user's specific question\n")
        parts.append("- If user mentions their year/course/income/community, tailor eligibility check accordingly\n")
        parts.append("- Provide relevant next steps specific to their situation\n")
        parts.append("- Use conversational, helpful language - not raw data dump\n")
        parts.append("- Focus on what matters to THEIR specific query\n")
        parts.append("=" * 80 + "\n")
        
        return ''.join(parts)

    def format_generic_dict(p, c):
        """Format any dictionary content - faculty, courses, exams, holidays, etc."""
        summary = f"\n[Source: {p}]\n"
        
        # Faculty data
        if 'name' in c and 'designation' in c:
            summary += f"Faculty: {c.get('name')}\n"
            summary += f"Designation: {c.get('designation')}\n"
            if 'email' in c:
                summary += f"Email: {c.get('email')}\n"
            if 'phone' in c:
                summary += f"Phone: {c.get('phone')}\n"
            if 'specialization' in c:
                summary += f"Specialization: {c.get('specialization')}\n"
            if 'qualification' in c:
                summary += f"Qualification: {c.get('qualification')}\n"
            return summary
        
        # Exam data
        if 'exam_name' in c or 'exam_date' in c:
            if 'exam_name' in c:
                summary += f"Exam: {c.get('exam_name')}\n"
            if 'exam_date' in c:
                summary += f"Date: {c.get('exam_date')}\n"
            if 'time' in c:
                summary += f"Time: {c.get('time')}\n"
            if 'duration' in c:
                summary += f"Duration: {c.get('duration')}\n"
            if 'subjects' in c and isinstance(c['subjects'], list):
                summary += f"Subjects: {', '.join(c['subjects'])}\n"
            return summary
        
        # Holiday data
        if 'holiday_name' in c or ('date' in c and 'day' in c):
            if 'holiday_name' in c:
                summary += f"Holiday: {c.get('holiday_name')}\n"
            if 'date' in c:
                summary += f"Date: {c.get('date')}\n"
            if 'day' in c:
                summary += f"Day: {c.get('day')}\n"
            return summary
        
        # Course/Subject data
        course_name = c.get('subject_name') or c.get('course_name')
        course_code = c.get('subject_code') or c.get('course_code')
        if course_name or course_code:
            if course_name:
                summary += f"Subject: {course_name}\n"
            if course_code:
                summary += f"Code: {course_code}\n"
            if 'summary' in c:
                summary += f"Summary: {c.get('summary', 'N/A')}\n"
            if 'modules' in c:
                summary += f"Modules ({len(c.get('modules', []))}):\n"
                for mod in c.get('modules', [])[:5]:
                    mod_num = mod.get('module_no') or mod.get('module_number', '?')
                    summary += f"  - Module {mod_num}: {mod.get('title', 'N/A')}\n"
            if 'course_outcomes' in c and c['course_outcomes']:
                summary += f"Course Outcomes ({len(c['course_outcomes'])}):\n"
                for i, outcome in enumerate(c['course_outcomes'][:3], 1):
                    summary += f"  {i}. {outcome}\n"
            if 'prerequisites' in c and c['prerequisites']:
                summary += f"Prerequisites: {', '.join(c['prerequisites'][:3])}\n"
            return summary
        
        # Generic fallback - show all key-value pairs (for hostel rules, library info, etc.)
        summary += "Content:\n"
        for key, value in c.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, (str, int, float, bool)):
                summary += f"  {formatted_key}: {value}\n"
            elif isinstance(value, list):
                summary += f"  {formatted_key}: "
                if all(isinstance(item, (str, int, float)) for item in value[:3]):
                    summary += ', '.join(str(v) for v in value[:3])
                    if len(value) > 3:
                        summary += f" (+{len(value)-3} more)"
                    summary += "\n"
                else:
                    summary += f"[{len(value)} items]\n"
                    for item in value[:3]:
                        if isinstance(item, dict):
                            summary += f"    - {json.dumps(item, ensure_ascii=False)[:100]}...\n"
                        else:
                            summary += f"    - {str(item)[:100]}\n"
            elif isinstance(value, dict):
                summary += f"  {formatted_key}: {json.dumps(value, ensure_ascii=False)[:200]}\n"
        
        return summary

    context_parts = []
    for doc in relevant_docs:
        path = doc['path']
        content = doc['full_content']

        if is_scholarship_doc(path, content):
            try:
                context_parts.append(format_scholarship_context(path, content))
            except Exception:
                context_parts.append(f"\n[Source: {path}] (scholarship content could not be summarized)\n")
        elif isinstance(content, dict):
            context_parts.append(format_generic_dict(path, content))
        elif isinstance(content, list):
            # Better formatting for lists
            summary = f"\n[Source: {path}]\nContains {len(content)} items:\n"
            for idx, item in enumerate(content[:10], 1):  # Show first 10 items
                if isinstance(item, dict):
                    # Extract key info from dict items
                    item_summary = []
                    for key, value in list(item.items())[:5]:  # First 5 keys
                        if isinstance(value, (str, int, float, bool)):
                            item_summary.append(f"{key}: {value}")
                    summary += f"  {idx}. {', '.join(item_summary)}\n"
                else:
                    # Plain strings or numbers
                    summary += f"  {idx}. {str(item)[:200]}\n"
            if len(content) > 10:
                summary += f"  ... and {len(content) - 10} more items\n"
            context_parts.append(summary)
        elif isinstance(content, str):
            # Plain text content (like hostel rules from JSONL)
            summary = f"\n[Source: {path}]\n"
            # Show first 800 characters of text content
            if len(content) > 800:
                summary += content[:800] + "...\n[Text truncated for context]\n"
            else:
                summary += content + "\n"
            context_parts.append(summary)
        else:
            # Unknown type - show as is
            context_parts.append(f"\n[Source: {path}]\n{str(content)[:500]}\n")

    return '\n'.join(context_parts)

def format_scholarship_for_user(content):
    """Format scholarship data in a clean, user-friendly way"""
    parts = []
    
    # Scholarship name
    name = content.get('scholarship_name') or content.get('official_name') or content.get('popular_name') or content.get('title', 'Scholarship Information')
    # Clean up name (remove markdown symbols for cleaner display)
    name = name.replace('**', '').replace('🌸', '').strip()
    parts.append(f"📚 {name}\n")
    parts.append("=" * 60 + "\n\n")
    
    # Overview/Introduction
    intro = content.get('introduction') or (content.get('overview', {}).get('description') if isinstance(content.get('overview'), dict) else content.get('overview'))
    if intro:
        parts.append(f"ℹ️ Overview:\n{intro}\n\n")
    
    # Grant Amount (if available)
    grant = content.get('grant_amount')
    if grant:
        if isinstance(grant, dict):
            amount = grant.get('amount', '')
            payment_type = grant.get('payment_type', '')
            if amount:
                parts.append(f"💰 Grant Amount: {amount}")
                if payment_type:
                    parts.append(f" ({payment_type})")
                parts.append("\n\n")
        else:
            parts.append(f"💰 Grant Amount: {grant}\n\n")
    
    # Eligibility - Format nicely
    elig = content.get('eligibility') or content.get('eligibility_criteria') or content.get('who_should_apply')
    if elig:
        parts.append("✅ Eligibility:\n")
        if isinstance(elig, dict):
            # Handle nested eligibility criteria
            for key, value in elig.items():
                key_display = key.replace('_', ' ').title()
                if isinstance(value, dict):
                    parts.append(f"  • {key_display}:\n")
                    for sub_key, sub_val in value.items():
                        sub_key_display = sub_key.replace('_', ' ').title()
                        if isinstance(sub_val, str):
                            clean_val = sub_val.replace('*', '').replace('**', '')
                            parts.append(f"    - {sub_key_display}: {clean_val}\n")
                        else:
                            parts.append(f"    - {sub_key_display}: {sub_val}\n")
                elif isinstance(value, list):
                    parts.append(f"  • {key_display}:\n")
                    for item in value:
                        clean_item = str(item).replace('*', '').replace('**', '').replace('🎯', '').strip()
                        parts.append(f"    - {clean_item}\n")
                else:
                    clean_val = str(value).replace('*', '').replace('**', '')
                    parts.append(f"  • {key_display}: {clean_val}\n")
        elif isinstance(elig, list):
            for item in elig:
                clean_item = str(item).replace('*', '').replace('**', '').replace('🎯', '').strip()
                parts.append(f"  • {clean_item}\n")
        else:
            parts.append(f"  {str(elig).replace('*', '')}\n")
        parts.append("\n")
    
    # Income Limit
    income = content.get('income_limit')
    if not income and isinstance(elig, dict):
        income = elig.get('income_criteria') or elig.get('income_limit')
    if income:
        parts.append("💵 Income Criteria:\n")
        if isinstance(income, dict):
            for key, value in income.items():
                key_display = key.replace('_', ' ').title()
                parts.append(f"  • {key_display}: {value}\n")
        else:
            parts.append(f"  • {income}\n")
        parts.append("\n")
    
    # Benefits
    benefits = content.get('scholarship_benefits') or content.get('benefits')
    if benefits:
        parts.append("🎁 Benefits:\n")
        if isinstance(benefits, dict):
            for key, value in benefits.items():
                key_display = key.replace('_', ' ').title()
                if isinstance(value, list):
                    parts.append(f"  • {key_display}:\n")
                    for item in value:
                        parts.append(f"    - {item}\n")
                else:
                    parts.append(f"  • {key_display}: {value}\n")
        elif isinstance(benefits, list):
            for item in benefits:
                parts.append(f"  • {item}\n")
        else:
            parts.append(f"  {benefits}\n")
        parts.append("\n")
    
    # Application Process
    app_process = content.get('application_process') or content.get('how_to_apply') or content.get('application_steps')
    if app_process:
        parts.append("📝 How to Apply:\n")
        if isinstance(app_process, dict):
            mode = app_process.get('mode')
            if mode:
                parts.append(f"  Mode: {mode.replace('**', '').replace('🖥', '').strip()}\n")
            steps = app_process.get('steps')
            if steps and isinstance(steps, list):
                parts.append("  Steps:\n")
                for i, step in enumerate(steps, 1):
                    clean_step = str(step).replace('🔹', '').replace('**', '').strip()
                    parts.append(f"    {i}. {clean_step}\n")
        elif isinstance(app_process, list):
            for i, step in enumerate(app_process, 1):
                clean_step = str(step).replace('🔹', '').replace('**', '').strip()
                parts.append(f"  {i}. {clean_step}\n")
        else:
            parts.append(f"  {str(app_process).replace('**', '')}\n")
        parts.append("\n")
    
    # Important Dates
    dates = content.get('important_dates')
    if dates:
        parts.append("📅 Important Dates:\n")
        if isinstance(dates, dict):
            for key, value in dates.items():
                key_display = key.replace('_', ' ').title()
                parts.append(f"  • {key_display}: {value}\n")
        parts.append("\n")
    
    # Official Website
    website = content.get('official_website')
    if website:
        parts.append(f"🌐 Official Website: {website}\n\n")
    
    # Add a helpful note
    parts.append("💡 Tip: For detailed eligibility verification, please check the official portal or contact the scholarship office.\n")
    
    return ''.join(parts)

def get_notice_context():
    """Get current notices context for AI"""
    try:
        notices = []
        
        # Get PDF-based notices
        notices_dir = os.path.join(os.path.dirname(__file__), 'notice', 'pdfs')
        if os.path.exists(notices_dir):
            for filename in os.listdir(notices_dir):
                if filename.endswith('.pdf'):
                    parts = filename[:-4].split('--')
                    if len(parts) >= 3:
                        category = parts[0].strip()
                        title = parts[1].strip()
                        date = parts[2].strip()
                        notices.append({
                            'category': category,
                            'title': title,
                            'date': date,
                            'type': 'pdf'
                        })
        
        # Get announcements from admin panel
        try:
            conn = get_admin_db()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT title, body, published_at
                FROM announcements
                WHERE is_active = 1 
                AND visible_to_chatbot = 1
                AND published_at IS NOT NULL
                AND published_at <= datetime('now')
                ORDER BY published_at DESC
                LIMIT 20
            ''')
            
            for row in cursor.fetchall():
                published_date = row[2].split(' ')[0] if row[2] else datetime.now().strftime('%Y-%m-%d')
                notices.append({
                    'category': 'Announcement',
                    'title': row[0],
                    'date': published_date,
                    'body': row[1][:200] if row[1] else '',
                    'type': 'announcement'
                })
            conn.close()
        except Exception as e:
            print(f"[WARNING] Could not fetch announcements for AI: {e}")
        
        # Sort by date (newest first)
        notices.sort(key=lambda x: x['date'], reverse=True)
        
        # Build context text
        if not notices:
            return "NOTICES: No notices currently available."
        
        context = f"NOTICES (Total: {len(notices)}):\n"
        context += "IMPORTANT: When asked about notices, inform the user that notices are available and tell them to check Academic → Notice section for full details.\n\n"
        
        # Add recent notices (last 10)
        for notice in notices[:10]:
            context += f"- [{notice['date']}] {notice['category']}: {notice['title']}"
            if notice.get('body'):
                context += f" - {notice['body'][:100]}..."
            context += "\n"
        
        if len(notices) > 10:
            context += f"\n... and {len(notices) - 10} more notices available in the Notice panel.\n"
        
        return context
    except Exception as e:
        print(f"[ERROR] Failed to get notice context: {e}")
        return "NOTICES: Unable to fetch current notices."

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(force=True)
    user_query = data.get('query', '').strip()
    if not user_query:
        return jsonify({'error': 'No query provided.'}), 400

    # Get or create session
    session_id = get_or_create_session()
    
    # Sanitize input
    user_query_clean = sanitize_text(user_query)
    
    # Check for basic greetings first (quick response)
    greeting_patterns = ['hi', 'hello', 'hey', 'namaste', 'good morning', 'good afternoon', 'good evening']
    user_lower = user_query_clean.lower()
    for greeting in greeting_patterns:
        if user_lower == greeting or user_lower.startswith(greeting + ' ') or user_lower.startswith(greeting + ','):
            bot_answer = knowledge.get(greeting, knowledge.get('hello', 'Hello! How can I help you today?'))
            CHAT_HISTORY[session_id].append({'role': 'user', 'content': user_query_clean})
            CHAT_HISTORY[session_id].append({'role': 'assistant', 'content': bot_answer})
            log_student_query(user_query_clean, bot_answer, session_id)
            resp = make_response(jsonify({"response": bot_answer, "sources": []}))
            resp.set_cookie('chat_session_id', session_id, max_age=86400, httponly=True)
            return resp
    
    # Add user message to history
    CHAT_HISTORY[session_id].append({'role': 'user', 'content': user_query_clean})
    
    # Keep only last 10 messages to avoid token overflow
    if len(CHAT_HISTORY[session_id]) > 10:
        CHAT_HISTORY[session_id] = CHAT_HISTORY[session_id][-10:]

    # Build context from loaded JSON files
    json_context = build_context_from_docs(user_query_clean)
    
    # Build university rules context
    university_rules_context = get_university_rules_context(user_query_clean)
    
    # Debug logging
    print(f"\n[DEBUG] Query: {user_query_clean}")
    print(f"[DEBUG] Context length: {len(json_context)} chars")
    print(f"[DEBUG] Rules context length: {len(university_rules_context)} chars")
    print(f"[DEBUG] Context preview: {json_context[:300]}...")
    
    # Build conversation history for prompt
    history_text = ""
    for msg in CHAT_HISTORY[session_id][-6:]:  # Last 3 exchanges
        role = "User" if msg['role'] == 'user' else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    # Gemini API endpoint and key from .env
    api_url = os.environ.get('GEMINI_API_URL')
    api_key = os.environ.get('GEMINI_API_KEY')
    
    # Build comprehensive prompt with strict instructions
    # Include high-priority global texts (hostel rules, faculty summary, academic calendar, holidays, notices)
    # so the model always has access to these even if retrieval does not return them.
    global_context_parts = []
    
    # Add notice context FIRST (highest priority)
    try:
        notice_context = get_notice_context()
        if notice_context:
            global_context_parts.append(notice_context)
    except Exception as e:
        print(f"[ERROR] Could not add notice context: {e}")
    
    # Short authoritative override for common hostel FAQ (ensures model gives correct, concise answer)
    try:
        hostel_quick_facts = (
            "Hostel Quick Facts:\n"
            "- Room cleaning/service: The hostel provides routine room cleaning service every day; only the designated subday is off.\n"
            "- Students are not required to perform routine room cleaning themselves; use hostel service for regular cleaning.\n"
            "- For exceptions or special requests, follow the hostel rule-book procedures."
        )
        global_context_parts.append(hostel_quick_facts)
    except Exception:
        pass
    try:
        if hostel_rules_text:
            global_context_parts.append("Hostel Rules:\n" + (hostel_rules_text[:4000] + "\n...[truncated]" if len(hostel_rules_text) > 4000 else hostel_rules_text))
    except Exception:
        pass
    try:
        if faculty_text:
            global_context_parts.append("Faculty Summary:\n" + (faculty_text[:1500] + "\n...[truncated]" if len(faculty_text) > 1500 else faculty_text))
    except Exception:
        pass
    try:
        if academic_text:
            global_context_parts.append("Academic Calendar:\n" + (academic_text[:1000] + "\n...[truncated]" if len(academic_text) > 1000 else academic_text))
    except Exception:
        pass
    try:
        if holiday_text:
            global_context_parts.append("Holidays:\n" + (holiday_text[:1000] + "\n...[truncated]" if len(holiday_text) > 1000 else holiday_text))
    except Exception:
        pass

    global_context = "\n\n".join(global_context_parts)

    # Inject user profile into global context if available
    try:
        user_profile = USER_PROFILES.get(session_id)
        if user_profile:
            profile_text = "User Profile:\n"
            for k, v in user_profile.items():
                profile_text += f"- {k}: {v}\n"
            global_context = profile_text + "\n" + global_context
    except Exception:
        pass

    system_instruction = """You are a campus assistant for Brainware University, Department of Computer Science & Engineering (AI).

CRITICAL INSTRUCTIONS:
1. Answer STRICTLY using information from the provided project files and the global context sections below.
2. DO NOT use your general knowledge or training data.
3. For greetings (hi, hello, hey), respond warmly and offer to help with university information.
4. If the answer is not in the provided context, respond with EXACTLY: "I don't have this information in the knowledge base. Let me provide you with relevant contact details."
5. Keep answers concise and relevant to the user's question.
6. Remember previous messages in this conversation.
7. When citing sources, prefer the file paths listed in the available knowledge base (but do not invent file paths).
8. If user asks in hinglish, respond in hinglish.

SPECIAL INSTRUCTIONS FOR NOTICES:
- You have access to current notices in the NOTICES section of GLOBAL CONTEXT.
- When asked about new notices or announcements, check the NOTICES section and answer YES or NO based on what's available.
- When asked about specific notices or details, briefly mention if they exist and ALWAYS direct users to: "Academic → Notice" section in the chatbot interface for full details and PDFs.
- Do NOT provide the full content of PDF notices - just confirm their existence and tell users where to find them.
- For announcement-type notices, you can provide a brief summary but still direct them to the Notice panel for complete information.

SPECIAL INSTRUCTIONS FOR UNIVERSITY RULES:
- You have comprehensive access to ALL university rules and policies in the UNIVERSITY RULES section below.
- When asked about rules, policies, what's allowed/prohibited, or any conduct questions, refer to the UNIVERSITY RULES section.
- Provide specific rule information including penalties, fines, and consequences when applicable.
- If asked for a summary of rules in a category, provide a clear overview from the available rules.
- Answer directly without mentioning rule categories, sections, or source references in your response.
- For disciplinary matters, mention both the violation and the consequences clearly.

SPECIAL INSTRUCTIONS FOR SCHOLARSHIPS:
- You have access to COMPREHENSIVE scholarship data from Scholarship/data/detailed scholarship folder.
- NEVER copy-paste scholarship details verbatim - this is CRITICAL.
- READ and UNDERSTAND the scholarship data, then PERSONALIZE your response.
- When user asks about scholarships:
  * Identify which scholarship(s) are relevant to their query
  * Check if they mentioned their profile (year, course, income, community, category)
  * Provide PERSONALIZED eligibility assessment based on their profile
  * Explain benefits in context of what they asked
  * Give specific next steps tailored to their situation
- Use conversational, helpful language - NOT data dumps.
- If user asks "Am I eligible?", check their profile against criteria and give a clear YES/NO with reasons.
- If profile info is missing, ask specific questions to help assess eligibility.
- Focus on what matters to THEIR specific query, not everything about the scholarship.

GLOBAL CONTEXT (always available):
{}

UNIVERSITY RULES (comprehensive policy database):
{}

AVAILABLE KNOWLEDGE BASE (relevant documents returned by retrieval):
{}

CONVERSATION HISTORY:
{}

USER QUESTION: {}

Answer based ONLY on the provided knowledge base, university rules, and the global context above.""".format(
        global_context,
        university_rules_context,
        json_context,
        history_text,
        user_query_clean
    )

    bot_answer = ""
    
    if not api_url or not api_key:
        # Fallback: Use retrieved context directly if API not configured
        retrieved_docs = retrieve_top_k(user_query_clean, k=3)
        
        if not retrieved_docs:
            bot_answer = "I don't have this information in the knowledge base."
            # Add helpline contact
            helpline_info = find_relevant_helpline(user_query_clean)
            bot_answer += helpline_info
        else:
            # Build answer from retrieved context - clean and direct
            for doc in retrieved_docs[:1]:  # Use top result
                content = doc['full_content']
                path = doc['path']

                # Scholarship-specific formatting and basic personalization
                is_scholarship = False
                if isinstance(content, dict):
                    keys_low = set(k.lower() for k in content.keys())
                    if 'scholarship_name' in keys_low or 'official_name' in keys_low or 'scholarship_id' in keys_low or 'scholarship_benefits' in keys_low:
                        is_scholarship = True

                if is_scholarship and isinstance(content, dict):
                    # Use the clean formatting function
                    bot_answer += format_scholarship_for_user(content)
                    
                    # Add personalized guidance if user is asking about themselves
                    user_l = user_query_clean.lower()
                    if any(w in user_l for w in ['i ', ' my ', "i'm", "i'm", 'me ', 'myself', 'am ', 'eligible']):
                        bot_answer += "\n" + "="*60 + "\n"
                        bot_answer += "📌 Personalized Guidance:\n\n"
                        
                        if 'minority' in user_l or 'sc' in user_l or 'st' in user_l or 'obc' in user_l:
                            bot_answer += "• Since you mentioned your community, make sure to prepare:\n"
                            bot_answer += "  - Community/Caste certificate\n"
                            bot_answer += "  - Income certificate from competent authority\n\n"
                        
                        if 'income' in user_l or 'family income' in user_l:
                            inc = content.get('income_limit')
                            if inc:
                                if isinstance(inc, dict):
                                    annual = inc.get('annual_family_income') or inc.get('maximum_family_income')
                                    if annual:
                                        bot_answer += f"• Family income limit: {annual}\n"
                                else:
                                    bot_answer += f"• Family income limit: {inc}\n"
                            bot_answer += "• You'll need an income certificate from BDO/SDO\n\n"
                        
                        if 'first' in user_l or '1st' in user_l or 'year' in user_l:
                            bot_answer += "• Keep your academic documents ready (mark sheets, certificates)\n"
                            bot_answer += "• Ensure you have a bank account in your name\n\n"
                        
                        if 'eligible' in user_l:
                            bot_answer += "• To confirm your eligibility, please share:\n"
                            bot_answer += "  - Your current year/semester\n"
                            bot_answer += "  - Family annual income\n"
                            bot_answer += "  - Category (if applicable)\n"
                            bot_answer += "  - Your marks/percentage\n"

                elif isinstance(content, dict):
                    # Generic dict handling (non-scholarship) - handle ALL types of data
                    
                    # Faculty data
                    if 'name' in content and 'designation' in content:
                        bot_answer += f"**{content.get('name')}**\n"
                        bot_answer += f"Designation: {content.get('designation')}\n"
                        if 'email' in content:
                            bot_answer += f"Email: {content.get('email')}\n"
                        if 'phone' in content:
                            bot_answer += f"Phone: {content.get('phone')}\n"
                        if 'specialization' in content:
                            bot_answer += f"Specialization: {content.get('specialization')}\n"
                        if 'qualification' in content:
                            bot_answer += f"Qualification: {content.get('qualification')}\n"
                        bot_answer += "\n"
                    
                    # Exam data
                    elif 'exam_name' in content or 'exam_date' in content:
                        if 'exam_name' in content:
                            bot_answer += f"**{content.get('exam_name')}**\n"
                        if 'exam_date' in content:
                            bot_answer += f"Date: {content.get('exam_date')}\n"
                        if 'time' in content:
                            bot_answer += f"Time: {content.get('time')}\n"
                        if 'duration' in content:
                            bot_answer += f"Duration: {content.get('duration')}\n"
                        if 'subjects' in content:
                            bot_answer += f"Subjects: {', '.join(content.get('subjects', []))}\n"
                        bot_answer += "\n"
                    
                    # Holiday data
                    elif 'holiday_name' in content or 'date' in content:
                        if 'holiday_name' in content:
                            bot_answer += f"**{content.get('holiday_name')}**\n"
                        if 'date' in content:
                            bot_answer += f"Date: {content.get('date')}\n"
                        if 'day' in content:
                            bot_answer += f"Day: {content.get('day')}\n"
                        bot_answer += "\n"
                    
                    # Course/Subject data
                    elif 'course_name' in content or 'subject_name' in content:
                        course_name = content.get('course_name') or content.get('subject_name', 'Unknown Course')
                        course_code = content.get('course_code') or content.get('subject_code', '')
                        
                        if course_code and course_name:
                            bot_answer += f"**{course_code}: {course_name}**\n\n"
                        
                        if 'summary' in content:
                            bot_answer += f"{content['summary']}\n\n"
                        
                        if 'modules' in content:
                            modules = content['modules']
                            bot_answer += f"**Modules ({len(modules)}):**\n"
                            for mod in modules:
                                mod_num = mod.get('module_no') or mod.get('module_number', '?')
                                bot_answer += f"{mod_num}. {mod.get('title', 'N/A')}\n"
                            bot_answer += "\n"
                        
                        if 'course_outcomes' in content and content['course_outcomes']:
                            outcomes = content['course_outcomes']
                            bot_answer += f"**Course Outcomes ({len(outcomes)}):**\n"
                            for i, outcome in enumerate(outcomes[:3], 1):
                                bot_answer += f"{i}. {outcome}\n"
                            if len(outcomes) > 3:
                                bot_answer += f"... and {len(outcomes) - 3} more\n"
                            bot_answer += "\n"
                        
                        if 'prerequisites' in content and content['prerequisites']:
                            prereqs = content['prerequisites']
                            bot_answer += f"**Prerequisites ({len(prereqs)}):**\n"
                            for i, prereq in enumerate(prereqs[:3], 1):
                                bot_answer += f"{i}. {prereq}\n"
                            if len(prereqs) > 3:
                                bot_answer += f"... and {len(prereqs) - 3} more\n"
                            bot_answer += "\n"
                    
                    # Generic fallback for any other dict data (hostel rules, library info, etc.)
                    else:
                        # Display all key-value pairs in a readable format
                        for key, value in content.items():
                            if isinstance(value, (str, int, float)):
                                # Simple values
                                formatted_key = key.replace('_', ' ').title()
                                bot_answer += f"**{formatted_key}:** {value}\n"
                            elif isinstance(value, list):
                                # Lists
                                formatted_key = key.replace('_', ' ').title()
                                bot_answer += f"\n**{formatted_key}:**\n"
                                for item in value[:10]:  # Limit to 10 items
                                    if isinstance(item, dict):
                                        # If list contains dicts, show them nicely
                                        for k, v in item.items():
                                            bot_answer += f"  • {k.replace('_', ' ').title()}: {v}\n"
                                    else:
                                        bot_answer += f"  • {item}\n"
                                if len(value) > 10:
                                    bot_answer += f"  ... and {len(value) - 10} more\n"
                                bot_answer += "\n"
                            elif isinstance(value, dict):
                                # Nested dicts
                                formatted_key = key.replace('_', ' ').title()
                                bot_answer += f"\n**{formatted_key}:**\n"
                                for k, v in value.items():
                                    bot_answer += f"  • {k.replace('_', ' ').title()}: {v}\n"
                                bot_answer += "\n"
                
                elif isinstance(content, list):
                    # Content is a list (e.g., list of rules, events, etc.)
                    for i, item in enumerate(content[:15], 1):  # Show first 15 items
                        if isinstance(item, dict):
                            # List of dicts
                            for key, value in item.items():
                                formatted_key = key.replace('_', ' ').title()
                                bot_answer += f"**{formatted_key}:** {value}\n"
                            bot_answer += "\n"
                        else:
                            # List of strings/simple values
                            bot_answer += f"{i}. {item}\n"
                    
                    if len(content) > 15:
                        bot_answer += f"\n... and {len(content) - 15} more items\n"
                
                elif isinstance(content, str):
                    # Content is plain text (e.g., hostel rules text file)
                    # Show first 1000 characters to avoid overwhelming the user
                    if len(content) > 1000:
                        bot_answer += content[:1000] + "\n\n... [Content truncated. Ask specific questions for more details]\n"
                    else:
                        bot_answer += content + "\n"
                
                else:
                    # Unknown content type - show as is
                    bot_answer += str(content)
        
        bot_answer = sanitize_text(bot_answer)
        
        # Add assistant response to history
        CHAT_HISTORY[session_id].append({'role': 'assistant', 'content': bot_answer})
        
        # Log to admin panel database
        log_student_query(user_query_clean, bot_answer, session_id)
        
        resp = make_response(jsonify({"response": bot_answer, "sources": [d['path'] for d in retrieved_docs]}))
        resp.set_cookie('chat_session_id', session_id, max_age=86400, httponly=True)
        return resp

    # Prepare Gemini request
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_instruction}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Extract answer from Gemini response
        answer = ""
        candidates = result.get('candidates', [])
        if candidates and 'content' in candidates[0] and 'parts' in candidates[0]['content']:
            answer = candidates[0]['content']['parts'][0].get('text', '')

        if not answer:
            # Fallback if no answer
            answer = "I couldn't generate a response. Please try rephrasing your question."

        # Sanitize output
        bot_answer = sanitize_text(answer)

        # --- ENFORCE STRICT KB MATCH ---
        # If the answer does not contain any content from the loaded knowledge base, override with contact info
        kb_match = False
        for doc in LOADED_DOCS.values():
            if isinstance(doc, list):
                for item in doc:
                    if isinstance(item, dict):
                        for v in item.values():
                            if isinstance(v, str) and v.strip() and v.lower() in bot_answer.lower():
                                kb_match = True
                                break
                    elif isinstance(item, str) and item.strip() and item.lower() in bot_answer.lower():
                        kb_match = True
                        break
            elif isinstance(doc, dict):
                for v in doc.values():
                    if isinstance(v, str) and v.strip() and v.lower() in bot_answer.lower():
                        kb_match = True
                        break
            elif isinstance(doc, str) and doc.strip() and doc.lower() in bot_answer.lower():
                kb_match = True
                break
            if kb_match:
                break

        if ("don't have this information" in bot_answer.lower() or "i don't know" in bot_answer.lower() or not kb_match):
            # Always override with your contact info message
            bot_answer = "I don't have this information in the knowledge base. Let me provide you with relevant contact details." + find_relevant_helpline(user_query_clean)

        # Add assistant response to history
        CHAT_HISTORY[session_id].append({'role': 'assistant', 'content': bot_answer})

        # Log to admin panel database
        log_student_query(user_query_clean, bot_answer, session_id)

        # Return response with session cookie
        resp = make_response(jsonify({
            "response": bot_answer,
            "sources": [d['path'] for d in retrieve_top_k(user_query_clean, k=3)]
        }))
        resp.set_cookie('chat_session_id', session_id, max_age=86400, httponly=True)
        return resp

    except Exception as e:
        # Attempt graceful fallback: build answer from retrieved docs if possible
        try:
            retrieved_docs = retrieve_top_k(user_query_clean, k=6)
            bot_answer = None
            if retrieved_docs:
                # Try to find a scholarship doc and summarize it; if summarization fails, try the next
                scholarship_candidates = [d for d in retrieved_docs if 'scholarship' in d['path'].lower()]
                tried = []
                for cand in (scholarship_candidates + retrieved_docs):
                    if cand['path'] in tried:
                        continue
                    tried.append(cand['path'])
                    try:
                        content = cand['full_content']
                        path = cand['path']
                        if isinstance(content, dict) and any(k in (k_.lower() for k_ in content.keys()) for k in ['scholarship_name','official_name','scholarship_id','scholarship_benefits']):
                            # Use clean formatting
                            bot_answer = format_scholarship_for_user(content)
                            break
                        elif isinstance(content, dict):
                            # Generic dict fallback - handle ALL data types
                            parts = []
                            
                            # Faculty
                            if 'name' in content and 'designation' in content:
                                parts.append(f"**{content.get('name')}**\n")
                                parts.append(f"Designation: {content.get('designation')}\n")
                                if 'email' in content:
                                    parts.append(f"Email: {content.get('email')}\n")
                                if 'specialization' in content:
                                    parts.append(f"Specialization: {content.get('specialization')}\n")
                            
                            # Exam
                            elif 'exam_name' in content:
                                parts.append(f"**{content.get('exam_name')}**\n")
                                if 'exam_date' in content:
                                    parts.append(f"Date: {content.get('exam_date')}\n")
                                if 'time' in content:
                                    parts.append(f"Time: {content.get('time')}\n")
                            
                            # Holiday
                            elif 'holiday_name' in content:
                                parts.append(f"**{content.get('holiday_name')}**\n")
                                if 'date' in content:
                                    parts.append(f"Date: {content.get('date')}\n")
                            
                            # Course/Subject
                            else:
                                cn = content.get('course_name') or content.get('subject_name')
                                cc = content.get('course_code') or content.get('subject_code','')
                                if cn:
                                    parts.append(f"**{cc + ': ' if cc else ''}{cn}**\n\n")
                                if 'summary' in content:
                                    parts.append(f"{content['summary']}\n\n")
                            
                            if parts:
                                bot_answer = ''.join(parts)
                                break
                        elif isinstance(content, str):
                            # Plain text content
                            bot_answer = content[:1000]
                            if len(content) > 1000:
                                bot_answer += "\n\n[Text truncated. Ask for specific details.]"
                            break
                        elif isinstance(content, list):
                            # List content
                            parts = [f"Found {len(content)} items:\n\n"]
                            for idx, item in enumerate(content[:5], 1):
                                if isinstance(item, dict):
                                    item_str = ', '.join(f"{k}: {v}" for k, v in list(item.items())[:3] if isinstance(v, (str, int, float)))
                                    parts.append(f"{idx}. {item_str}\n")
                                else:
                                    parts.append(f"{idx}. {str(item)[:150]}\n")
                            if len(content) > 5:
                                parts.append(f"\n... and {len(content) - 5} more items")
                            bot_answer = ''.join(parts)
                            break
                    except Exception:
                        # try next candidate
                        continue

            if not bot_answer:
                bot_answer = "I encountered an error while processing your request. Let me provide you with relevant contact details."
                bot_answer = sanitize_text(bot_answer)
                bot_answer += find_relevant_helpline(user_query_clean)
        except Exception:
            bot_answer = "I encountered an error while processing your request. Let me provide you with relevant contact details."
            bot_answer = sanitize_text(bot_answer)
            bot_answer += find_relevant_helpline(user_query_clean)

        CHAT_HISTORY[session_id].append({'role': 'assistant', 'content': bot_answer})
        log_student_query(user_query_clean, bot_answer, session_id)

        resp = make_response(jsonify({
            "response": bot_answer,
            "error": str(e),
            "sources": [d['path'] for d in retrieved_docs] if 'retrieved_docs' in locals() else []
        }))
        resp.set_cookie('chat_session_id', session_id, max_age=86400, httponly=True)
        return resp

def log_student_query(question, answer, student_id=None):
    """Log student query to admin panel database"""
    try:
        conn = get_admin_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO student_queries (student_identifier, question_text, bot_answer, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id or 'anonymous', question, answer, 'new', datetime.utcnow().isoformat()))
        
        conn.commit()
        conn.close()
        print(f"[INFO] Query logged to admin panel database")
    except Exception as e:
        print(f"[ERROR] Failed to log query to admin panel: {e}")
        traceback.print_exc()

# Route to serve logo files
@app.route('/logo/<path:filename>')
def serve_logo(filename):
    return send_from_directory('logo', filename)

# Route to get active announcements for students
@app.route('/api/announcements/active')
def get_active_announcements():
    """Get active announcements from admin panel for students"""
    try:
        conn = get_admin_db()
        cursor = conn.cursor()
        
        # Get active announcements that are visible to chatbot
        cursor.execute('''
            SELECT id, title, body, attachments, published_at, created_at
            FROM announcements
            WHERE is_active = 1 
            AND visible_to_chatbot = 1
            AND published_at IS NOT NULL
            AND published_at <= datetime('now')
            ORDER BY published_at DESC
            LIMIT 10
        ''')
        
        announcements = []
        for row in cursor.fetchall():
            announcements.append({
                'id': row[0],
                'title': row[1],
                'body': row[2],
                'attachments': json.loads(row[3]) if row[3] else [],
                'published_at': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return jsonify({'success': True, 'data': announcements})
    except Exception as e:
        print(f"[ERROR] Failed to fetch announcements: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e), 'data': []})

# Route to get real-time statistics for admin panel
@app.route('/api/admin/stats')
def get_admin_stats():
    """Get real-time statistics from the chatbot usage"""
    try:
        conn = get_admin_db()
        cursor = conn.cursor()
        
        # Total queries today
        cursor.execute('''
            SELECT COUNT(*) FROM student_queries 
            WHERE DATE(created_at) = DATE('now')
        ''')
        queries_today = cursor.fetchone()[0]
        
        # Total queries this week
        cursor.execute('''
            SELECT COUNT(*) FROM student_queries 
            WHERE created_at >= datetime('now', '-7 days')
        ''')
        queries_week = cursor.fetchone()[0]
        
        # Total queries all time
        cursor.execute('SELECT COUNT(*) FROM student_queries')
        total_queries = cursor.fetchone()[0]
        
        # Pending queries
        cursor.execute('''
            SELECT COUNT(*) FROM student_queries 
            WHERE status IN ('new', 'in_progress')
        ''')
        pending_queries = cursor.fetchone()[0]
        
        # Total FAQs
        cursor.execute('SELECT COUNT(*) FROM faqs')
        total_faqs = cursor.fetchone()[0]
        
        # Total announcements
        cursor.execute('SELECT COUNT(*) FROM announcements WHERE is_active = 1')
        total_announcements = cursor.fetchone()[0]
        
        # Chatbot accuracy (based on feedback)
        cursor.execute('''
            SELECT COUNT(*) FROM feedback WHERE helpful_bool IS NOT NULL
        ''')
        total_feedback = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM feedback WHERE helpful_bool = 1
        ''')
        helpful_feedback = cursor.fetchone()[0]
        
        accuracy = round((helpful_feedback / total_feedback * 100), 2) if total_feedback > 0 else 0
        
        # Recent queries (last 10)
        cursor.execute('''
            SELECT id, student_identifier, question_text, status, created_at
            FROM student_queries
            ORDER BY created_at DESC
            LIMIT 10
        ''')
        recent_queries = []
        for row in cursor.fetchall():
            recent_queries.append({
                'id': row[0],
                'student_id': row[1],
                'question': row[2][:100] + '...' if len(row[2]) > 100 else row[2],
                'status': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'queries_today': queries_today,
                'queries_week': queries_week,
                'total_queries': total_queries,
                'pending_queries': pending_queries,
                'total_faqs': total_faqs,
                'total_announcements': total_announcements,
                'chatbot_accuracy': accuracy,
                'recent_queries': recent_queries
            }
        })
    except Exception as e:
        print(f"[ERROR] Failed to fetch admin stats: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e), 'data': None})

# Route to get all university rules
@app.route('/api/university-rules')
def get_university_rules():
    """Get all university rules organized by category"""
    try:
        if not UNIVERSITY_RULES:
            return jsonify({'success': False, 'error': 'No university rules loaded', 'data': {}})
        
        # Organize rules with statistics
        rules_summary = {}
        total_rules = 0
        
        for category, rules_list in UNIVERSITY_RULES.items():
            rules_summary[category] = {
                'count': len(rules_list),
                'rules': rules_list
            }
            total_rules += len(rules_list)
        
        return jsonify({
            'success': True,
            'data': {
                'total_categories': len(UNIVERSITY_RULES),
                'total_rules': total_rules,
                'categories': rules_summary
            }
        })
    except Exception as e:
        print(f"[ERROR] Failed to fetch university rules: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e), 'data': {}})

# Route to search university rules
@app.route('/api/university-rules/search', methods=['POST'])
def search_university_rules():
    """Search university rules by keyword"""
    try:
        data = request.get_json(force=True)
        query = data.get('query', '').strip().lower()
        
        if not query:
            return jsonify({'success': False, 'error': 'No search query provided', 'data': []})
        
        if not UNIVERSITY_RULES:
            return jsonify({'success': False, 'error': 'No university rules loaded', 'data': []})
        
        # Search across all rules
        matching_rules = []
        
        for category, rules_list in UNIVERSITY_RULES.items():
            for rule in rules_list:
                rule_text = f"{rule.get('title', '')} {rule.get('text', '')} {rule.get('section', '')}".lower()
                
                # Check if query appears in rule
                if query in rule_text:
                    matching_rules.append({
                        'category': category,
                        'id': rule.get('id', ''),
                        'section': rule.get('section', 'General'),
                        'title': rule.get('title', 'N/A'),
                        'text': rule.get('text', 'N/A'),
                        'source': rule.get('source', 'N/A'),
                        'page': rule.get('page', 'N/A')
                    })
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'count': len(matching_rules),
                'rules': matching_rules
            }
        })
    except Exception as e:
        print(f"[ERROR] Failed to search university rules: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e), 'data': []})

# Notice routes
@app.route('/api/notices')
def get_notices():
    """Get all notices from PDF files and admin announcements"""
    try:
        notices = []
        
        # 1. Get PDF-based notices
        notices_dir = os.path.join(os.path.dirname(__file__), 'notice', 'pdfs')
        
        # Create directory if it doesn't exist
        if not os.path.exists(notices_dir):
            os.makedirs(notices_dir)
        
        # Read all PDF files
        if os.path.exists(notices_dir):
            for filename in os.listdir(notices_dir):
                if filename.endswith('.pdf'):
                    # Parse filename format: "Category--Title--YYYY-MM-DD.pdf"
                    parts = filename[:-4].split('--')
                    
                    if len(parts) >= 3:
                        category = parts[0].strip()
                        title = parts[1].strip()
                        date = parts[2].strip()
                        
                        notices.append({
                            'category': category,
                            'title': title,
                            'date': date,
                            'filename': filename,
                            'type': 'pdf'
                        })
                    else:
                        # Fallback for files that don't match the pattern
                        notices.append({
                            'category': 'General',
                            'title': filename[:-4],
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'filename': filename,
                            'type': 'pdf'
                        })
        
        # 2. Get announcements from admin panel
        try:
            conn = get_admin_db()
            cursor = conn.cursor()
            
            # Get active announcements that are visible to chatbot
            cursor.execute('''
                SELECT id, title, body, attachments, published_at, created_at
                FROM announcements
                WHERE is_active = 1 
                AND visible_to_chatbot = 1
                AND published_at IS NOT NULL
                AND published_at <= datetime('now')
                ORDER BY published_at DESC
            ''')
            
            for row in cursor.fetchall():
                # Extract date from published_at (format: YYYY-MM-DD HH:MM:SS)
                published_date = row[4].split(' ')[0] if row[4] else datetime.now().strftime('%Y-%m-%d')
                
                # Parse attachments
                attachments = json.loads(row[3]) if row[3] else []
                
                notices.append({
                    'category': 'Announcement',
                    'title': row[1],
                    'date': published_date,
                    'body': row[2],
                    'attachments': attachments,
                    'announcement_id': row[0],
                    'type': 'announcement'
                })
            
            conn.close()
        except Exception as e:
            print(f"[WARNING] Could not fetch admin announcements: {e}")
            # Continue even if admin announcements fail
        
        # Sort by date (newest first)
        notices.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify(notices)
    except Exception as e:
        print(f"[ERROR] Failed to fetch notices: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)})

@app.route('/pdfs/<path:filename>')
def serve_notice_pdf(filename):
    """Serve PDF files from notice/pdfs/ directory"""
    try:
        notices_dir = os.path.join(os.path.dirname(__file__), 'notice', 'pdfs')
        return send_from_directory(notices_dir, filename)
    except Exception as e:
        print(f"[ERROR] Failed to serve PDF: {e}")
        abort(404)

# Route to serve announcement attachments from admin panel
@app.route('/uploads/<path:filepath>')
def serve_uploads(filepath):
    """Serve uploaded files from admin panel uploads directory"""
    try:
        uploads_dir = os.path.join(os.path.dirname(__file__), 'Admin Panel', 'uploads')
        return send_from_directory(uploads_dir, filepath)
    except Exception as e:
        print(f"[ERROR] Failed to serve upload file: {e}")
        abort(404)

# Route to serve sidebar icons
@app.route('/sidebar/<path:filename>')
def serve_sidebar(filename):
    return send_from_directory('sidebar', filename)

# Route to serve exam files
@app.route('/exam/<path:filename>')
def serve_exam(filename):
    return send_from_directory('Exam', filename)

# Route to serve faculty photos
@app.route('/Faculty/Photos/<path:filename>')
def serve_faculty_photo(filename):
    return send_from_directory(os.path.join('Faculty', 'Photos'), filename)

# Route to serve faculty data
@app.route('/faculty-data')
def get_faculty_data():
    try:
        faculty_path = os.path.join(os.path.dirname(__file__), 'Faculty', 'brainware_cse_ai_faculty.json')
        with open(faculty_path, 'r', encoding='utf-8') as f:
            faculty_data = json.load(f)
        
        # Convert the faculty object to an array format expected by frontend
        faculty_list = []
        if 'faculty' in faculty_data and isinstance(faculty_data['faculty'], dict):
            department = faculty_data.get('department', 'Unknown Department')
            for faculty_id, faculty_info in faculty_data['faculty'].items():
                faculty_member = {
                    'id': faculty_id,
                    'name': faculty_info.get('name', 'Unknown'),
                    'position': faculty_info.get('position', 'Unknown'),
                    'qualification': faculty_info.get('qualification', 'Unknown'),
                    'department': department,
                    'research': ', '.join(faculty_info.get('research_area', [])) if faculty_info.get('research_area') else None,
                    'photo': faculty_info.get('photo', 'logo/Brainware_University.jpg')
                }
                faculty_list.append(faculty_member)
        
        return jsonify(faculty_list)
    except FileNotFoundError as fnf:
        return jsonify({"error": f"Faculty file not found: {str(fnf)}"}), 404
    except json.JSONDecodeError as jde:
        return jsonify({"error": f"Invalid JSON in faculty file: {str(jde)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error loading faculty data: {str(e)}"}), 500

# Route to serve exam data
@app.route('/exam-data')
def get_exam_data():
    try:
        with open('Exam/exam.json', 'r', encoding='utf-8') as f:
            exam_data = json.load(f)
        return jsonify(exam_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/knowledge-files')
def knowledge_files():
    """Return a listing of all loaded JSON/JSONL files and simple stats."""
    try:
        files = []
        for rel, content in LOADED_DOCS.items():
            entry = {'path': rel}
            if isinstance(content, dict):
                entry['type'] = 'json'
                entry['top_keys'] = list(content.keys())[:10]
            elif isinstance(content, list):
                entry['type'] = 'jsonl_or_array'
                entry['items'] = len(content)
            else:
                entry['type'] = str(type(content))
            files.append(entry)
        return jsonify({'count': len(files), 'files': files, 'prompt_file': PROMPT_FILE_PATH})
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/query-knowledge', methods=['POST'])
def query_knowledge():
    """Simple keyword search over loaded JSON files. Returns best matches with short snippets."""
    try:
        data = request.get_json(force=True)
        q = (data.get('q') or '').strip().lower()
        max_results = int(data.get('max_results', 6))
        if not q:
            return jsonify({'error': 'No query provided.'}), 400

        scores = []
        for rel, content in LOADED_DOCS.items():
            try:
                text = ''
                if isinstance(content, dict) or isinstance(content, list):
                    text = json.dumps(content)
                else:
                    text = str(content)
                idx = text.lower().count(q)
                if idx > 0:
                    # produce a snippet
                    pos = text.lower().find(q)
                    start = max(0, pos - 120)
                    snippet = text[start:start+300].replace('\n', ' ')
                    scores.append({'path': rel, 'score': idx, 'snippet': snippet})
            except Exception:
                continue

        # sort by score desc
        scores.sort(key=lambda x: x['score'], reverse=True)
        return jsonify({'query': q, 'results': scores[:max_results]})
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/clear-history', methods=['POST'])
def clear_history():
    """Clear chat history for current session."""
    session_id = request.cookies.get('chat_session_id')
    if session_id and session_id in CHAT_HISTORY:
        CHAT_HISTORY[session_id] = []
        return jsonify({'message': 'Chat history cleared successfully.'})
    return jsonify({'message': 'No active session found.'})

# Serve static files (holiday JSON, pdf, etc.)
@app.route('/holiday/<path:filename>')
def serve_holiday_file(filename):
    try:
        return send_from_directory(STATIC_DIR, filename, as_attachment=False)
    except FileNotFoundError:
        return jsonify({"error": "File not found", "filename": filename}), 404
    except Exception as e:
        return jsonify({"error": "Server error", "detail": str(e)}), 500

# Holiday Data API
@app.route('/holiday-data')
def holiday_data():
    json_path = os.path.join(STATIC_DIR, 'holiday.json')
    if not os.path.exists(json_path):
        return jsonify({"error": "holiday.json not found on server"}), 404
    try:
        with open(json_path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            # data should be an array; otherwise try to find a top-level key
            if isinstance(data, dict):
               
                if 'holiday_list_2025' in data and isinstance(data['holiday_list_2025'], list):
                    return jsonify(data['holiday_list_2025'])
                # If top-level has one array value, return it
                for v in data.values():
                    if isinstance(v, list):
                        return jsonify(v)
                return jsonify({"error": "Invalid JSON shape. Expected array."}), 500
            return jsonify(data)
    except json.JSONDecodeError as jde:
        return jsonify({"error": "JSON decode error", "detail": str(jde)}), 500
    except Exception as e:
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500

def find_best_match(user_input):
    user_input = (user_input or "").lower().strip()
    if not user_input:
        return "default"
    keys = list(knowledge.keys())
    lowermap = {k.lower(): k for k in keys}
    matches = difflib.get_close_matches(user_input, list(lowermap.keys()), n=1, cutoff=0.5)
    if matches:
        return lowermap[matches[0]]
    return "default"


@app.route('/semesters')
def get_semesters():
    """Return list of available semesters"""
    try:
        sem_dir = os.path.join(os.path.dirname(__file__), 'sem_json')
        semesters = []
        for i in range(1, 6):  # sem_1 to sem_5
            sem_file = os.path.join(sem_dir, f'sem_{i}.json')
            if os.path.exists(sem_file):
                with open(sem_file, 'r', encoding='utf-8') as f:
                    sem_data = json.load(f)
                    semesters.append({
                        'id': i,
                        'name': sem_data.get('semester', f'Semester {i}'),
                        'subject_count': len(sem_data.get('subjects', []))
                    })
        return jsonify(semesters)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/semester/<int:sem_id>/subjects')
def get_semester_subjects(sem_id):
    """Return subjects for a specific semester"""
    try:
        sem_file = os.path.join(os.path.dirname(__file__), 'sem_json', f'sem_{sem_id}.json')
        if not os.path.exists(sem_file):
            return jsonify({'error': 'Semester not found'}), 404
        
        with open(sem_file, 'r', encoding='utf-8') as f:
            sem_data = json.load(f)
        
        return jsonify(sem_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/course-explanation/<course_code>')
def get_course_explanation(course_code):
    """Return detailed explanation for a specific course"""
    try:
        # Determine which semester folder based on course code pattern
        sem_map = {
            'HSMCM101': 'sem_01', 'BSCM101': 'sem_01', 'BSCM102': 'sem_01', 'ESCM101': 'sem_01', 'BSCM191': 'sem_01', 'ESCM191': 'sem_01', 'ESCM192': 'sem_01', 'AUM-1': 'sem_01',
            'BSCM201': 'sem_02', 'BSCM202': 'sem_02', 'BSCM203': 'sem_02', 'ESCM201': 'sem_02', 'BSCM291': 'sem_02', 'ESCM291': 'sem_02', 'ESCM292': 'sem_02', 'AUM-2': 'sem_02',
            'BSCM301': 'sem_03', 'ESCM301': 'sem_03', 'ESCM302': 'sem_03', 'ESCM303': 'sem_03', 'PCC-CSM301': 'sem_03', 'ESCM392': 'sem_03', 'ESCM393': 'sem_03', 'PCC-CSM391': 'sem_03', 'AUM': 'sem_03',
            'HSMCM401': 'sem_04', 'PCC-CSM401': 'sem_04', 'PCC-CSM402': 'sem_04', 'PCC-CSM403': 'sem_04', 'PCC-CSM404': 'sem_04', 'PCC-CSM405': 'sem_04', 'PCC-CSM491': 'sem_04', 'PCC-CSM492': 'sem_04', 'PCC-CSM493': 'sem_04',
            'PCC-CSM501': 'sem_05', 'PCC-CSM502': 'sem_05', 'PCC-CSM503': 'sem_05', 'PCC-CSM504': 'sem_05', 'PEC-CSM501': 'sem_05', 'PCC-CSM591': 'sem_05', 'PCC-CSM592': 'sem_05', 'PCC-CSM593': 'sem_05', 'PEC-CSM591': 'sem_05'
        }
        
        sem_folder = sem_map.get(course_code)
        if not sem_folder:
            return jsonify({'error': 'Course not found'}), 404
        
        explain_file = os.path.join(os.path.dirname(__file__), 'sem_explain', sem_folder, f'{course_code}.json')
        
        if not os.path.exists(explain_file):
            return jsonify({'error': 'Explanation file not found'}), 404
        
        with open(explain_file, 'r', encoding='utf-8') as f:
            explain_data = json.load(f)
        
        return jsonify(explain_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/module-explanation/<course_code>/<int:module_number>')
def get_module_explanation(course_code, module_number):
    """Return detailed explanation for a specific module"""
    try:
        # Determine which semester folder based on course code pattern
        sem_folders = {
            'HSMCM1': 'sem_01', 'BSCM1': 'sem_01', 'ESCM1': 'sem_01', 'AUM-1': 'sem_01',
            'HSMCM2': 'sem_02', 'BSCM2': 'sem_02', 'ESCM2': 'sem_02', 'AUM-2': 'sem_02',
            'HSMCM3': 'sem_03', 'BSCM3': 'sem_03', 'ESCM3': 'sem_03', 'PCC-CSM3': 'sem_03', 'AUM-3': 'sem_03',
            'HSMCM4': 'sem_04', 'PCC-CSM4': 'sem_04',
            'PCC-CSM5': 'sem_05', 'PEC-CSM5': 'sem_05'
        }
        
        # Find matching folder
        sem_folder = None
        for prefix, folder in sem_folders.items():
            if course_code.startswith(prefix):
                sem_folder = folder
                break
        
        if not sem_folder:
            return jsonify({'error': 'Course not found', 'detailed_content': 'Module explanation not available for this course.'}), 404
        
        explain_file = os.path.join(os.path.dirname(__file__), 'sem_explain', sem_folder, f'{course_code}.json')
        
        if not os.path.exists(explain_file):
            return jsonify({'error': 'Explanation file not found', 'detailed_content': 'Module explanation not available.'}), 404
        
        with open(explain_file, 'r', encoding='utf-8') as f:
            explain_data = json.load(f)
        
        # Find the specific module
        module_data = None
        for module in explain_data.get('modules', []):
            if module.get('module_no') == module_number:
                module_data = module
                break
        
        if not module_data:
            return jsonify({'error': 'Module not found', 'detailed_content': 'Module explanation not available.'}), 404
        
        return jsonify({
            'subject_name': explain_data.get('subject_name', ''),
            'module_number': module_data.get('module_no'),
            'title': module_data.get('title', ''),
            'summary': module_data.get('summary', ''),
            'detailed_content': module_data.get('detailed_content', ''),
            'raw_text': module_data.get('raw_text', '')
        })
    except Exception as e:
        return jsonify({'error': str(e), 'detailed_content': 'Error loading module explanation.'}), 500

@app.route('/')
def home():
    # If student not logged in, show login first
    try:
        if not session.get('user'):
            return redirect(url_for('login.login'))
    except Exception:
        # session may not be available; fallback to index
        pass
    return render_template('index.html')


@app.route('/student-start')
def student_start():
    """Entry point for students — send them to the login page first."""
    try:
        # If already logged-in, send to home; otherwise to login
        if session.get('user'):
            return redirect(url_for('home'))
        return redirect(url_for('login.login'))
    except Exception:
        # fallback to main home if login blueprint isn't available
        return render_template('index.html')

@app.route('/faculty')
def faculty():
    return render_template('faculty.html')

@app.route('/get', methods=['GET', 'POST'])
def get_response():
    if request.method == "POST":
        user_text = (request.form.get("msg", "") or "").lower().strip()
    else:
        user_text = (request.args.get("msg", "") or "").lower().strip()

    best_match = find_best_match(user_text)
    response_text = knowledge.get(best_match, knowledge["default"])
    return jsonify({"response": response_text})



if __name__ == "__main__":
    # Use 0.0.0.0 only if you intend to expose the dev server on the network
    app.run(debug=True, port=int(os.environ.get("PORT", 8081)))