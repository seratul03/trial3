"""Test the new scholarship formatting"""
import sys
sys.path.insert(0, '.')
import json
from app import format_scholarship_for_user

# Load a sample scholarship
with open('Scholarship/data/detailed scholarship/kanyashree.json', 'r', encoding='utf-8') as f:
    kanyashree_data = json.load(f)

print("="*80)
print("TESTING NEW SCHOLARSHIP FORMATTING")
print("="*80)
print("\nFormatted Output:\n")
print(format_scholarship_for_user(kanyashree_data))
