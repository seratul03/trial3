import app, json

def main():
    q = 'kanyashree scholarship'
    print('LOADED_DOCS count:', len(app.LOADED_DOCS))
    sch_keys = [k for k in app.LOADED_DOCS.keys() if 'scholarship' in k.lower()]
    print('Scholarship files:')
    print(json.dumps(sch_keys, indent=2))
    res = app.retrieve_top_k(q, k=8)
    print('\nretrieve_top_k results:')
    for r in res:
        print('-', r['path'], 'score=', r['score'])
        print('  snippet:', r['snippet'][:200].replace('\n', ' '))

if __name__ == '__main__':
    main()
