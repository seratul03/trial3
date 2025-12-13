"""
Test script to verify scholarship files are being loaded correctly
"""
import json
from pathlib import Path
import os

def test_scholarship_loading():
    """Test that scholarship files from detailed scholarship folder are loaded"""
    
    print("=" * 80)
    print("SCHOLARSHIP FILES LOADING TEST")
    print("=" * 80)
    
    # Check if detailed scholarship folder exists
    detailed_scholarship_path = Path(__file__).parent / 'Scholarship' / 'data' / 'detailed scholarship'
    
    if not detailed_scholarship_path.exists():
        print(f"❌ ERROR: Detailed scholarship folder not found at: {detailed_scholarship_path}")
        return False
    
    print(f"✅ Found detailed scholarship folder: {detailed_scholarship_path}")
    
    # List all JSON files in the folder
    json_files = list(detailed_scholarship_path.glob('*.json'))
    
    print(f"\n📁 Found {len(json_files)} JSON files:")
    for json_file in json_files:
        print(f"   - {json_file.name}")
    
    # Load and verify each file
    print("\n🔍 Verifying file contents:")
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check for key scholarship fields
            scholarship_name = data.get('scholarship_name') or data.get('official_name') or data.get('popular_name')
            has_eligibility = 'eligibility' in data or 'eligibility_criteria' in data
            has_benefits = 'scholarship_benefits' in data or 'benefits' in data
            
            print(f"\n   {json_file.name}:")
            print(f"      Name: {scholarship_name}")
            print(f"      Has Eligibility: {'✅' if has_eligibility else '❌'}")
            print(f"      Has Benefits: {'✅' if has_benefits else '❌'}")
            print(f"      Total Fields: {len(data)}")
            
            # Show a sample of the data structure
            print(f"      Top-level keys: {list(data.keys())[:10]}")
            
        except Exception as e:
            print(f"   ❌ ERROR loading {json_file.name}: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    return True

if __name__ == '__main__':
    test_scholarship_loading()
