# Notice System

## Overview

The notice system allows you to publish PDF notices that students can view through the chatbot's Academic section.

## How to Add Notices

### File Naming Convention

All PDF files must follow this naming pattern:

```
Category--Title--YYYY-MM-DD.pdf
```

**Examples:**

- `Academic--Mid Semester Exam Schedule--2025-03-15.pdf`
- `Examination--Final Exam Notification--2025-05-20.pdf`
- `Event--Annual Tech Fest--2025-04-10.pdf`
- `Holiday--Summer Break Notice--2025-06-01.pdf`
- `Important--Fee Payment Deadline--2025-03-01.pdf`
- `General--Library Hours Update--2025-02-28.pdf`

### Steps to Add a Notice

1. **Prepare your PDF file**

   - Ensure the PDF is properly formatted and readable
   - Keep file size reasonable (under 5MB recommended)

2. **Name the file correctly**

   - Follow the pattern: `Category--Title--YYYY-MM-DD.pdf`
   - Use double dashes (`--`) as separators
   - Date format must be: YYYY-MM-DD (e.g., 2025-03-15)

3. **Upload the file**
   - Copy the PDF file to: `notice/pdfs/`
   - The file will automatically appear in the student interface

### Available Categories

- **Academic** - Course-related announcements
- **Examination** - Exam schedules, results, forms
- **Event** - College events, fests, competitions
- **Holiday** - Holiday notifications, calendar updates
- **Important** - Critical announcements requiring immediate attention
- **General** - Other general notices

### Student Interface Features

Students can:

- **Search** notices by title
- **Filter** by category
- **Filter** by date (specific date, month, or year)
- **Sort** by newest/oldest or view last 7 days
- **Click** to open and view the PDF

### Directory Structure

```
notice/
├── pdfs/                          # Place all notice PDFs here
│   ├── Academic--Exam Notice--2025-03-15.pdf
│   ├── Event--Tech Fest--2025-04-10.pdf
│   └── ...
└── README.md                      # This file
```

### Important Notes

1. **File names are case-sensitive**
2. **Use only alphanumeric characters, spaces, and hyphens in titles**
3. **Date must be valid (YYYY-MM-DD format)**
4. **Category must match one of the predefined categories**
5. **Files appear immediately - no restart required**

### Troubleshooting

**Notice not appearing?**

- Check file name follows the exact pattern
- Verify the PDF is in the `notice/pdfs/` directory
- Ensure date format is correct (YYYY-MM-DD)
- Category name must match exactly (case-sensitive)

**PDF won't open?**

- Verify the PDF file is not corrupted
- Check file permissions
- Ensure file size is reasonable

### Example Workflow

1. Create a notice PDF: `exam_schedule.pdf`
2. Rename it: `Examination--Mid Semester Exam Schedule--2025-03-15.pdf`
3. Copy to: `notice/pdfs/`
4. Students can now see and access it immediately!

---

**Last Updated:** January 2025
