Admin panel (Flask + SQLite) for the University Chatbot (trial)

Run:

1. Create a virtual environment (recommended) and install Flask and Werkzeug:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install flask werkzeug
```

2. Run the admin app:

```powershell
python admin\app.py
```

3. Open http://127.0.0.1:5001/

Default seeded admin:
- email: admin@university.edu
- password: password123

Notes:
- Frontend is static HTML/JS under `admin/static` and does not use Jinja.
- DB file `admin/admin.db` is created on first run and seeded with mock data.
- To reseed the mock data use the `Settings` tab -> `Reseed Mock Data` (logged-in admins only).
 - New features: Audit log, Feedback, user delete/role change, session export (CSV), session detail view.
 - Use the `Audit` tab to view admin actions and submitted feedback.
 - Implemented feature endpoints for: subjects, courses, syllabus upload, FAQs, custom replies, announcements, exams, and error logs. Use the new pages: `/static/syllabus.html`, `/static/control.html`, `/static/faq.html`, `/static/knowledge.html`, `/static/announcements.html`, `/static/exams.html`.
