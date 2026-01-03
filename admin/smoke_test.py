import requests
import sys

BASE = "http://127.0.0.1:5001"
ADMIN_EMAIL = "admin@university.edu"
ADMIN_PASS = "password123"

session = requests.Session()

def ok(resp):
    try:
        return resp.status_code, resp.json()
    except Exception:
        return resp.status_code, resp.text[:200]

def step(name, fn):
    print(f"--- {name} ---")
    try:
        resp = fn()
        code, body = ok(resp)
        print(code)
        print(body)
        return code, body
    except Exception as e:
        print("ERROR:", e)
        return None, str(e)

def main():
    results = {}

    # 1 - GET /api/me before login
    results['me_before'] = step('GET /api/me (before login)', lambda: session.get(f"{BASE}/api/me"))

    # 2 - POST /api/login
    def login():
        return session.post(f"{BASE}/api/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
    results['login'] = step('POST /api/login', login)

    # 3 - GET /api/me after login
    results['me_after'] = step('GET /api/me (after login)', lambda: session.get(f"{BASE}/api/me"))

    # 4 - GET /api/users
    results['users'] = step('GET /api/users', lambda: session.get(f"{BASE}/api/users"))

    # 5 - Create KB item
    def create_kb():
        return session.post(f"{BASE}/api/kb", json={"title":"smoke-test-kb","content":"created by smoke test"})
    code, body = step('POST /api/kb', create_kb)
    kb_id = None
    if isinstance(body, dict) and 'id' in body:
        kb_id = body['id']
    results['create_kb'] = (code, body)

    # 6 - Update KB (if created)
    if kb_id:
        results['update_kb'] = step('PUT /api/kb/<id>', lambda: session.put(f"{BASE}/api/kb/{kb_id}", json={"title":"smoke-test-kb-updated","content":"updated"}))
        results['delete_kb'] = step('DELETE /api/kb/<id>', lambda: session.delete(f"{BASE}/api/kb/{kb_id}"))

    # 7 - Simulate session
    results['simulate'] = step('POST /api/simulate-session', lambda: session.post(f"{BASE}/api/simulate-session", json={"user_email":"smoke.user@example.com","messages":"Hello from smoke test"}))

    # 8 - GET /api/sessions
    results['sessions'] = step('GET /api/sessions', lambda: session.get(f"{BASE}/api/sessions"))

    # 9 - GET /api/analytics
    results['analytics'] = step('GET /api/analytics', lambda: session.get(f"{BASE}/api/analytics"))

    # 10 - GET /api/export/sessions (CSV)
    def export_sessions():
        return session.get(f"{BASE}/api/export/sessions")
    code, body = step('GET /api/export/sessions', export_sessions)
    results['export_sessions'] = (code, 'csv' if isinstance(body, str) and (body.startswith('id') or '\n' in body) else body)

    # 11 - Logout
    results['logout'] = step('POST /api/logout', lambda: session.post(f"{BASE}/api/logout"))

    print('\nSummary:')
    ok_count = 0
    for k, v in results.items():
        code = v[0] if isinstance(v, tuple) else None
        status = 'OK' if code and 200 <= code < 300 else 'FAIL'
        print(f"{k}: {status} ({code})")
        if status == 'OK':
            ok_count += 1

    print(f"\nPassed {ok_count}/{len(results)} steps")

if __name__ == '__main__':
    main()
