"""
Context Extraction - Smart extraction of relevant information from documents
Reduces context size and improves answer accuracy
"""
import json
import re


def extract_faculty_info(query, docs):
    """
    Extract specific faculty information from documents based on the query.
    This prevents sending entire faculty databases to the LLM.
    """
    query_lower = query.lower()
    
    # Check if asking about HOD
    is_hod_query = any(term in query_lower for term in ["hod", "head of department", "head of dept"])
    
    # Check if asking about a specific person
    # Extract potential names (capitalized words that aren't common words)
    name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    potential_names = re.findall(name_pattern, query)
    
    extracted_info = []
    found_specific = False
    
    for doc_text in docs:
        try:
            # Check if doc is already parsed (string format) or raw JSON
            if isinstance(doc_text, str) and doc_text.strip().startswith('{'):
                data = json.loads(doc_text)
            elif isinstance(doc_text, str):
                # Already parsed, return as-is but check if it's faculty info
                if "DEPARTMENT:" in doc_text or "Faculty Member:" in doc_text:
                    # Parse the already-formatted text to extract only what we need
                    if is_hod_query and "HOD" in doc_text:
                        lines = doc_text.split("\n")
                        current_faculty = []
                        in_hod_section = False
                        
                        for line in lines:
                            if "Faculty Member:" in line:
                                if current_faculty and in_hod_section:
                                    extracted_info.append("\n".join(current_faculty))
                                    found_specific = True
                                    break
                                current_faculty = [line]
                                in_hod_section = False
                            elif "Position:" in line and "HOD" in line:
                                in_hod_section = True
                                current_faculty.append(line)
                            elif current_faculty:
                                current_faculty.append(line)
                                if line.strip() == "":
                                    if in_hod_section:
                                        extracted_info.append("\n".join(current_faculty))
                                        found_specific = True
                                        break
                                    current_faculty = []
                    
                    elif potential_names:
                        for name in potential_names:
                            if name.lower() in doc_text.lower():
                                # Extract just this faculty member's section
                                lines = doc_text.split("\n")
                                current_section = []
                                capture = False
                                
                                for line in lines:
                                    if f"Faculty Member: {name}" in line or name in line:
                                        capture = True
                                        current_section.append(line)
                                    elif capture:
                                        if line.startswith("============================================================"):
                                            if len(current_section) > 1:
                                                current_section.append(line)
                                                break
                                        current_section.append(line)
                                
                                if current_section:
                                    extracted_info.append("\n".join(current_section))
                                    found_specific = True
                                    break
                
                if found_specific:
                    break
                continue
            else:
                data = doc_text
            
            if "faculty" not in data:
                continue
            
            department = data.get("department", "Unknown Department")
            
            # If asking about HOD
            if is_hod_query:
                for faculty_id, info in data["faculty"].items():
                    position = info.get("position", "").lower()
                    if "hod" in position or "head" in position:
                        extracted_info.append(format_faculty_member(info, department))
                        found_specific = True
                        break
            
            # If asking about specific person
            elif potential_names:
                for name in potential_names:
                    for faculty_id, info in data["faculty"].items():
                        faculty_name = info.get("name", "")
                        if name.lower() in faculty_name.lower():
                            extracted_info.append(format_faculty_member(info, department))
                            found_specific = True
                            break
                    if found_specific:
                        break
            
            if found_specific:
                break
        
        except (json.JSONDecodeError, TypeError):
            continue
    
    # If we found specific info, return only that
    if extracted_info:
        return extracted_info[:1]  # Return only the first match
    
    # Otherwise return empty (let the original docs through)
    return []


def format_faculty_member(info, department):
    """Format a single faculty member's information"""
    parts = [
        "="*60,
        f"Faculty Member: {info.get('name', 'Unknown')}",
        "="*60,
        f"Department: {department}",
        f"Position: {info.get('position', 'Not specified')}",
        f"Qualification: {info.get('qualification', 'Not specified')}"
    ]
    
    if "research_area" in info:
        if isinstance(info["research_area"], list):
            parts.append(f"Research Areas: {', '.join(info['research_area'])}")
        else:
            parts.append(f"Research Areas: {info['research_area']}")
    
    if "email" in info:
        parts.append(f"Email: {info['email']}")
    
    if "phone" in info:
        parts.append(f"Phone: {info['phone']}")
    
    return "\n".join(parts)


def extract_relevant_context(query, docs):
    """
    Main extraction function - intelligently extracts relevant context
    based on query type to reduce token usage and improve accuracy
    """
    query_lower = query.lower()
    
    # Faculty/HOD queries
    if any(term in query_lower for term in ["hod", "faculty", "professor", "teacher", "dr."]):
        extracted = extract_faculty_info(query, docs)
        if extracted:
            return extracted
    
    # For other queries, return the docs as-is
    return docs
