import json
import os

# Read the JSON file
json_path = r"C:\Users\Seratul Mustakim\Downloads\College_chatbot\College_chatbot\Faculty\brainware_cse_ai_faculty.json"
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Photo directory
photos_dir = r"C:\Users\Seratul Mustakim\Downloads\College_chatbot\College_chatbot\Faculty\Photos"

# Get all photo files
photo_files = os.listdir(photos_dir)
print(f"Found {len(photo_files)} photos")

# Create a mapping from name to photo file
photo_mapping = {}
for photo in photo_files:
    # Remove extension and normalize
    name_from_file = os.path.splitext(photo)[0]
    photo_mapping[name_from_file] = f"Faculty/Photos/{photo}"

# Function to add photo to faculty member
def add_photo_to_member(member_data):
    name = member_data.get('name')
    if name:
        # Try exact match first
        if name in photo_mapping:
            member_data['photo'] = photo_mapping[name]
            return True
        
        # Try variations (with/without Dr.)
        for photo_name in photo_mapping:
            if name.replace('Dr. ', '') == photo_name.replace('Dr. ', '').replace('Dr ', ''):
                member_data['photo'] = photo_mapping[photo_name]
                return True
    return False

# Add photos to faculty section
added_count = 0
for key, member in data['faculty'].items():
    if add_photo_to_member(member):
        added_count += 1

print(f"Added photos to {added_count} faculty members in 'faculty' section")

# Add photos to teachers section
added_count = 0
for key, member in data['teachers'].items():
    if add_photo_to_member(member):
        added_count += 1

print(f"Added photos to {added_count} faculty members in 'teachers' section")

# Save the updated JSON
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nUpdated JSON saved to: {json_path}")
print(f"Total faculty count: {data['teacher_count']}")
