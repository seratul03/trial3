import json
import os

def update_explanation_files():
    """Update all explanation files with course outcomes and prerequisites from sem_co_pre"""
    
    base_path = r"C:\Users\Seratul Mustakim\Downloads\College_chatbot\College_chatbot"
    
    # Process each semester
    for sem_num in range(1, 6):
        print(f"\n{'='*60}")
        print(f"Processing Semester {sem_num}")
        print(f"{'='*60}")
        
        # Read the course outcomes and prerequisites file
        co_pre_file = os.path.join(base_path, "sem_co_pre", f"sem{sem_num}.json")
        
        if not os.path.exists(co_pre_file):
            print(f"⚠️  Warning: {co_pre_file} not found, skipping...")
            continue
            
        with open(co_pre_file, 'r', encoding='utf-8') as f:
            sem_data = json.load(f)
        
        # Create a mapping of course_code to outcomes/prerequisites
        course_map = {}
        for subject in sem_data['subjects']:
            course_code = subject['course_code']
            # Convert prerequisites to array if it's a string
            prereq = subject.get('prerequisites', '')
            if isinstance(prereq, str):
                prereq = [prereq] if prereq and prereq.lower() != 'none' else []
            
            course_map[course_code] = {
                'course_outcomes': subject.get('course_outcomes', []),
                'prerequisites': prereq
            }
        
        # Update explanation files
        explain_dir = os.path.join(base_path, "sem_explain", f"sem_0{sem_num}")
        
        if not os.path.exists(explain_dir):
            print(f"⚠️  Warning: {explain_dir} not found, skipping...")
            continue
        
        updated_count = 0
        
        for filename in os.listdir(explain_dir):
            if not filename.endswith('.json'):
                continue
                
            course_code = filename.replace('.json', '')
            explain_file = os.path.join(explain_dir, filename)
            
            # Read existing explanation file
            with open(explain_file, 'r', encoding='utf-8') as f:
                explain_data = json.load(f)
            
            # Update with course outcomes and prerequisites if available
            if course_code in course_map:
                explain_data['course_outcomes'] = course_map[course_code]['course_outcomes']
                explain_data['prerequisites'] = course_map[course_code]['prerequisites']
                
                # Write back
                with open(explain_file, 'w', encoding='utf-8') as f:
                    json.dump(explain_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Updated {course_code}: {len(explain_data['course_outcomes'])} outcomes, {len(explain_data['prerequisites'])} prerequisites")
                updated_count += 1
            else:
                print(f"⚠️  No data found for {course_code}")
        
        print(f"\n📊 Semester {sem_num}: Updated {updated_count} files")
    
    print(f"\n{'='*60}")
    print("✅ All files updated successfully!")
    print(f"{'='*60}")

if __name__ == "__main__":
    update_explanation_files()
