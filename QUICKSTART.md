# Quick Start Guide - Integrated System

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Required packages installed (see requirements)

### Step 1: Start Student Chatbot

```bash
cd College_chatbot
python app.py
```

✅ Student chatbot will run on `http://localhost:8000`

### Step 2: Start Admin Panel

```bash
cd "Admin Panel"
python start.py
```

✅ Admin Panel will open automatically

- Backend: `http://localhost:8000` (or 8001 if modified)
- Frontend: `http://localhost:3000`

---

## 📢 Test Announcement Feature

### Create an Announcement (Admin)

1. Open `http://localhost:3000`
2. Login: `admin@college.edu` / `admin123`
3. Click **Announcements** in sidebar
4. Click **Create Announcement**
5. Fill in:
   ```
   Title: Welcome to New Semester!
   Body: Classes begin on January 20, 2025. Please check your schedules.
   Visible to Chatbot: ✓ (toggle ON)
   ```
6. Click **Save**

### View Announcement (Student)

1. Open `http://localhost:8000` (student chatbot)
2. Click the **chat button** (bottom right)
3. On welcome screen, click **"See Latest Notice"**
4. ✅ Your announcement should appear!

---

## 📊 Test Real-Time Analytics

### Generate Some Data (Student Side)

1. Open student chatbot `http://localhost:8000`
2. Click chat button
3. Click "Start Chatting"
4. Ask a few questions:
   - "What is the syllabus for semester 1?"
   - "Who are the faculty members?"
   - "When are the exams?"

### View Analytics (Admin Side)

1. Open Admin Panel `http://localhost:3000`
2. Go to **Dashboard**
3. Check the stats:
   - **Queries Today** - should show 3+
   - **Recent Activity** - should show your questions
4. Go to **Query Logs** to see detailed queries

---

## 🧪 Quick Tests

### Test 1: Announcement Creation → Student View

```
✓ Create announcement in admin panel
✓ Open student chatbot
✓ Click "See Latest Notice"
✓ Announcement appears with title and body
```

### Test 2: Student Query → Admin Logging

```
✓ Ask question in student chatbot
✓ Refresh admin panel dashboard
✓ "Queries Today" count increases
✓ Question appears in "Recent Activity"
✓ Question visible in "Query Logs" page
```

### Test 3: Real-Time Stats

```
✓ Note current "Queries Today" count in admin
✓ Ask 3 questions in student chatbot
✓ Refresh admin dashboard
✓ Count increases by 3
```

---

## 🔍 Troubleshooting

### Announcements Not Showing

```bash
# Check if announcement is published
# In admin panel: Announcements → Check "is_active" column
# Ensure "Visible to Chatbot" is ON
```

### Queries Not Logging

```bash
# Check database path in app.py
# Verify: Admin Panel/college_chatbot.db exists
# Check terminal for error messages
```

### Dashboard Shows 0 Stats

```bash
# Make sure student chatbot is running on port 8000
# Check environment variable STUDENT_CHATBOT_URL
# Try asking some questions first to generate data
```

---

## 📁 Important Files

### Student Chatbot

- `app.py` - Main application with integration
- `templates/index.html` - UI with announcements modal
- `Admin Panel/college_chatbot.db` - Shared database

### Admin Panel

- `Admin Panel/backend/app/routes/analytics.py` - Real-time stats
- `Admin Panel/frontend/dashboard.html` - Dashboard UI
- `Admin Panel/frontend/announcements.html` - Announcement management

---

## 🎯 Key Features

✅ **Announcements** - Create in admin, view in student chatbot
✅ **Query Logging** - All student questions logged automatically
✅ **Real-Time Analytics** - Dashboard shows actual usage data
✅ **Shared Database** - Both systems use same database
✅ **Responsive UI** - Works on all devices

---

## 💡 Tips

1. **Testing Announcements**: Create multiple announcements to see the list
2. **NEW Badge**: Announcements created within 3 days show "NEW" badge
3. **Attachments**: Add PDF links in attachments array
4. **Scheduling**: Leave publish date blank for immediate publish
5. **Analytics**: Stats update in real-time, refresh page to see latest

---

## 🆘 Need Help?

Check these documents:

- `INTEGRATION_GUIDE.md` - Detailed integration documentation
- `CHANGES_SUMMARY.md` - Complete list of changes made
- `Admin Panel/QUICKSTART.md` - Admin panel specific guide

---

**Ready to go!** 🎉
Start both systems and test the integration!
