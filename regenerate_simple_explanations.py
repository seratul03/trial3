"""
Simple Course Explanation Generator
Generates module-based explanations with 5-sentence summary at the end
"""

import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
SEM_JSON_DIR = BASE_DIR / "sem_json"
SEM_EXPLAIN_DIR = BASE_DIR / "sem_explain"

def generate_5_sentence_summary(course_name, course_code, modules):
    """Generate a 5-sentence summary about the subject"""
    
    summaries = {
        'HSMCM101': "Communication Skills is a foundational course that enhances your ability to express ideas clearly and effectively. This subject builds essential grammar, vocabulary, and pronunciation skills needed for professional settings. You'll learn communication theories and comprehension strategies. The course prepares you for academic writing, presentations, and workplace interactions. These skills are crucial for your entire academic journey and future career.",
        
        'BSCM101': "Semiconductor Physics introduces the quantum mechanical principles governing modern electronic devices. This course explores how materials behave at the atomic level and their applications in technology. You'll understand semiconductors, optical transitions, and measurement techniques. The knowledge forms the foundation for advanced electronics and optoelectronics. This subject is essential for anyone pursuing careers in electronics, photonics, or materials science.",
        
        'BSCM102': "Calculus & Linear Algebra provides the mathematical toolkit essential for engineering and science. This course covers differentiation, integration, sequences, series, and vector spaces. You'll develop analytical thinking and problem-solving abilities through rigorous mathematical methods. These concepts are fundamental for modeling real-world phenomena. Mastering this subject opens doors to advanced engineering courses and research opportunities.",
        
        'ESCM101': "Basic Electrical and Electronics Engineering bridges theory with practical circuit applications. This course covers DC/AC circuits, transformers, machines, and semiconductor devices. You'll learn to analyze electrical systems and understand electronic components. The subject provides hands-on experience with fundamental electrical concepts. These skills are applicable across all engineering disciplines.",
        
        'default': f"{course_name} is a comprehensive course designed to build strong foundational knowledge in this important area. This subject covers {len(modules)} key modules that progressively develop your understanding. You'll gain both theoretical insights and practical skills through lectures and assignments. The course prepares you for advanced studies and professional applications. Mastering this subject will significantly contribute to your academic and career success."
    }
    
    return summaries.get(course_code, summaries['default'])

def process_semester(sem_file):
    """Process one semester JSON file and generate simplified explanations"""
    
    with open(sem_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    semester = data['semester']
    subjects = data['subjects']
    
    sem_num = sem_file.stem.split('_')[1]
    output_dir = SEM_EXPLAIN_DIR / f"sem_0{sem_num}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"📚 Processing {semester}")
    print(f"{'='*70}")
    print(f"✓ Found {len(subjects)} subjects")
    
    for idx, subject in enumerate(subjects, 1):
        course_code = subject['course_code']
        course_name = subject['course_name']
        modules = subject['modules']
        books = subject.get('recommended_books', [])
        
        print(f"  [{idx}/{len(subjects)}] {course_code} - {course_name}")
        
        # Generate module list
        module_list = []
        for module in modules:
            module_list.append({
                "module_number": module['module_number'],
                "title": module['title']
            })
        
        # Generate 5-sentence summary
        summary = generate_5_sentence_summary(course_name, course_code, modules)
        
        # Create output JSON
        output_data = {
            "course_code": course_code,
            "course_name": course_name,
            "modules": module_list,
            "summary": summary,
            "recommended_books": books,
            "course_outcomes": [],  # Placeholder for later
            "prerequisites": []  # Placeholder for later
        }
        
        # Save to file
        output_file = output_dir / f"{course_code}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"      ✓ Saved {output_file.name}")
    
    print(f"✅ Completed {semester}\n")
    return len(subjects)

def main():
    """Main execution function"""
    
    print("="*70)
    print("Simple Course Explanation Generator")
    print("Generating module lists with 5-sentence summaries")
    print("="*70)
    
    sem_files = sorted(SEM_JSON_DIR.glob("sem_*.json"))
    
    if not sem_files:
        print("❌ No semester JSON files found!")
        return
    
    total_subjects = 0
    
    for sem_file in sem_files:
        count = process_semester(sem_file)
        total_subjects += count
    
    print("="*70)
    print(f"✅ Successfully generated explanations for {total_subjects} subjects!")
    print("="*70)
    print(f"\n📁 All explanations saved to: {SEM_EXPLAIN_DIR}")
    print("\n✅ Ready! Now updating frontend...")

if __name__ == "__main__":
    main()
