"""
Seed data script to populate database with demo content
"""
import sys
import os
# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal, init_db
from app.models import User, Subject, Tag, FAQ, PDFDocument, StudentQuery, Feedback, BotConfig
from app.auth import get_password_hash
from datetime import datetime, timedelta

def seed_database():
    """Populate database with demo data"""
    print("Initializing database...")
    init_db()
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(Feedback).delete()
        db.query(StudentQuery).delete()
        db.query(FAQ).delete()
        db.query(PDFDocument).delete()
        db.query(Tag).delete()
        db.query(Subject).delete()
        db.query(BotConfig).delete()
        db.query(User).delete()
        db.commit()
        
        print("Creating users...")
        # Create admin
        admin = User(
            name="Dr. Shivnath Ghosh",
            email="admin@college.edu",
            password_hash=get_password_hash("admin123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        
        print("Creating subjects...")
        # Create subjects
        subjects = [
            Subject(
                code="CS101",
                name="Introduction to Computer Science",
                semester=1,
                department="Computer Science",
                course_outcomes=[
                    "Understand basic programming concepts",
                    "Write simple programs in Python",
                    "Apply problem-solving techniques"
                ],
                prerequisites=[],
                books=[
                    {"title": "Python Programming", "author": "John Zelle", "url": ""},
                ],
                modules=[
                    {"number": 1, "title": "Introduction to Programming", "description": "Basic concepts"},
                    {"number": 2, "title": "Data Types and Variables", "description": "Working with data"}
                ],
                internal_exam_info={"structure": "2 tests + assignments", "marks": 40}
            ),
            Subject(
                code="CS201",
                name="Data Structures and Algorithms",
                semester=3,
                department="Computer Science",
                course_outcomes=[
                    "Understand fundamental data structures",
                    "Analyze algorithm complexity",
                    "Implement efficient algorithms"
                ],
                prerequisites=["CS101"],
                books=[
                    {"title": "Introduction to Algorithms", "author": "CLRS", "url": ""},
                ],
                modules=[
                    {"number": 1, "title": "Arrays and Linked Lists", "description": "Linear data structures"},
                    {"number": 2, "title": "Trees and Graphs", "description": "Hierarchical structures"}
                ],
                internal_exam_info={"structure": "2 tests + coding assignments", "marks": 40}
            ),
            Subject(
                code="MATH101",
                name="Calculus I",
                semester=1,
                department="Mathematics",
                course_outcomes=[
                    "Understand limits and continuity",
                    "Master differentiation techniques",
                    "Solve integration problems"
                ],
                prerequisites=[],
                books=[
                    {"title": "Calculus", "author": "James Stewart", "url": ""},
                ],
                modules=[
                    {"number": 1, "title": "Limits and Continuity", "description": "Foundation concepts"},
                    {"number": 2, "title": "Derivatives", "description": "Differentiation techniques"}
                ],
                internal_exam_info={"structure": "2 tests", "marks": 40}
            )
        ]
        
        for subject in subjects:
            db.add(subject)
        db.commit()
        
        print("Creating tags...")
        # Create tags
        tags = [
            Tag(name="admissions"),
            Tag(name="exams"),
            Tag(name="programming"),
            Tag(name="mathematics"),
            Tag(name="assignments"),
            Tag(name="syllabus"),
            Tag(name="fees"),
            Tag(name="schedule")
        ]
        
        for tag in tags:
            db.add(tag)
        db.commit()
        
        print("Creating FAQs...")
        # Create FAQs
        faqs = [
            FAQ(
                question="What are the prerequisites for CS201?",
                answer="CS101 (Introduction to Computer Science) is the prerequisite for CS201. You should have a good understanding of basic programming concepts.",
                subject_id=subjects[1].id,
                created_by=admin.id,
                tags=[tags[2], tags[5]]
            ),
            FAQ(
                question="When is the final exam for CS101?",
                answer="The final exam for CS101 is scheduled for the last week of the semester. Exact dates will be announced 2 weeks in advance.",
                subject_id=subjects[0].id,
                created_by=admin.id,
                tags=[tags[1]]
            ),
            FAQ(
                question="How many assignments are there in Data Structures?",
                answer="There are 4 programming assignments throughout the semester. Each assignment is worth 10% of your final grade.",
                subject_id=subjects[1].id,
                created_by=admin.id,
                tags=[tags[4]]
            ),
            FAQ(
                question="What programming language is used in CS101?",
                answer="We use Python 3.x for CS101. Make sure you have Python installed on your computer.",
                subject_id=subjects[0].id,
                created_by=admin.id,
                tags=[tags[2]]
            ),
            FAQ(
                question="What topics are covered in Calculus I?",
                answer="Calculus I covers limits, continuity, derivatives, applications of derivatives, and an introduction to integration.",
                subject_id=subjects[2].id,
                created_by=admin.id,
                tags=[tags[3], tags[5]]
            ),
            FAQ(
                question="How do I submit my programming assignments?",
                answer="Programming assignments should be submitted through the college portal before the deadline. Late submissions will incur a penalty.",
                subject_id=subjects[0].id,
                created_by=admin.id,
                tags=[tags[4], tags[2]]
            ),
            FAQ(
                question="What is the grading policy?",
                answer="Grading is based on: Internal exams (40%), Final exam (40%), Assignments (15%), and Attendance (5%).",
                subject_id=subjects[0].id,
                created_by=admin.id,
                tags=[tags[1]]
            ),
            FAQ(
                question="Are there any lab sessions for CS101?",
                answer="Yes, there are weekly 2-hour lab sessions where you'll practice programming concepts under supervision.",
                subject_id=subjects[0].id,
                created_by=admin.id,
                tags=[tags[7]]
            ),
            FAQ(
                question="What is the fee structure for the semester?",
                answer="The fee structure varies by program. Please contact the admissions office for detailed fee information.",
                subject_id=None,
                created_by=admin.id,
                tags=[tags[6], tags[0]]
            ),
            FAQ(
                question="How can I apply for admission?",
                answer="You can apply online through our website or visit the admissions office. The application period is from June to July.",
                subject_id=None,
                created_by=admin.id,
                tags=[tags[0]]
            )
        ]
        
        for faq in faqs:
            db.add(faq)
        db.commit()
        
        print("Creating sample student queries...")
        # Create sample queries with more data
        queries = [
            StudentQuery(
                student_identifier="student001",
                question_text="What is the deadline for CS101 Assignment 2?",
                bot_answer="The deadline for Assignment 2 is next Friday at 11:59 PM.",
                status="resolved",
                subject_id=subjects[0].id,
                resolved_at=datetime.utcnow() - timedelta(days=2)
            ),
            StudentQuery(
                student_identifier="student002",
                question_text="I'm having trouble understanding recursion. Can you help?",
                bot_answer="Recursion is when a function calls itself. I recommend checking the course materials on recursion.",
                status="in_progress",
                subject_id=subjects[1].id
            ),
            StudentQuery(
                student_identifier="student003",
                question_text="When will the class schedule be released?",
                bot_answer=None,
                status="new",
                subject_id=None
            ),
            StudentQuery(
                student_identifier="student004",
                question_text="How do I calculate the derivative of x^2?",
                bot_answer="The derivative of x^2 is 2x, using the power rule.",
                status="resolved",
                subject_id=subjects[2].id,
                resolved_at=datetime.utcnow() - timedelta(days=1)
            ),
            StudentQuery(
                student_identifier="student005",
                question_text="What books are recommended for Data Structures?",
                bot_answer="Introduction to Algorithms by CLRS is the main textbook.",
                status="resolved",
                subject_id=subjects[1].id,
                resolved_at=datetime.utcnow() - timedelta(days=3)
            ),
            StudentQuery(
                student_identifier="student006",
                question_text="Is there a lab session for CS101 this week?",
                bot_answer="Yes, the lab session is on Wednesday at 2 PM in Lab Room 301.",
                status="resolved",
                subject_id=subjects[0].id,
                resolved_at=datetime.utcnow() - timedelta(hours=5)
            ),
            StudentQuery(
                student_identifier="student007",
                question_text="What topics will be covered in the mid-term exam?",
                bot_answer="The mid-term will cover chapters 1-5, including loops, functions, and arrays.",
                status="resolved",
                subject_id=subjects[0].id,
                resolved_at=datetime.utcnow() - timedelta(hours=12)
            ),
            StudentQuery(
                student_identifier="student008",
                question_text="How can I access the library resources?",
                bot_answer=None,
                status="new",
                subject_id=None
            ),
            StudentQuery(
                student_identifier="student009",
                question_text="What is the grading policy for CS201?",
                bot_answer="Grading is based on: 30% assignments, 20% quizzes, 50% exams.",
                status="resolved",
                subject_id=subjects[1].id,
                resolved_at=datetime.utcnow() - timedelta(days=1)
            ),
            StudentQuery(
                student_identifier="student010",
                question_text="Can I submit my assignment late with a penalty?",
                bot_answer=None,
                status="in_progress",
                subject_id=subjects[0].id
            ),
            StudentQuery(
                student_identifier="student011",
                question_text="What are the prerequisites for taking CS201?",
                bot_answer="You need to complete CS101 with a grade of C or better.",
                status="resolved",
                subject_id=subjects[1].id,
                resolved_at=datetime.utcnow() - timedelta(days=4)
            ),
            StudentQuery(
                student_identifier="student012",
                question_text="Where can I find the lecture slides?",
                bot_answer=None,
                status="new",
                subject_id=subjects[0].id
            ),
            StudentQuery(
                student_identifier="student013",
                question_text="Is there any extra credit opportunity?",
                bot_answer="Yes, you can participate in the coding competition for extra credit.",
                status="resolved",
                subject_id=subjects[1].id,
                resolved_at=datetime.utcnow() - timedelta(hours=8)
            ),
            StudentQuery(
                student_identifier="student014",
                question_text="What is the formula for integration by parts?",
                bot_answer="∫u dv = uv - ∫v du, where u and v are functions of x.",
                status="resolved",
                subject_id=subjects[2].id,
                resolved_at=datetime.utcnow() - timedelta(days=2)
            ),
            StudentQuery(
                student_identifier="student015",
                question_text="How do I reset my student portal password?",
                bot_answer=None,
                status="new",
                subject_id=None
            )
        ]
        
        for query in queries:
            db.add(query)
        db.commit()
        
        print("Creating feedback...")
        # Create more feedback entries
        feedbacks = [
            Feedback(
                query_id=queries[0].id,
                student_id="student001",
                comment="Very helpful, thank you!",
                helpful_bool=True,
                reviewed_bool=True
            ),
            Feedback(
                query_id=queries[1].id,
                student_id="student002",
                comment="Need more detailed explanation",
                helpful_bool=False,
                reviewed_bool=False
            ),
            Feedback(
                query_id=queries[3].id,
                student_id="student004",
                comment="Perfect answer!",
                helpful_bool=True,
                reviewed_bool=True
            ),
            Feedback(
                query_id=queries[4].id,
                student_id="student005",
                comment=None,
                helpful_bool=True,
                reviewed_bool=True
            ),
            Feedback(
                query_id=queries[5].id,
                student_id="student006",
                comment="Quick and accurate response.",
                helpful_bool=True,
                reviewed_bool=True
            ),
            Feedback(
                query_id=queries[6].id,
                student_id="student007",
                comment="This really helped me prepare!",
                helpful_bool=True,
                reviewed_bool=True
            ),
            Feedback(
                query_id=queries[8].id,
                student_id="student009",
                comment="Clear explanation of the policy.",
                helpful_bool=True,
                reviewed_bool=True
            ),
            Feedback(
                query_id=queries[10].id,
                student_id="student011",
                comment=None,
                helpful_bool=True,
                reviewed_bool=True
            ),
            Feedback(
                query_id=queries[12].id,
                student_id="student013",
                comment="Great to know about extra credit!",
                helpful_bool=True,
                reviewed_bool=False
            ),
            Feedback(
                query_id=queries[13].id,
                student_id="student014",
                comment="The formula was exactly what I needed.",
                helpful_bool=True,
                reviewed_bool=True
            )
        ]
        
        for feedback in feedbacks:
            db.add(feedback)
        db.commit()
        
        print("Creating bot config...")
        # Create bot configuration
        bot_config = BotConfig(
            greeting_message="Hello! I'm your college chatbot assistant. How can I help you today?",
            fallback_message="I'm sorry, I couldn't find an answer to your question. A teacher will get back to you soon. For urgent matters, please call +1-234-567-8900.",
            error_message="Oops! Something went wrong. Please try again later.",
            tone="academic",
            contact_phone="+1-234-567-8900"
        )
        db.add(bot_config)
        db.commit()
        
        print("\n" + "="*50)
        print("✓ Database seeded successfully!")
        print("="*50)
        print("\nDemo Account:")
        print("-" * 50)
        print("Admin:")
        print("  Email: admin@college.edu")
        print("  Password: admin123")
        print("="*50)
        print(f"\nCreated:")
        print(f"  - 1 user (admin)")
        print(f"  - 3 subjects")
        print(f"  - 8 tags")
        print(f"  - 10 FAQs")
        print(f"  - 15 sample queries")
        print(f"  - 10 feedback entries")
        print("="*50)
        
    except Exception as e:
        print(f"\nError seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
