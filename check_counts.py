import json

files = ['medha_britti.json', 'kanyashree.json']
for f in files:
    with open(f'Scholarship/data/detailed scholarship/{f}', encoding='utf-8') as file:
        data = json.load(file)
        text = json.dumps(data).lower()
        print(f"\n{f}:")
        print(f"  'scholarship' count: {text.count('scholarship')}")
        print(f"  'kanyashree' count: {text.count('kanyashree')}")
        print(f"  Total length: {len(text)}")
