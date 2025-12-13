# Quick Start Guide - Notice System Testing

## Step 1: Add Sample PDF Notices

To test the notice system, you need to add PDF files to the `notice/pdfs/` directory.

### Create Sample PDFs (if needed)

You can use any PDF files you have, just rename them according to the pattern below.

### Naming Pattern:

```
Category--Title--YYYY-MM-DD.pdf
```

### Sample Filenames to Try:

1. `Academic--Mid Semester Examination Schedule--2025-03-15.pdf`
2. `Examination--Final Exam Form Fill-up Notice--2025-05-10.pdf`
3. `Event--Annual Technical Symposium 2025--2025-04-20.pdf`
4. `Important--Fee Payment Deadline Extended--2025-02-28.pdf`
5. `Holiday--Summer Vacation Notice--2025-06-01.pdf`
6. `General--Library Hours Update--2025-01-15.pdf`

## Step 2: Start the Chatbot

```bash
cd College_chatbot
python app.py
```

The server should start on `http://localhost:8000`

## Step 3: Test the Notice Interface

1. Open your browser and go to `http://localhost:8000`
2. Click the **chat button** to open the chatbot
3. Click **Academic** button in the modal
4. Click **Notice** in the submenu

### You should see:

- Search bar at the top
- Filter button
- List of all notices (if you added PDFs)
- Each notice showing:
  - Category badge (colored)
  - Date
  - Title

## Step 4: Test Features

### Test Search:

1. Type a keyword in the search bar
2. Notices should filter in real-time

### Test Category Filter:

1. Click the **Filters** button
2. Select a category from dropdown
3. Only notices of that category should show

### Test Date Filters:

1. Click **Filters**
2. Change "Date Mode" to:
   - **Specific Date** - Select exact date
   - **Month** - Select month
   - **Year** - Enter year
3. Notices should filter accordingly

### Test Quick Filters:

1. Click **Filters**
2. Try the quick filter buttons:
   - **Newest First** - Sorts newest to oldest
   - **Oldest First** - Sorts oldest to newest
   - **Last 7 Days** - Shows only recent notices

### Test PDF Opening:

1. Click on any notice card
2. PDF should open in a new browser tab

## Step 5: Verify API Endpoints

### Test Notices API:

Open in browser: `http://localhost:8000/api/notices`

You should see JSON response like:

```json
[
  {
    "category": "Academic",
    "title": "Mid Semester Examination Schedule",
    "date": "2025-03-15",
    "filename": "Academic--Mid Semester Examination Schedule--2025-03-15.pdf"
  }
]
```

### Test PDF Serving:

If you added a file: `Academic--Test Notice--2025-01-15.pdf`

Open: `http://localhost:8000/pdfs/Academic--Test Notice--2025-01-15.pdf`

The PDF should display or download.

## Troubleshooting

### No Notices Appearing?

**Check:**

1. PDFs are in `notice/pdfs/` directory
2. Filenames follow the exact pattern: `Category--Title--YYYY-MM-DD.pdf`
3. Categories match exactly (case-sensitive):
   - Academic
   - Examination
   - Event
   - Holiday
   - Important
   - General

### Filter Panel Not Showing?

- Click the **Filters** button next to the search bar
- Panel should slide down

### PDF Won't Open?

**Check:**

1. PDF file exists in `notice/pdfs/`
2. Filename in the notice card matches actual file
3. Browser allows pop-ups (may be blocked)

### Empty State?

If you see "No notices found":

- Add at least one PDF file to `notice/pdfs/`
- Refresh the page
- Make sure API returns data: `http://localhost:8000/api/notices`

## Expected Behavior

### Without PDF Files:

- Notice section loads
- Shows: "No notices found matching your filters."
- All controls work but no cards appear

### With PDF Files:

- Notice cards appear immediately
- Search filters cards in real-time
- Category filter works
- Date filters work
- Quick filters sort/filter correctly
- Clicking card opens PDF in new tab

## Development Notes

### Adding Notices While Server is Running:

1. Just copy PDF files to `notice/pdfs/`
2. Refresh the notice section (close and reopen Academic → Notice)
3. New notices appear immediately - no server restart needed!

### Removing Notices:

1. Delete PDF from `notice/pdfs/`
2. Refresh the notice section
3. Notice disappears immediately

### Real-Time Updates:

The system reads the directory on each API call, so:

- ✅ Add PDFs anytime
- ✅ Remove PDFs anytime
- ✅ Rename PDFs anytime
- ✅ No restart required
- ✅ Just refresh the notice section

## Sample Testing Script

```bash
# 1. Create test directory (if not exists)
mkdir -p "College_chatbot/notice/pdfs"

# 2. Add sample PDFs (you'll need actual PDF files)
# Copy any PDF and rename to these patterns:
# - Academic--Test Notice--2025-01-15.pdf
# - Event--Sample Event--2025-02-20.pdf

# 3. Start server
cd College_chatbot
python app.py

# 4. Test in browser
# Go to: http://localhost:8000
# Click: Chat → Academic → Notice
```

## Success Criteria

✅ Notice button appears in Academic modal
✅ Notice section loads without errors
✅ Search works
✅ Filters work
✅ PDFs open correctly
✅ Empty state handled
✅ Real-time updates work

---

**Ready to use! Add your PDFs and start testing!** 🚀
