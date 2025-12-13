# Quick Start Guide

## Get Your Admin Panel Running in 5 Minutes

### Step 1: Install Dependencies (1 minute)

Open PowerShell in the project directory:

```powershell
cd backend
pip install -r requirements.txt
```

### Step 2: Initialize Database (30 seconds)

```powershell
cd ..
python seed_data.py
```

You should see output like:
```
✓ Database seeded successfully!
Created:
  - 3 users (1 admin, 2 teachers)
  - 10 FAQs
  - 5 sample queries
```

### Step 3: Start Backend Server (30 seconds)

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal open. You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 4: Start Frontend Server (30 seconds)

Open a **new** PowerShell terminal:

```powershell
cd frontend
python -m http.server 3000
```

You should see:
```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

### Step 5: Open in Browser (10 seconds)

Open your browser and go to:
```
http://localhost:3000
```

### Step 6: Login

Use this demo account:

**Admin Account:**
- Email: `admin@college.edu`
- Password: `admin123`

---

## What to Test

### ✅ Dashboard
- View statistics (queries today, pending, accuracy)
- See recent activity
- Check most asked topics

### ✅ Knowledge Base
- Click "Knowledge Base" in sidebar
- **Create FAQ**: Click "+ Add FAQ", fill form, submit
- **Upload PDF**: Go to "PDF Documents" tab, click "+ Upload PDF"
- **Create Tags**: Go to "Tags" tab, add new tags
- **Search**: Use search box to find FAQs

### ✅ Settings
- Click "Settings" in sidebar
- Modify greeting, fallback, error messages
- Change contact phone number
- Select tone (formal/friendly/academic)
- Click "Save Configuration"

---

## API Documentation

While servers are running, visit:
```
http://localhost:8000/docs
```

This shows all API endpoints with:
- Request/response schemas
- Try-it-out functionality
- Authentication requirements

---

## Troubleshooting

### "Port already in use"
```powershell
# Use different ports
# Backend:
python -m uvicorn app.main:app --reload --port 8001

# Frontend:
python -m http.server 3001
```

### "Module not found"
```powershell
# Make sure you're in the backend directory
cd backend
pip install -r requirements.txt
```

### "Database errors"
```powershell
# Delete and recreate database
rm college_chatbot.db
python seed_data.py
```

### "Login not working"
- Check browser console (F12) for errors
- Verify backend is running on port 8000
- Check that API_BASE_URL in `frontend/assets/js/api.js` is correct

---

## Project Files Overview

```
Admin Panel/
├── backend/                  # Python FastAPI backend
│   ├── app/
│   │   ├── main.py          # Main application
│   │   ├── models.py        # Database models
│   │   ├── routes/          # API endpoints
│   │   └── ...
│   └── requirements.txt     # Python dependencies
│
├── frontend/                # HTML/CSS/JS frontend
│   ├── index.html          # Login page
│   ├── dashboard.html      # Dashboard
│   ├── kb.html             # Knowledge Base
│   ├── settings.html       # Bot Settings
│   └── assets/             # JavaScript and CSS
│
├── uploads/                # Uploaded files
│   ├── pdfs/              # PDF documents
│   └── attachments/       # Query attachments
│
├── seed_data.py           # Database seeding script
├── README.md              # Full documentation
└── QUICKSTART.md          # This file
```

---

## Next Steps

1. **Explore all pages**: Click through all sidebar links
2. **Test PDF upload**: Upload a real PDF and see text extraction
3. **Create FAQs**: Add your own FAQs with tags
4. **Check Analytics**: View the analytics page
5. **Read full README.md**: See all features and API endpoints

---

## Production Deployment

For production use:

1. Change `SECRET_KEY` in environment variables
2. Use PostgreSQL instead of SQLite
3. Set up proper CORS with specific origins
4. Use a production WSGI server (Gunicorn)
5. Enable HTTPS
6. Set up monitoring and logging

---

## Support

- **API Docs**: http://localhost:8000/docs
- **Full README**: See README.md in project root
- **Check logs**: Look at terminal output for errors

---

**Enjoy your Admin Panel! 🎉**
