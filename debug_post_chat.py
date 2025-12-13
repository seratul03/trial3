import json
from app import app as flask_app

def main():
    client = flask_app.test_client()
    resp = client.post('/chat', json={'query':'Tell me about kanyashree scholarship?'} )
    print('Status:', resp.status_code)
    try:
        print(json.dumps(resp.get_json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print('Response text:', resp.get_data(as_text=True))

if __name__ == '__main__':
    main()
