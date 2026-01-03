from flask import Flask, request, jsonify, session, send_from_directory, abort
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
from datetime import datetime, timedelta
import os
from functools import wraps

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'admin.db'
# Target upload directory provided by the user; fallback to a local folder if creation fails.
PREFERRED_UPLOAD_ROOT = Path(r"C:\Users\Seratul Mustakim\Desktop\Ai saves\College_chatbot\admin\uploads")
UPLOAD_ROOT = PREFERRED_UPLOAD_ROOT
try:
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
except Exception:
    UPLOAD_ROOT = BASE_DIR / 'uploads'
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=str(BASE_DIR / 'static'), static_url_path='/static')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB limit
app.secret_key = 'dev-secret-key-change-me'
app.permanent_session_lifetime = timedelta(minutes=30)


def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'admin_email' not in session:
            return jsonify({'error': 'unauthorized'}), 401
        return fn(*args, **kwargs)
    return wrapper


SESSION_CATEGORY_RULES = {
    'hostel': ['hostel', 'dorm', 'residence', 'mess'],
    'library': ['library', 'book', 'journal', 'borrow'],
    'faculty': ['faculty', 'professor', 'teacher', 'mentor'],
    'research': ['research', 'lab', 'paper', 'publication', 'grant'],
    'assignment': ['assignment', 'homework', 'submission', 'deadline'],
    'syllabus': ['syllabus', 'course outline', 'curriculum'],
    'exam': ['exam', 'timetable', 'result', 'grade', 'test'],
    'canteen': ['canteen', 'mess hall', 'food court', 'cafeteria'],
    'holiday': ['holiday', 'vacation', 'leave', 'break'],
    'general': ['info', 'information', 'general', 'question'],
    'others': [],
}


def init_db(force=False):
    if force and DB_PATH.exists():
        try:
            os.remove(DB_PATH)
        except Exception:
            pass
    # Always ensure required tables exist (CREATE IF NOT EXISTS)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'admin',
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS kb (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        department TEXT,
        tags TEXT,
        active INTEGER DEFAULT 1,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        transcript TEXT,
        status TEXT,
        started_at TEXT,
        ended_at TEXT
    );
    CREATE TABLE IF NOT EXISTS audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_email TEXT,
        action TEXT,
        detail TEXT,
        ts TEXT
    );
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        message TEXT,
        created_at TEXT,
        handled INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        department TEXT,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        semester INTEGER,
        department TEXT,
        enabled INTEGER DEFAULT 1,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS syllabus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        filename TEXT,
        filetype TEXT,
        department TEXT,
        semester INTEGER,
        active INTEGER DEFAULT 1,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS faq (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT,
        active INTEGER DEFAULT 1,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS custom_replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trigger TEXT,
        response TEXT,
        priority INTEGER DEFAULT 10,
        active INTEGER DEFAULT 1,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        publish_at TEXT,
        expire_at TEXT,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        visible INTEGER DEFAULT 1,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS error_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        message TEXT,
        detail TEXT,
        ts TEXT
    );
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        filename TEXT,
        filetype TEXT,
        tags TEXT,
        department TEXT,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS session_categories (
        session_id INTEGER,
        category TEXT,
        PRIMARY KEY (session_id, category)
    );
    ''')

    # seed admin user
    now = datetime.utcnow().isoformat()
    admin_pass = generate_password_hash('password123')
    try:
        cur.execute('INSERT INTO users (email, password_hash, role, created_at) VALUES (?, ?, ?, ?)',
                    ('admin@university.edu', admin_pass, 'admin', now))
    except sqlite3.IntegrityError:
        pass

    # seed KB
    kb_items = [
        ('How to apply for scholarship', 'Visit the scholarships page and fill the application.', 'Scholarship', 'scholarship,apply', 1),
        ('Hostel rules summary', 'Hostel rules include quiet hours 10pm-6am, guests allowed...', 'Hostel', 'hostel,rules', 1),
        ('Exam timetable release', 'Exam timetables are published on the exam portal two weeks before exams.', 'Exams', 'exam,timetable', 1),
    ]
    for title, content, dept, tags, active in kb_items:
        cur.execute('INSERT INTO kb (title, content, department, tags, active, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                    (title, content, dept, tags, active, now))

    # seed simulated sessions
    sessions = [
        ('student1@university.edu', 'I want to know how to apply for scholarship', 'answered', now, now),
        ('student2@university.edu', 'What are hostel quiet hours?', 'answered', now, now),
        ('student3@university.edu', 'When will exam timetable be released?', 'unanswered', now, None),
    ]
    for email, transcript, status, started, ended in sessions:
        cur.execute('INSERT INTO sessions (user_email, transcript, status, started_at, ended_at) VALUES (?, ?, ?, ?, ?)',
                    (email, transcript, status, started, ended))

    # seed default control settings if not present
    defaults = {
        'chatbot_enabled': '1',
        'maintenance_mode': '0',
        'maintenance_reply': 'The system is under maintenance. Please try again later.',
        'greeting_message': 'Hello! How can I help you today?',
        'fallback_message': 'Sorry, I do not understand. Please rephrase or contact support.',
        'tone': 'neutral',
        'suggestions_enabled': '1'
    }
    for k, v in defaults.items():
        cur.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (k, v))

    conn.commit()
    conn.close()


def log_action(admin_email, action, detail=''):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO audit (admin_email, action, detail, ts) VALUES (?, ?, ?, ?)',
                     (admin_email, action, detail, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
    except Exception:
        pass


@app.route('/api/subjects', methods=['GET', 'POST'])
@login_required
def subjects():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        rows = cur.execute('SELECT * FROM subjects ORDER BY id DESC').fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    data = request.json
    name = data.get('name')
    department = data.get('department')
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO subjects (name, department, created_at) VALUES (?, ?, ?)', (name, department, now))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'), 'create_subject', name)
    return jsonify({'ok': True})


@app.route('/api/subjects/<int:sid>', methods=['PUT','DELETE'])
@login_required
def subjects_modify(sid):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'DELETE':
        cur.execute('DELETE FROM subjects WHERE id=?', (sid,))
        conn.commit()
        conn.close()
        log_action(session.get('admin_email'),'delete_subject',str(sid))
        return jsonify({'ok': True})
    data = request.json
    name = data.get('name')
    department = data.get('department')
    cur.execute('UPDATE subjects SET name=?, department=? WHERE id=?', (name, department, sid))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'),'update_subject',str(sid))
    return jsonify({'ok': True})


@app.route('/api/courses', methods=['GET', 'POST'])
@login_required
def courses():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        rows = cur.execute('SELECT * FROM courses ORDER BY id DESC').fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    data = request.json
    name = data.get('name')
    semester = data.get('semester')
    department = data.get('department')
    enabled = 1 if data.get('enabled', True) else 0
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO courses (name, semester, department, enabled, created_at) VALUES (?, ?, ?, ?, ?)', (name, semester, department, enabled, now))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'), 'create_course', name)
    return jsonify({'ok': True})


@app.route('/api/courses/<int:cid>', methods=['PUT','DELETE'])
@login_required
def courses_modify(cid):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'DELETE':
        cur.execute('DELETE FROM courses WHERE id=?', (cid,))
        conn.commit()
        conn.close()
        log_action(session.get('admin_email'),'delete_course',str(cid))
        return jsonify({'ok': True})
    data = request.json
    name = data.get('name')
    semester = data.get('semester')
    department = data.get('department')
    enabled = 1 if data.get('enabled', True) else 0
    cur.execute('UPDATE courses SET name=?, semester=?, department=?, enabled=? WHERE id=?', (name, semester, department, enabled, cid))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'),'update_course',str(cid))
    return jsonify({'ok': True})


@app.route('/api/syllabus', methods=['GET', 'POST'])
@login_required
def syllabus_list_create():
    if request.method == 'GET':
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM syllabus ORDER BY id DESC').fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    # POST with multipart/form-data
    file = request.files.get('file')
    title = request.form.get('title')
    department = request.form.get('department')
    semester = request.form.get('semester')
    active = 1 if request.form.get('active','1')=='1' else 0
    now = datetime.utcnow().isoformat()
    filename = None
    filetype = None
    if file:
        upload_dir = BASE_DIR / 'static' / 'uploads'
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{int(datetime.utcnow().timestamp())}_{file.filename}"
        filepath = upload_dir / filename
        file.save(str(filepath))
        filetype = file.mimetype
    conn = get_db_connection()
    conn.execute('INSERT INTO syllabus (title, filename, filetype, department, semester, active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)', (title, filename, filetype, department, semester, active, now))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'), 'upload_syllabus', title)
    return jsonify({'ok': True})


@app.route('/api/syllabus/<int:sid>', methods=['DELETE','PUT'])
@login_required
def syllabus_modify(sid):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'DELETE':
        cur.execute('DELETE FROM syllabus WHERE id = ?', (sid,))
        conn.commit()
        conn.close()
        log_action(session.get('admin_email'), 'delete_syllabus', str(sid))
        return jsonify({'ok': True})
    data = request.json
    title = data.get('title')
    active = 1 if data.get('active', True) else 0
    cur.execute('UPDATE syllabus SET title=?, active=? WHERE id=?', (title, active, sid))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'), 'update_syllabus', str(sid))
    return jsonify({'ok': True})


@app.route('/api/faq', methods=['GET', 'POST'])
@login_required
def faq_list_create():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        rows = cur.execute('SELECT * FROM faq ORDER BY id DESC').fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    data = request.json
    q = data.get('question')
    a = data.get('answer')
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO faq (question, answer, active, created_at) VALUES (?, ?, ?, ?)', (q, a, 1, now))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'), 'create_faq', q)
    return jsonify({'ok': True})


@app.route('/api/faq/<int:fid>', methods=['PUT','DELETE'])
@login_required
def faq_modify(fid):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'DELETE':
        cur.execute('DELETE FROM faq WHERE id=?', (fid,))
        conn.commit()
        conn.close()
        log_action(session.get('admin_email'),'delete_faq',str(fid))
        return jsonify({'ok': True})
    data = request.json
    q = data.get('question')
    a = data.get('answer')
    active = 1 if data.get('active', True) else 0
    cur.execute('UPDATE faq SET question=?, answer=?, active=? WHERE id=?', (q, a, active, fid))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'),'update_faq',str(fid))
    return jsonify({'ok': True})


@app.route('/api/custom-replies', methods=['GET', 'POST'])
@login_required
def custom_replies_list_create():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        rows = cur.execute('SELECT * FROM custom_replies ORDER BY priority ASC').fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    data = request.json
    trigger = data.get('trigger')
    response = data.get('response')
    priority = int(data.get('priority', 10))
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO custom_replies (trigger, response, priority, active, created_at) VALUES (?, ?, ?, ?, ?)', (trigger, response, priority, 1, now))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'), 'create_custom_reply', trigger)
    return jsonify({'ok': True})


@app.route('/api/custom-replies/<int:rid>', methods=['PUT','DELETE'])
@login_required
def custom_replies_modify(rid):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'DELETE':
        cur.execute('DELETE FROM custom_replies WHERE id=?', (rid,))
        conn.commit()
        conn.close()
        log_action(session.get('admin_email'),'delete_custom_reply',str(rid))
        return jsonify({'ok': True})
    data = request.json
    trigger = data.get('trigger')
    response = data.get('response')
    priority = int(data.get('priority', 10))
    active = 1 if data.get('active', True) else 0
    cur.execute('UPDATE custom_replies SET trigger=?, response=?, priority=?, active=? WHERE id=?', (trigger, response, priority, active, rid))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'),'update_custom_reply',str(rid))
    return jsonify({'ok': True})


@app.route('/api/control', methods=['GET', 'POST'])
@login_required
def control_api():
    """Get or update chatbot control settings like on/off, greeting, fallback, tone, suggestions."""
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        rows = cur.execute(
            'SELECT key, value FROM settings WHERE key IN ("chatbot_enabled","maintenance_mode","maintenance_reply","greeting_message","fallback_message","tone","suggestions_enabled")'
        ).fetchall()
        conn.close()
        return jsonify({r['key']: r['value'] for r in rows})
    data = request.json or {}
    chatbot_enabled = '1' if str(data.get('chatbot_enabled', '1')) == '1' else '0'
    maintenance_mode_requested = '1' if str(data.get('maintenance_mode', '0')) == '1' else '0'
    # Maintenance can only be toggled when chatbot is enabled
    maintenance_mode = maintenance_mode_requested if chatbot_enabled == '1' else '0'
    updates = {
        'chatbot_enabled': chatbot_enabled,
        'maintenance_mode': maintenance_mode,
        'maintenance_reply': data.get('maintenance_reply', ''),
        'greeting_message': data.get('greeting_message', ''),
        'fallback_message': data.get('fallback_message', ''),
        'tone': data.get('tone', 'neutral'),
        'suggestions_enabled': '1' if str(data.get('suggestions_enabled', '1')) == '1' else '0',
    }
    for k, v in updates.items():
        cur.execute('REPLACE INTO settings (key, value) VALUES (?, ?)', (k, str(v)))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'), 'update_control', str(updates))
    return jsonify({'ok': True, **updates})


@app.route('/api/documents', methods=['GET', 'POST'])
@login_required
def documents_list_create():
    if request.method == 'GET':
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM documents ORDER BY id DESC').fetchall()
        conn.close()
        docs = []
        for r in rows:
            item = dict(r)
            if item.get('filename'):
                item['download_url'] = f"/api/documents/{item['id']}/download"
            docs.append(item)
        return jsonify(docs)
    # POST multipart
    file = request.files.get('file')
    title = request.form.get('title') or (file.filename if file else 'untitled')
    tags = request.form.get('tags')
    department = request.form.get('department')
    now = datetime.utcnow().isoformat()
    filename = None
    filetype = None
    if file:
        filename = f"{int(datetime.utcnow().timestamp())}_{file.filename}"
        filepath = UPLOAD_ROOT / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        file.save(str(filepath))
        filetype = file.mimetype
    conn = get_db_connection()
    conn.execute('INSERT INTO documents (title, filename, filetype, tags, department, created_at) VALUES (?, ?, ?, ?, ?, ?)', (title, filename, filetype, tags, department, now))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'), 'upload_document', title)
    return jsonify({'ok': True})


@app.route('/api/documents/<int:did>', methods=['DELETE'])
@login_required
def documents_delete(did):
    conn = get_db_connection()
    cur = conn.cursor()
    row = cur.execute('SELECT filename FROM documents WHERE id=?', (did,)).fetchone()
    if row and row['filename']:
        try:
            fpath = UPLOAD_ROOT / row['filename']
            if fpath.exists():
                fpath.unlink()
        except Exception:
            pass
    cur.execute('DELETE FROM documents WHERE id=?', (did,))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'), 'delete_document', str(did))
    return jsonify({'ok': True})


@app.route('/api/documents/<int:did>/download', methods=['GET'])
@login_required
def documents_download(did):
    conn = get_db_connection()
    row = conn.execute('SELECT filename, title FROM documents WHERE id=?', (did,)).fetchone()
    conn.close()
    if not row or not row['filename']:
        return abort(404)
    filepath = UPLOAD_ROOT / row['filename']
    if not filepath.exists():
        return abort(404)
    return send_from_directory(filepath.parent, filepath.name, as_attachment=True, download_name=row['filename'])


@app.route('/api/unanswered', methods=['GET'])
@login_required
def unanswered_list():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM sessions WHERE status='unanswered' ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/unanswered/<int:sid>/answer', methods=['POST'])
@login_required
def unanswered_answer(sid):
    data = request.json or {}
    answer = data.get('answer')
    add_to_kb = data.get('add_to_kb', False)
    save_as_custom_reply = data.get('save_as_custom_reply', False)
    if not answer:
        return jsonify({'error': 'answer required'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    # append answer to transcript and mark answered
    row = cur.execute('SELECT transcript FROM sessions WHERE id=?', (sid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'session not found'}), 404
    transcript = (row['transcript'] or '') + '\n\nAdmin answer: ' + answer
    cur.execute('UPDATE sessions SET transcript=?, status=?, ended_at=? WHERE id=?', (transcript, 'answered', datetime.utcnow().isoformat(), sid))
    if add_to_kb:
        now = datetime.utcnow().isoformat()
        cur.execute('INSERT INTO kb (title, content, department, tags, active, created_at) VALUES (?, ?, ?, ?, ?, ?)', (f'Answer for session {sid}', answer, 'General', '', 1, now))
    if save_as_custom_reply:
        trigger = (row['transcript'] or '').strip()[:140] or f'session-{sid}'
        cur.execute('INSERT INTO custom_replies (trigger, response, priority, active, created_at) VALUES (?, ?, ?, ?, ?)', (trigger, answer, 10, 1, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'), 'answer_unanswered', str(sid))
    return jsonify({'ok': True})


@app.route('/api/analytics/daily-users', methods=['GET'])
@login_required
def analytics_daily_users():
    conn = get_db_connection()
    rows = conn.execute("SELECT substr(started_at,1,10) as day, COUNT(DISTINCT user_email) as c FROM sessions WHERE started_at IS NOT NULL GROUP BY day ORDER BY day DESC LIMIT 30").fetchall()
    conn.close()
    return jsonify({r['day']: r['c'] for r in rows})


@app.route('/api/classify', methods=['POST'])
@login_required
def classify_sessions():
    """Simple keyword-based classification for sessions; stores results in session_categories."""
    conn = get_db_connection()
    rows = conn.execute('SELECT id, transcript FROM sessions').fetchall()
    cur = conn.cursor()
    for r in rows:
        sid = r['id']
        text = (r['transcript'] or '').lower()
        assigned = set()
        for cat, keys in SESSION_CATEGORY_RULES.items():
            for k in keys:
                if k in text:
                    assigned.add(cat)
                    break
        if not assigned:
            assigned.add('others')
        # remove existing categories for session
        cur.execute('DELETE FROM session_categories WHERE session_id=?', (sid,))
        for cat in assigned:
            cur.execute('INSERT OR IGNORE INTO session_categories (session_id, category) VALUES (?, ?)', (sid, cat))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'), 'classify_sessions', 'manual run')
    return jsonify({'ok': True})


@app.route('/api/categories', methods=['GET'])
@login_required
def categories_counts():
    conn = get_db_connection()
    rows = conn.execute('SELECT category, COUNT(*) as c FROM session_categories GROUP BY category').fetchall()
    conn.close()
    return jsonify({r['category']: r['c'] for r in rows})


@app.route('/api/announcements', methods=['GET', 'POST'])
@login_required
def announcements_list_create():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        rows = cur.execute('SELECT * FROM announcements ORDER BY id DESC').fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    data = request.json
    title = data.get('title')
    content = data.get('content')
    publish_at = data.get('publish_at')
    expire_at = data.get('expire_at')
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO announcements (title, content, publish_at, expire_at, created_at) VALUES (?, ?, ?, ?, ?)', (title, content, publish_at, expire_at, now))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'), 'create_announcement', title)
    return jsonify({'ok': True})


@app.route('/api/announcements/<int:aid>', methods=['PUT','DELETE'])
@login_required
def announcements_modify(aid):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'DELETE':
        cur.execute('DELETE FROM announcements WHERE id=?', (aid,))
        conn.commit()
        conn.close()
        log_action(session.get('admin_email'),'delete_announcement',str(aid))
        return jsonify({'ok': True})
    data = request.json
    title = data.get('title')
    content = data.get('content')
    publish_at = data.get('publish_at')
    expire_at = data.get('expire_at')
    cur.execute('UPDATE announcements SET title=?, content=?, publish_at=?, expire_at=? WHERE id=?', (title, content, publish_at, expire_at, aid))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'),'update_announcement',str(aid))
    return jsonify({'ok': True})


@app.route('/api/exams', methods=['GET', 'POST'])
@login_required
def exams_list_create():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        rows = cur.execute('SELECT * FROM exams ORDER BY id DESC').fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    data = request.json
    title = data.get('title')
    content = data.get('content')
    visible = 1 if data.get('visible', True) else 0
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO exams (title, content, visible, created_at) VALUES (?, ?, ?, ?)', (title, content, visible, now))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'), 'create_exam', title)
    return jsonify({'ok': True})


@app.route('/api/exams/<int:eid>', methods=['PUT','DELETE'])
@login_required
def exams_modify(eid):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'DELETE':
        cur.execute('DELETE FROM exams WHERE id=?', (eid,))
        conn.commit()
        conn.close()
        log_action(session.get('admin_email'),'delete_exam',str(eid))
        return jsonify({'ok': True})
    data = request.json
    title = data.get('title')
    content = data.get('content')
    visible = 1 if data.get('visible', True) else 0
    cur.execute('UPDATE exams SET title=?, content=?, visible=? WHERE id=?', (title, content, visible, eid))
    conn.commit()
    conn.close()
    log_action(session.get('admin_email'),'update_exam',str(eid))
    return jsonify({'ok': True})


@app.route('/api/errors', methods=['GET', 'POST'])
@login_required
def errors_list_create():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        rows = cur.execute('SELECT * FROM error_logs ORDER BY id DESC').fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    data = request.json
    source = data.get('source')
    message = data.get('message')
    detail = data.get('detail')
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO error_logs (source, message, detail, ts) VALUES (?, ?, ?, ?)', (source, message, detail, now))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# Initialize DB at import time to avoid depending on Flask version's decorators
init_db()


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or request.form
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'email and password required'}), 400
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    if user and check_password_hash(user['password_hash'], password):
        session['admin_email'] = email
        session.permanent = True
        try:
            log_action(email, 'login', 'admin logged in')
        except Exception:
            pass
        return jsonify({'ok': True, 'email': email})
    return jsonify({'error': 'invalid credentials'}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('admin_email', None)
    return jsonify({'ok': True})


@app.route('/api/me')
def me():
    email = session.get('admin_email')
    if not email:
        return jsonify({'admin': None})
    return jsonify({'admin': {'email': email}})


@app.route('/api/users', methods=['GET', 'POST'])
@login_required
def users():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        rows = cur.execute('SELECT email, role, created_at FROM users').fetchall()
        result = [dict(r) for r in rows]
        conn.close()
        return jsonify(result)
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'admin')
    if not email or not password:
        return jsonify({'error': 'email and password required'}), 400
    password_hash = generate_password_hash(password)
    now = datetime.utcnow().isoformat()
    try:
        cur.execute('INSERT INTO users (email, password_hash, role, created_at) VALUES (?, ?, ?, ?)',
                    (email, password_hash, role, now))
        conn.commit()
        try:
            log_action(session.get('admin_email','system'), 'create_user', email)
        except Exception:
            pass
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'user exists'}), 400
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/users/<path:email>', methods=['DELETE'])
@login_required
def users_modify(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE email = ?', (email,))
    conn.commit()
    conn.close()
    try:
        log_action(session.get('admin_email'), 'delete_user', email)
    except Exception:
        pass
    return jsonify({'ok': True})


@app.route('/api/kb', methods=['GET', 'POST'])
@login_required
def kb_list_create():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        rows = cur.execute('SELECT * FROM kb ORDER BY id DESC').fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    data = request.json
    title = data.get('title')
    content = data.get('content')
    department = data.get('department') or 'General'
    tags = data.get('tags') or ''
    active = 1 if data.get('active', True) else 0
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO kb (title, content, department, tags, active, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                (title, content, department, tags, active, now))
    conn.commit()
    conn.close()
    try:
        log_action(session.get('admin_email'), 'create_kb', title)
    except Exception:
        pass
    return jsonify({'ok': True})


@app.route('/api/kb/<int:item_id>', methods=['PUT', 'DELETE'])
@login_required
def kb_modify(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'DELETE':
        cur.execute('DELETE FROM kb WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
        try:
            log_action(session.get('admin_email'), 'delete_kb', str(item_id))
        except Exception:
            pass
        return jsonify({'ok': True})
    data = request.json
    title = data.get('title')
    content = data.get('content')
    department = data.get('department')
    tags = data.get('tags')
    active = 1 if data.get('active', True) else 0
    cur.execute('UPDATE kb SET title=?, content=?, department=?, tags=?, active=? WHERE id=?',
                (title, content, department, tags, active, item_id))
    conn.commit()
    conn.close()
    try:
        log_action(session.get('admin_email'), 'update_kb', str(item_id))
    except Exception:
        pass
    return jsonify({'ok': True})


@app.route('/api/sessions', methods=['GET'])
@login_required
def sessions_list():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM sessions ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/sessions/<int:sid>', methods=['GET'])
@login_required
def session_detail(sid):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM sessions WHERE id = ?', (sid,)).fetchone()
    conn.close()
    if not row:
        return jsonify({'error':'not found'}), 404
    return jsonify(dict(row))


@app.route('/api/simulate-session', methods=['POST'])
@login_required
def simulate_session():
    data = request.json
    user_email = data.get('user_email') or 'simulated@university.edu'
    transcript = data.get('transcript') or 'Simulated conversation text.'
    status = data.get('status') or 'answered'
    now = datetime.utcnow().isoformat()
    conn = get_db_connection()
    conn.execute('INSERT INTO sessions (user_email, transcript, status, started_at, ended_at) VALUES (?, ?, ?, ?, ?)',
                 (user_email, transcript, status, now, now if status!='unanswered' else None))
    conn.commit()
    conn.close()
    try:
        log_action(session.get('admin_email'), 'simulate_session', user_email)
    except Exception:
        pass
    return jsonify({'ok': True})


@app.route('/api/analytics', methods=['GET'])
@login_required
def analytics():
    conn = get_db_connection()
    cur = conn.cursor()
    total_sessions = cur.execute('SELECT COUNT(*) as c FROM sessions').fetchone()['c']
    unanswered = cur.execute("SELECT COUNT(*) as c FROM sessions WHERE status='unanswered'").fetchone()['c']
    total_kb = cur.execute('SELECT COUNT(*) as c FROM kb').fetchone()['c']
    total_users = cur.execute('SELECT COUNT(*) as c FROM users').fetchone()['c']
    # queries today and this week
    today_count = cur.execute("SELECT COUNT(*) as c FROM sessions WHERE date(started_at)=date('now')").fetchone()['c']
    week_count = cur.execute("SELECT COUNT(*) as c FROM sessions WHERE date(started_at) >= date('now','-6 days')").fetchone()['c']
    # AI success rate as answered / total_sessions
    answered = cur.execute("SELECT COUNT(*) as c FROM sessions WHERE status='answered'").fetchone()['c']
    ai_success_rate = round((answered / total_sessions * 100) if total_sessions else 0, 2)
    conn.close()
    return jsonify({'total_sessions': total_sessions, 'unanswered_sessions': unanswered, 'total_kb': total_kb, 'total_users': total_users, 'queries_today': today_count, 'queries_week': week_count, 'ai_success_rate': ai_success_rate})


@app.route('/api/analytics/top-topics', methods=['GET'])
@login_required
def analytics_top_topics():
    # crude keyword counting from sessions.transcript
    conn = get_db_connection()
    rows = conn.execute('SELECT transcript FROM sessions').fetchall()
    conn.close()
    counts = {}
    for r in rows:
        text = (r['transcript'] or '').lower()
        for word in text.split():
            w = ''.join([c for c in word if c.isalnum()])
            if len(w) < 3: continue
            counts[w] = counts.get(w, 0) + 1
    top = sorted(counts.items(), key=lambda x: -x[1])[:20]
    return jsonify({'top_topics': top})


@app.route('/api/analytics/queries-by-day', methods=['GET'])
@login_required
def analytics_queries_by_day():
    conn = get_db_connection()
    rows = conn.execute("SELECT substr(started_at,1,10) as day, COUNT(*) as c FROM sessions WHERE started_at IS NOT NULL GROUP BY day ORDER BY day DESC LIMIT 30").fetchall()
    conn.close()
    return jsonify({r['day']: r['c'] for r in rows})


@app.route('/api/analytics/category', methods=['GET'])
@login_required
def analytics_by_category():
    category = request.args.get('category','')
    keywords = {
        'exam': ['exam','timetable','result','grade'],
        'syllabus': ['syllabus','course','semester'],
        'rules': ['rule','hostel','policy']
    }
    keys = keywords.get(category.lower(), [])
    conn = get_db_connection()
    if not keys:
        # return empty counts
        conn.close()
        return jsonify({'category': category, 'count': 0})
    q = ' OR '.join(["transcript LIKE ?" for _ in keys])
    params = [f'%{k}%' for k in keys]
    rows = conn.execute(f'SELECT COUNT(*) as c FROM sessions WHERE {q}', params).fetchone()
    conn.close()
    return jsonify({'category': category, 'count': rows['c']})


@app.route('/api/reseed', methods=['POST'])
@login_required
def reseed():
    """Delete existing DB and recreate seeded DB. Protected endpoint."""
    try:
        init_db(force=True)
    except Exception as e:
        return jsonify({'error': 'reseed failed', 'detail': str(e)}), 500
    return jsonify({'ok': True, 'message': 'reseeded'})


@app.route('/api/reindex', methods=['POST'])
@login_required
def reindex():
    # Stub for re-indexing knowledge base / vectors
    try:
        log_action(session.get('admin_email'), 'reindex', 'manual trigger')
    except Exception:
        pass
    return jsonify({'ok': True, 'message': 'reindex started (stub)'})


@app.route('/api/audit', methods=['GET'])
@login_required
def audit_list():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 200').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/feedback', methods=['GET', 'POST'])
@login_required
def feedback_list_create():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        rows = cur.execute('SELECT * FROM feedback ORDER BY id DESC').fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    data = request.json
    user_email = data.get('user_email') or 'anonymous'
    message = data.get('message') or ''
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO feedback (user_email, message, created_at) VALUES (?, ?, ?)', (user_email, message, now))
    conn.commit()
    conn.close()
    try:
        log_action(session.get('admin_email'), 'submit_feedback', user_email)
    except Exception:
        pass
    return jsonify({'ok': True})


@app.route('/api/export/sessions', methods=['GET'])
@login_required
def export_sessions():
    import csv, io
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM sessions ORDER BY id DESC').fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id','user_email','transcript','status','started_at','ended_at'])
    for r in rows:
        writer.writerow([r['id'], r['user_email'], r['transcript'], r['status'], r['started_at'], r['ended_at']])
    resp = app.response_class(output.getvalue(), mimetype='text/csv')
    resp.headers['Content-Disposition'] = 'attachment; filename=sessions.csv'
    return resp


@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def settings_api():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        rows = cur.execute('SELECT key, value FROM settings').fetchall()
        conn.close()
        return jsonify({r['key']: r['value'] for r in rows})
    data = request.json
    for k, v in (data or {}).items():
        cur.execute('REPLACE INTO settings (key, value) VALUES (?, ?)', (k, str(v)))
    conn.commit()
    conn.close()
    try:
        log_action(session.get('admin_email'), 'update_settings', str(data))
    except Exception:
        pass
    return jsonify({'ok': True})


@app.errorhandler(413)
def too_large(_err):
    return jsonify({'error': 'file too large', 'limit_mb': 500}), 413


if __name__ == '__main__':
    app.run(debug=True, port=5001)
