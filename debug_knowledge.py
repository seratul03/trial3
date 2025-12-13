import json
from pathlib import Path
import os

# Same loader function from app.py
def load_all_json_files(root_dir=None):
    """Recursively find and load all .json and .jsonl files under root_dir (project root by default)."""
    root = Path(root_dir or os.path.dirname(__file__)).resolve()
    skip_dirs = {'.venv', 'venv', '__pycache__', '.git'}
    loaded = {}
    for p in root.rglob('*'):
        try:
            if p.is_dir():
                if p.name in skip_dirs:
                    continue
                else:
                    continue
            if p.suffix.lower() not in {'.json', '.jsonl'}:
                continue
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
                                items.append(line)
                    loaded[rel] = items
            except Exception as e:
                loaded[rel] = {'_load_error': str(e)}
        except Exception:
            continue
    return loaded

print("Loading all JSON files...")
LOADED_DOCS = load_all_json_files()

print(f"\nTotal files loaded: {len(LOADED_DOCS)}")
print("\nFiles containing 'BSCM101':")

for path, content in LOADED_DOCS.items():
    try:
        text = json.dumps(content) if isinstance(content, (dict, list)) else str(content)
        if 'bscm101' in text.lower():
            print(f"  ✓ {path}")
            # Check if it has subject info
            if isinstance(content, dict):
                if 'subject_name' in content:
                    print(f"    Subject: {content.get('subject_name', 'N/A')}")
                if 'subject_code' in content:
                    print(f"    Code: {content.get('subject_code', 'N/A')}")
    except Exception as e:
        print(f"  ✗ {path} - Error: {e}")

print("\nSample file paths:")
for i, path in enumerate(list(LOADED_DOCS.keys())[:10]):
    print(f"  {i+1}. {path}")
