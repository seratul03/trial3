# Admin Panel & Student Chatbot Integration Guide

## Overview

The Admin Panel and Student Chatbot are now fully integrated. Announcements created in the admin panel appear in the student chatbot, and all student queries are logged to the admin panel database for real-time analytics.

## Features Integrated

### 1. **Announcements System**

- ✅ Create announcements in the Admin Panel
- ✅ Announcements automatically appear in the Student Chatbot
- ✅ Students can view latest announcements by clicking "See Latest Notice" on the welcome screen
- ✅ Support for scheduled announcements and attachments

### 2. **Student Query Logging**

- ✅ All student chat queries are logged to the Admin Panel database
- ✅ Track student questions, bot responses, and timestamps
- ✅ Queries appear in real-time in the Admin Panel

### 3. **Real-Time Analytics**

- ✅ Admin Panel dashboard shows real-time statistics from student chatbot
- ✅ Live tracking of:
  - Queries today
  - Pending queries
  - Total FAQs
  - Chatbot accuracy
  - Recent activity

### 4. **Notice System (PDF-Based)**

- ✅ Upload PDF notices to `notice/pdfs/` directory
- ✅ Automatic parsing of notice metadata from filename
- ✅ Students can access notices through Academic → Notice submenu
- ✅ Advanced filtering by category, date, and search
- ✅ Real-time updates - no restart required

## How to Use

### For Administrators

#### Creating an Announcement

1. Start both servers (see "Running the System" below)
2. Open the Admin Panel at `http://localhost:3000`
3. Log in with admin credentials (default: `admin@college.edu` / `admin123`)
4. Navigate to **Announcements** in the sidebar
5. Click **"Create Announcement"**
6. Fill in:
   - Title
   - Body (announcement message)
   - Visibility to Chatbot (toggle ON for students to see)
   - Schedule time (optional - leave blank for immediate publish)
   - Attachments (optional)
7. Click **Save**

The announcement will now appear in the student chatbot!

#### Viewing Student Queries

1. Go to **Query Logs** in the Admin Panel
2. See all student questions in real-time
3. Filter by date, status, or search
4. Reply to queries and optionally add them to the Knowledge Base

#### Checking Analytics

1. Go to **Dashboard** in the Admin Panel
2. View real-time statistics:
   - **Queries Today**: Total questions asked today
   - **Pending Queries**: Questions awaiting review
   - **Chatbot Accuracy**: Based on student feedback
   - **Recent Activity**: Last 10 queries

#### Managing PDF Notices

1. Navigate to `College_chatbot/notice/pdfs/` directory
2. Add PDF files following the naming convention:
   - Format: `Category--Title--YYYY-MM-DD.pdf`
   - Example: `Academic--Mid Semester Exam Schedule--2025-03-15.pdf`
3. Available categories:
   - Academic
   - Examination
   - Event
   - Holiday
   - Important
   - General
4. The notice will immediately appear in the student interface (no restart needed)

For detailed instructions, see `notice/README.md`

### For Students

#### Viewing Announcements

1. Open the chatbot by clicking the chat button
2. On the welcome screen, click **"See Latest Notice"**
3. View all active announcements from the administration
4. New announcements are marked with a "NEW" badge (within 3 days)

#### Viewing PDF Notices

1. Open the chatbot
2. Click on **Academic** button
3. Select **Notice** from the submenu
4. Use the search bar to find specific notices
5. Click **Filters** to:
   - Filter by category (Academic, Exam, Event, etc.)
   - Filter by date (specific date, month, or year)
   - Use quick filters (Newest, Oldest, Last 7 Days)
6. Click any notice card to view the PDF

#### Chatting with the Bot

- All your questions are automatically logged for improvement
- Admins can see your questions and provide better answers
- Your conversation helps improve the chatbot over time

## Running the System

### Start the Student Chatbot (Port 8000)

```bash
cd College_chatbot
python app.py
```

### Start the Admin Panel (Ports 3000 & 8000)

```bash
cd "Admin Panel"
python start.py
```

**Note**: The admin panel backend runs on port 8000 by default. If both are running on the same machine, you'll need to change the admin panel port in `Admin Panel/run_backend.py`:

```python
# Change port from 8000 to 8001 or another port
uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
```

And update the API_BASE_URL in `Admin Panel/frontend/assets/js/api.js`:

```javascript
const API_BASE_URL = "http://localhost:8001";
```

## Database Structure

Both systems share the same database (`Admin Panel/college_chatbot.db`):

### Key Tables

- **announcements**: Stores all announcements created by admins
- **student_queries**: Logs all student chat queries
- **faqs**: Knowledge base questions and answers
- **feedback**: Student feedback on bot responses
- **users**: Admin and teacher accounts

## API Endpoints

### Student Chatbot Endpoints

- `GET /api/announcements/active` - Get active announcements for students
- `GET /api/admin/stats` - Get real-time statistics for admin panel
- `POST /chat` - Process student queries (auto-logs to database)

### Admin Panel Endpoints

- `GET /api/announcements` - List all announcements
- `POST /api/announcements` - Create new announcement
- `GET /api/analytics/dashboard` - Get dashboard statistics
- `GET /api/queries` - List student queries
- `GET /api/analytics/logs` - Get detailed query logs

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Gemini AI Configuration
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent
GEMINI_API_KEY=your_api_key_here

# Student Chatbot URL (for admin panel to fetch stats)
STUDENT_CHATBOT_URL=http://localhost:8000

# Database
DATABASE_URL=sqlite:///./college_chatbot.db
```

## Troubleshooting

### Announcements not showing in student chatbot

- Check that "Visible to Chatbot" is enabled in admin panel
- Ensure announcement is published (not scheduled for future)
- Check browser console for errors

### Student queries not appearing in admin panel

- Verify database path is correct in `app.py`
- Check database file permissions
- Look for errors in terminal output

### Dashboard showing "local" data instead of "real-time"

- Ensure student chatbot is running on port 8000
- Check `STUDENT_CHATBOT_URL` environment variable
- Verify firewall/network allows localhost connections

## Technical Details

### Data Flow

```
Student Chatbot (app.py:8000)
    ↓ (query)
Database (college_chatbot.db)
    ↑ (announcements)
Admin Panel (backend:8001, frontend:3000)
```

1. Student asks question → Logged to `student_queries` table
2. Admin creates announcement → Saved to `announcements` table
3. Student opens chatbot → Fetches active announcements
4. Admin views dashboard → Fetches real-time stats from chatbot

### Security Considerations

- Admin panel uses JWT authentication
- Student chatbot is public (no auth required)
- Database connection uses SQLite (local file)
- CORS enabled for cross-origin requests

## Future Enhancements

- Real-time WebSocket notifications
- Student authentication system
- Advanced analytics and reporting
- Email notifications for announcements
- Multi-language support

## Support

For issues or questions, contact the development team.

---

**Last Updated**: 2025-01-24
