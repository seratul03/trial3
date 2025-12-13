import json
from app import app as flask_app

def post_profile(client, profile):
    return client.post('/api/profile', json=profile)

def post_chat(client, query):
    return client.post('/chat', json={'query': query})

queries = [
    'Tell me about Kanyashree',
    'Am I eligible if family income is 1,20,000 per year?',
    'I am a first year B.Tech CSE student belonging to SC community. Am I eligible for Kanyashree?',
    'What scholarships does Brainware University offer?'
]

profile = {
    'course': 'B.Tech CSE',
    'year': '1',
    'community': 'SC',
    'income': '120000'
}


def main():
    client = flask_app.test_client()
    r = post_profile(client, profile)
    print('Set profile status:', r.status_code, r.get_json())
    for q in queries:
        resp = post_chat(client, q)
        print('\nQuery:', q)
        try:
            print(json.dumps(resp.get_json(), indent=2, ensure_ascii=False))
        except Exception:
            print('Response text:', resp.get_data(as_text=True))

if __name__ == '__main__':
    main()
