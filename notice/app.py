from flask import Flask, render_template, jsonify, send_from_directory
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__, static_folder='static', template_folder='templates')

# Use project root for consistent paths (parent of this notice folder)
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
PDF_FOLDER = os.path.join(ROOT_DIR, 'notice', 'pdfs')


def parse_filename(fn):
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
        path = os.path.join(PDF_FOLDER, fn)
        mtime = os.path.getmtime(path)
        dt = datetime.fromtimestamp(mtime)
        if obj['date'] is None:
            obj['date'] = dt.strftime("%Y-%m-%d")
    except:
        obj['date'] = "1970-01-01"

    return obj


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/notices')
def api_notices():
    notices = []
    if not os.path.isdir(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)

    for fn in os.listdir(PDF_FOLDER):
        if fn.lower().endswith('.pdf'):
            notices.append(parse_filename(fn))

    return jsonify(notices)


@app.route('/pdfs/<path:filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_FOLDER, filename, as_attachment=False)


if __name__ == '__main__':
    app.run(debug=True)
