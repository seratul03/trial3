"""
Document Parser - Converts JSON documents into human-readable text format
This ensures the LLM receives structured, parseable context instead of raw JSON
"""
import json
import re


def parse_faculty_document(data):
    """Parse faculty JSON into human-readable format"""
    if not isinstance(data, dict):
        return None
    
    if "faculty" not in data and "department" not in data:
        return None
    
    text_parts = []
    
    # Add department header
    if "department" in data:
        text_parts.append(f"DEPARTMENT: {data['department']}\n")
    
    # Parse each faculty member
    if "faculty" in data:
        for faculty_id, info in data["faculty"].items():
            text_parts.append("\n" + "="*60)
            text_parts.append(f"Faculty Member: {info.get('name', 'Unknown')}")
            text_parts.append("="*60)
            
            if "position" in info:
                text_parts.append(f"Position: {info['position']}")
            
            if "qualification" in info:
                text_parts.append(f"Qualification: {info['qualification']}")
            
            if "research_area" in info and isinstance(info["research_area"], list):
                text_parts.append(f"Research Areas: {', '.join(info['research_area'])}")
            
            if "email" in info:
                text_parts.append(f"Email: {info['email']}")
            
            if "phone" in info:
                text_parts.append(f"Phone: {info['phone']}")
    
    return "\n".join(text_parts)


def parse_scholarship_document(data):
    """Parse scholarship JSON into human-readable format"""
    if not isinstance(data, dict):
        return None
    
    # Check if this is a scholarship document
    has_scholarship_fields = any(k in data for k in [
        "scholarship_name", "scholarship_id", "scholarship_type",
        "offered_by", "eligibility", "benefits"
    ])
    
    if not has_scholarship_fields:
        return None
    
    text_parts = []
    
    text_parts.append("="*60)
    text_parts.append(f"SCHOLARSHIP: {data.get('scholarship_name', 'Unknown')}")
    text_parts.append("="*60)
    
    if "official_name" in data:
        text_parts.append(f"Official Name: {data['official_name']}")
    
    if "scholarship_type" in data:
        text_parts.append(f"Type: {data['scholarship_type']}")
    
    if "offered_by" in data:
        text_parts.append(f"Offered By: {data['offered_by']}")
    
    if "target_group" in data:
        text_parts.append(f"Target Group: {data['target_group']}")
    
    if "academic_level" in data:
        if isinstance(data["academic_level"], list):
            text_parts.append(f"Academic Level: {', '.join(data['academic_level'])}")
        else:
            text_parts.append(f"Academic Level: {data['academic_level']}")
    
    if "introduction" in data:
        text_parts.append(f"\nIntroduction:\n{data['introduction']}")
    
    if "eligibility" in data:
        text_parts.append(f"\nEligibility:\n{data['eligibility']}")
    
    if "benefits" in data:
        text_parts.append(f"\nBenefits:\n{data['benefits']}")
    
    if "application_process" in data:
        text_parts.append(f"\nApplication Process:\n{data['application_process']}")
    
    if "important_dates" in data:
        text_parts.append(f"\nImportant Dates:\n{data['important_dates']}")
    
    if "website" in data:
        text_parts.append(f"\nWebsite: {data['website']}")
    
    return "\n".join(text_parts)


def parse_holiday_document(data):
    """Parse holiday JSON into human-readable format"""
    if not isinstance(data, dict):
        return None
    
    # Check for holiday-specific fields
    if "_metadata" not in data or "holidays" not in data:
        return None
    
    text_parts = []
    
    if "_metadata" in data:
        meta = data["_metadata"]
        text_parts.append("="*60)
        text_parts.append(meta.get("title", "University Holiday Calendar"))
        text_parts.append("="*60)
        
        if "description" in meta:
            text_parts.append(f"\n{meta['description']}\n")
    
    if "holidays" in data:
        text_parts.append("\nHOLIDAY LIST:")
        text_parts.append("-"*60)
        
        for holiday in data["holidays"]:
            text_parts.append(f"\n• {holiday.get('name', 'Unknown Holiday')}")
            text_parts.append(f"  Date: {holiday.get('date', 'TBD')}")
            if "day" in holiday:
                text_parts.append(f"  Day: {holiday['day']}")
            if "type" in holiday:
                text_parts.append(f"  Type: {holiday['type']}")
    
    return "\n".join(text_parts)


def parse_exam_document(data):
    """Parse exam JSON into human-readable format"""
    if not isinstance(data, dict):
        return None
    
    # Check for exam-specific fields
    has_exam_fields = any(k in data for k in ["exam_schedule", "examinations", "exam"])
    
    if not has_exam_fields:
        return None
    
    text_parts = []
    text_parts.append("="*60)
    text_parts.append("EXAMINATION INFORMATION")
    text_parts.append("="*60)
    
    # Handle different exam data structures
    for key, value in data.items():
        if isinstance(value, dict):
            text_parts.append(f"\n{key.upper().replace('_', ' ')}:")
            for subkey, subval in value.items():
                text_parts.append(f"  {subkey}: {subval}")
        elif isinstance(value, list):
            text_parts.append(f"\n{key.upper().replace('_', ' ')}:")
            for item in value:
                if isinstance(item, dict):
                    for k, v in item.items():
                        text_parts.append(f"  {k}: {v}")
                else:
                    text_parts.append(f"  • {item}")
        else:
            text_parts.append(f"{key}: {value}")
    
    return "\n".join(text_parts)


def parse_generic_document(data):
    """Parse generic JSON into readable key-value format"""
    if not isinstance(data, dict):
        return str(data)
    
    text_parts = []
    
    for key, value in data.items():
        if key.startswith("_"):
            continue
        
        formatted_key = key.replace("_", " ").title()
        
        if isinstance(value, dict):
            text_parts.append(f"\n{formatted_key}:")
            for subkey, subval in value.items():
                formatted_subkey = subkey.replace("_", " ").title()
                text_parts.append(f"  {formatted_subkey}: {subval}")
        elif isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], dict):
                text_parts.append(f"\n{formatted_key}:")
                for item in value:
                    for k, v in item.items():
                        text_parts.append(f"  {k}: {v}")
            else:
                text_parts.append(f"{formatted_key}: {', '.join(map(str, value))}")
        else:
            text_parts.append(f"{formatted_key}: {value}")
    
    return "\n".join(text_parts)


def parse_document(json_string):
    """
    Main parser function - converts JSON string to human-readable text
    Returns formatted text that the LLM can easily understand
    """
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError:
        return json_string  # Return as-is if not valid JSON
    
    # Try specialized parsers first
    parsers = [
        parse_faculty_document,
        parse_scholarship_document,
        parse_holiday_document,
        parse_exam_document
    ]
    
    for parser in parsers:
        result = parser(data)
        if result:
            return result
    
    # Fallback to generic parser
    return parse_generic_document(data)


def parse_documents(json_strings):
    """Parse multiple JSON documents"""
    return [parse_document(doc) for doc in json_strings]
