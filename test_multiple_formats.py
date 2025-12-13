"""Test formatting with multiple scholarships"""
import sys
sys.path.insert(0, '.')
import json
from app.app import format_scholarship_for_user

scholarships = ['aikyashree.json', 'nabanna.json', 'sports.json']

for sch_file in scholarships:
    with open(f'Scholarship/data/detailed scholarship/{sch_file}', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n" + "="*80)
    print(f"Testing: {sch_file}")
    print("="*80)
    formatted = format_scholarship_for_user(data)
    # Show first 800 characters
    print(formatted[:800])
    print("\n... (truncated for testing)\n")
