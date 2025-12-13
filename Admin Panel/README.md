# College Chatbot - Teacher/Admin Panel

A production-quality web application for managing a college chatbot's knowledge base, handling student queries, and publishing announcements.

## Features

### ✅ Implemented Features

1. **Dashboard** - Real-time statistics and activity monitoring
2. **Knowledge Base Management** - FAQ and PDF document management with text extraction
3. **Announcements** - Create and schedule announcements with APScheduler
4. **Query Logs** - Comprehensive logging with filters and CSV export
5. **Feedback Review** - Student feedback analysis and KB correction
6. **Analytics** - Dashboard stats, trends, and insights
7. **Bot Configuration** - Customize chatbot messages and tone
8. **Role-Based Access** - Admin and Teacher roles with appropriate permissions
9. **PDF Text Extraction** - Automatic text extraction using pdfminer.six
10. **Full-Text Search** - Search across FAQs and PDF content
11. **Authentication** - JWT-based authentication with bcrypt password hashing
12. **File Upload Security** - Sanitized filenames and size validation

## Tech Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (python-jose) + bcrypt
- **PDF Processing**: PyPDF2 and pdfminer.six
- **Scheduling**: APScheduler
- **Validation**: Pydantic

### Frontend
- **Styling**: Tailwind CSS (CDN)
- **JavaScript**: Vanilla JS with Fetch API
- **No build tools** - Pure HTML/CSS/JS

## Project Structure

```
Admin Panel/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # Authentication utilities
│   │   ├── database.py          # Database configuration
│   │   ├── utils.py             # PDF extraction & utilities
│   │   ├── scheduler.py         # APScheduler configuration
│   │   └── routes/
│   │       ├── auth.py          # Auth endpoints
│   │       ├── kb.py            # Knowledge Base endpoints
│   │       ├── subjects.py      # Subject endpoints
│   │       ├── queries.py       # Query management
│   │       ├── announcements.py # Announcements
│   │       ├── analytics.py     # Analytics & logs
│   │       └── feedback.py      # Feedback & bot config
│   └── requirements.txt
├── frontend/
│   ├── index.html              # Login page
│   ├── dashboard.html          # Main dashboard
│   ├── kb.html                 # Knowledge Base
│   ├── announcements.html      # Announcements
│   ├── logs.html               # Query Logs
│   ├── feedback.html           # Feedback Review
│   ├── analytics.html          # Analytics
│   ├── settings.html           # Bot Settings
│   └── assets/
│       ├── js/
│       │   ├── api.js          # API client
│       │   └── utils.js        # Utility functions
│       └── css/
│           └── custom.css      # Custom styles
├── uploads/
│   ├── pdfs/                   # Uploaded PDF files
│   └── attachments/            # Query attachments
├── seed_data.py                # Database seeding script
└── README.md                   # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone/Download the repository

```powershell
cd "C:\Users\Seratul Mustakim\Downloads\College_chatbot\College_chatbot\Admin Panel"
```

### Step 2: Install Python dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### Step 3: Initialize and seed the database

```powershell
# Go back to project root
cd ..

# Run seed script
python seed_data.py
```

This creates:
- SQLite database (`college_chatbot.db`)
- 3 demo users (1 admin, 2 teachers)
- 8 tags
- 10 FAQs
- 5 sample queries with feedback

### Step 4: Start the backend server

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Step 5: Serve the frontend

Open a new PowerShell terminal:

```powershell
cd frontend
python -m http.server 3000
```

The frontend will be available at: `http://localhost:3000`

### Step 6: Login

Open your browser and go to `http://localhost:3000`

**Demo Account:**

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@college.edu | admin123 |

## Environment Variables

Create a `.env` file in the `backend` directory (optional):

```env
SECRET_KEY=your-secret-key-change-this-in-production-12345678
DATABASE_URL=sqlite:///./college_chatbot.db
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user
- `POST /api/auth/users` - Create user (admin only)
- `GET /api/auth/users` - List users (admin only)

### Knowledge Base
- `GET /api/kb/faqs` - List FAQs (with filters)
- `POST /api/kb/faqs` - Create FAQ
- `PUT /api/kb/faqs/{id}` - Update FAQ
- `DELETE /api/kb/faqs/{id}` - Delete FAQ
- `POST /api/kb/pdfs` - Upload PDF
- `GET /api/kb/pdfs` - List PDFs
- `GET /api/kb/pdfs/{id}` - Get PDF details
- `GET /api/kb/tags` - List tags
- `POST /api/kb/tags` - Create tag
- `GET /api/kb/search?q={query}` - Search KB

### Queries
- `GET /api/queries` - List queries (with filters)
- `GET /api/queries/{id}` - Get query details
- `POST /api/queries` - Create query (public)
- `POST /api/queries/{id}/reply` - Reply to query
- `PATCH /api/queries/{id}` - Update query status
- `GET /api/queries/stats/summary` - Get query statistics

### Announcements
- `GET /api/announcements/active` - Get active announcements (public)
- `GET /api/announcements` - List all announcements
- `POST /api/announcements` - Create announcement
- `PUT /api/announcements/{id}` - Update announcement
- `DELETE /api/announcements/{id}` - Delete announcement
- `POST /api/announcements/{id}/publish` - Manually publish

### Analytics
- `GET /api/analytics/dashboard` - Dashboard statistics
- `GET /api/analytics/confusing-questions` - Questions needing improvement
- `GET /api/analytics/improvement-trend` - Chatbot accuracy trend
- `GET /api/analytics/logs` - Query logs with filters
- `GET /api/analytics/export-logs` - Export logs as CSV

### Feedback & Config
- `GET /api/feedback` - List feedback
- `POST /api/feedback` - Submit feedback (public)
- `PATCH /api/feedback/{id}` - Mark feedback as reviewed
- `POST /api/feedback/{id}/fix-kb` - Update FAQ from feedback
- `GET /api/bot-config` - Get bot configuration (public)
- `PUT /api/bot-config` - Update bot configuration

## Example API Calls

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@college.edu", "password": "admin123"}'
```

### Create FAQ (with authentication)
```bash
curl -X POST "http://localhost:8000/api/kb/faqs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the exam schedule?",
    "answer": "Exams will be held from December 1-15.",
    "subject_id": 1,
    "tag_ids": [1, 2]
  }'
```

### Upload PDF
```bash
curl -X POST "http://localhost:8000/api/kb/pdfs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "subject_id=1" \
  -F 'tag_ids=[1,2]'
```

### Search Knowledge Base
```bash
curl "http://localhost:8000/api/kb/search?q=programming"
```

## Security Features

1. **Password Hashing**: bcrypt with automatic salt
2. **JWT Authentication**: Secure token-based auth with expiration
3. **Role-Based Access Control**: Admin and Teacher roles
4. **File Upload Validation**: 
   - Type checking (PDF only)
   - Size limit (20MB max)
   - Filename sanitization (prevents path traversal)
5. **HTML Sanitization**: Using bleach to prevent XSS
6. **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
7. **CORS Configuration**: Configurable allowed origins

## Testing

### Manual Testing

1. **Auth**: Login with each demo account
2. **KB**: Create, edit, delete FAQs and upload PDFs
3. **Queries**: Create queries and test manual responses
4. **Announcements**: Create immediate and scheduled announcements
5. **Search**: Test full-text search across FAQs and PDFs
6. **Analytics**: Check dashboard stats and trends

### Running Automated Tests (basic)

```powershell
cd backend
pytest
```

## Database Schema

Key tables:
- `users` - Admin and teacher accounts
- `tags` - Categorization tags
- `faqs` - Frequently asked questions
- `pdf_documents` - Uploaded PDFs with extracted text
- `student_queries` - Student questions from chatbot
- `manual_responses` - Teacher replies to queries
- `announcements` - Notices and announcements
- `feedback` - Student feedback on answers
- `bot_config` - Chatbot configuration
- `audit_logs` - KB edit history

## Production Deployment Considerations

1. **Use PostgreSQL** instead of SQLite for production
2. **Set strong SECRET_KEY** in environment variables
3. **Configure CORS** with specific allowed origins
4. **Use HTTPS** for all communications
5. **Set up proper logging** and monitoring
6. **Implement rate limiting** on critical endpoints
7. **Use a process manager** like Gunicorn + Supervisor
8. **Set up database backups**
9. **Use environment-specific configs**

## Troubleshooting

### Database errors
```powershell
# Delete and recreate database
rm college_chatbot.db
python seed_data.py
```

### Port already in use
```powershell
# Change ports in startup commands
# Backend: --port 8001
# Frontend: python -m http.server 3001
```

### CORS errors
- Check that frontend is accessing `http://localhost:8000`
- Verify CORS settings in `backend/app/main.py`

## Future Enhancements

- [ ] Real-time notifications using WebSockets
- [ ] Bulk import/export of FAQs via CSV/Excel
- [ ] Advanced analytics with Chart.js visualizations
- [ ] Email notifications for new queries
- [ ] Multi-language support
- [ ] Image upload support in FAQs
- [ ] Advanced search with filters and facets
- [ ] Auto-tagging using NLP

## License

MIT License - Feel free to use for educational purposes.

## Support

For questions or issues, please check:
1. API documentation at `http://localhost:8000/docs`
2. Server logs in the terminal
3. Browser console for frontend errors

---

**Built with ❤️ for College Chatbot System**
