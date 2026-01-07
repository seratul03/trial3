from pathlib import Path

BASE_RESOURCE_PATH = Path(
    r"C:\Users\Seratul Mustakim\Desktop\Ai saves\College_chatbot\Resources"
)

JSON_PATH = BASE_RESOURCE_PATH / "json"
PDF_PATH = BASE_RESOURCE_PATH / "pdf"

RESOURCE_MAP = {
    "faculty": [
        JSON_PATH / "brainware_cse_ai_faculty.json"
    ],

    "subject": [
        # subject code will be resolved dynamically
    ],

    "semester": [
        JSON_PATH / "sem1.json",
        JSON_PATH / "sem2.json",
        JSON_PATH / "sem3.json",
        JSON_PATH / "sem4.json",
        JSON_PATH / "sem5.json"
    ],

    "exam": [
        JSON_PATH / "exam.json",
        JSON_PATH / "attendance_and_examinations.json"
    ],

    "holiday": [
        JSON_PATH / "holiday.json"
    ],

    "rules": [
        JSON_PATH / "conduct_and_discipline.json",
        JSON_PATH / "campus_rules_and_facilities.json"
    ],

    "library": [
        JSON_PATH / "library_and_reading_room.json"
    ],

    "scholarship": [
        # handled separately by scholarship_matcher (already correct)
    ]
}
