# University Rules & Policies Knowledge Base

## Overview
This folder contains comprehensive university rules and policies for Brainware University, organized into 13 categories. The AI chatbot has full access to all these rules and can answer questions about university policies, regulations, and student conduct.

## Rule Categories

### 1. **University Vision & Mission**
- University's vision and mission statements
- Core values and objectives
- Educational philosophy

### 2. **Admissions & Eligibility**
- Admission criteria and procedures
- Eligibility requirements for different programs
- Reservation policies
- Placement eligibility criteria
- Examination eligibility

### 3. **Finance & Scholarships**
- Fee structures and payment policies
- Scholarship information
- Financial aid options
- Refund policies

### 4. **Attendance & Examinations**
- Minimum attendance requirements (75% general, 80% for Pharmaceutical, 100% for Nursing)
- Attendance concessions
- Examination rules and regulations
- Assessment criteria (CIA: 40%, TEE: 60%)
- Passing requirements (≥40% in both CIA and TEE)

### 5. **Campus Rules & Facilities**
- University timings (8:00 AM - 7:00 PM, Mon-Sat)
- ID card requirements and penalties for loss
- Dress code and uniform policies
- Mobile phone and laptop restrictions
- Canteen rules and etiquette
- General campus conduct

### 6. **Conduct & Discipline**
- Code of conduct
- Prohibited acts and violations
- Disciplinary sanctions and penalties
- Fines (ranging from INR 100 to INR 25,000)
- Suspension and expulsion policies
- Anti-ragging policies

### 7. **Social Media & Communication**
- Social media usage guidelines
- Official communication channels
- Photography and publication rules
- Online behavior expectations

### 8. **Laboratories & Safety**
- Laboratory rules and safety protocols
- Equipment usage guidelines
- Safety equipment requirements (lab coats, shoes, etc.)
- Accident reporting procedures

### 9. **Co-curricular & Outreach**
- Extra-curricular activities
- Student clubs and organizations
- Community service requirements
- Event participation rules

### 10. **Health & Counselling**
- Health services available
- Counselling services
- Medical emergency procedures
- Mental health support

### 11. **Library & Reading Room**
- Library membership and access
- Borrowing limits (4 books for 15 days for UG/PG)
- Overdue fines (INR 5 per book per day)
- Library conduct rules
- Silent zone policies
- Computer usage guidelines

### 12. **Legal & Jurisdiction**
- University jurisdiction
- Legal frameworks
- Dispute resolution procedures
- Governing laws

### 13. **Other Rules**
- Miscellaneous regulations
- Special circumstances
- Additional policies

## File Structure

Each category has two files:
- **`.json`** - Main rules file in JSON format (array of rule objects)
- **`.jsonl`** - JSONL format (one JSON object per line)

### Rule Object Structure
```json
{
  "id": "unique_id",
  "section": "Category/Section Name",
  "title": "Short rule title",
  "text": "Detailed rule description",
  "source": "student-rule-book-2025-26.pdf",
  "page": "page_number(s)"
}
```

## How the AI Uses These Rules

### 1. **Automatic Loading**
- All university rules are loaded into memory when the chatbot starts
- Rules are indexed and organized by category for quick access
- The AI has immediate access to all ~24+ rules across 13 categories

### 2. **Intelligent Retrieval**
- When users ask rule-related questions, the AI:
  - Detects rule-related keywords (policy, allowed, prohibited, fine, etc.)
  - Searches relevant rule categories
  - Retrieves the most applicable rules
  - Provides specific answers with penalties/consequences

### 3. **Enhanced Search**
- Rule files get 3x priority boost for rule-related queries
- Keyword matching across title, text, and section fields
- Context-aware filtering based on query intent

## Example Queries the AI Can Handle

### General Rules
- "What are the university timings?"
- "What is the dress code policy?"
- "Can I use my mobile phone in the library?"
- "What happens if I lose my ID card?"

### Attendance & Exams
- "What is the minimum attendance required?"
- "What are the attendance concessions?"
- "How are exams graded?"
- "What percentage do I need to pass?"

### Discipline & Penalties
- "What items are banned on campus?"
- "What are the penalties for smoking on campus?"
- "What happens if I'm caught with alcohol?"
- "What are the fines for dress code violations?"

### Library
- "How many books can I borrow?"
- "What is the overdue fine for library books?"
- "What are the library rules?"
- "Can I eat in the library?"

### Facilities
- "What are the canteen rules?"
- "What are the laboratory safety requirements?"
- "Can I bring my laptop to class?"

## API Endpoints

### Get All Rules
```
GET /api/university-rules
```
Returns all university rules organized by category with statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_categories": 13,
    "total_rules": 24,
    "categories": {
      "Admissions & Eligibility": {
        "count": 4,
        "rules": [...]
      },
      ...
    }
  }
}
```

### Search Rules
```
POST /api/university-rules/search
Content-Type: application/json

{
  "query": "attendance"
}
```
Returns all rules matching the search query.

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "attendance",
    "count": 2,
    "rules": [
      {
        "category": "Attendance & Examinations",
        "id": "6",
        "section": "Attendance Policy",
        "title": "Minimum attendance & concessions",
        "text": "Minimum attendance 75%...",
        "source": "student-rule-book-2025-26.pdf",
        "page": "12"
      }
    ]
  }
}
```

## Integration with Chat System

The university rules are integrated into the chat system through:

1. **Global Context**: Rules are included in the system prompt as a dedicated section
2. **Query Enhancement**: Rule-related queries get special handling with boosted retrieval
3. **Contextual Filtering**: AI filters and presents only relevant rules based on the question
4. **Source Citation**: AI cites specific rule categories and sections when answering

## Updating Rules

To add or update rules:

1. Edit the appropriate JSON file in this folder
2. Follow the existing structure (id, section, title, text, source, page)
3. Restart the application to reload the rules
4. Test with sample queries

## Best Practices

### For Users
- Be specific in your questions (e.g., "library borrowing limit" vs "library rules")
- Ask about penalties/fines when relevant
- Request summaries for broad topics

### For Administrators
- Keep rules up-to-date with official handbooks
- Use clear, concise language in rule descriptions
- Include specific penalties and fines in the text
- Reference source documents and page numbers
- Organize rules logically by section

## Source Document
All rules are extracted from: **student-rule-book-2025-26.pdf**

## Statistics
- **Total Categories**: 13
- **Total Rules**: 24+
- **Coverage**: Comprehensive university policies and regulations
- **Update Frequency**: As per official handbook updates

## Notes
- Rules are stored in both `.json` (for easy editing) and `.jsonl` (for ML/AI processing)
- The `index_by_class.json` file contains metadata about all rule categories
- All rules include source attribution and page references
- The AI provides factual information only - for official matters, always consult the university administration

## Support
For questions about:
- **Rule content**: Contact University Administration
- **Technical issues**: Contact IT Support
- **AI responses**: Check logs and knowledge base
