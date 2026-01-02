# Troubleshooting Guide - Scholarship Link Not Showing

## The Issue
The scholarship page link is not being added to the chatbot response.

## Debug Steps Added

I've added debug logging to help identify the issue:

### Backend Logging (new_app.py)
The server will now print:
```
[DEBUG] Scholarship intent detected for query: {query}
[DEBUG] Matched scholarship: {matched_scholarship}
[DEBUG] Scholarship response: {scholarship_response}
[DEBUG] Returning response: {response_data}
```

### Frontend Logging (templates/index.html)
The browser console will now show:
```
Chat response data: {data}
Has scholarship link: true/false
Scholarship slug: {slug}
Calling addMessageWithScholarshipLink/Calling regular addMessage
```

## How to Test

### Step 1: Restart the Server
```bash
# Stop the current server (Ctrl+C)
# Then restart:
python new_app.py
```

**Important**: The server MUST be restarted to pick up the backend changes!

### Step 2: Clear Browser Cache
1. Open your browser's Developer Tools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

OR simply use Ctrl+Shift+R (hard refresh)

### Step 3: Test with Query
1. Open http://localhost:8081/
2. Open browser console (F12 → Console tab)
3. Type in chat: "tell me about post matric scholarship"
4. Watch both:
   - **Server terminal** for backend logs
   - **Browser console** for frontend logs

## Expected Output

### In Server Terminal:
```
[DEBUG] Scholarship intent detected for query: tell me about post matric scholarship
[DEBUG] Matched scholarship: {'scholarship_id': '1-POST_MATRIC_SCHOLARS', ...}
[DEBUG] Scholarship response: ('For minority students...', 'post-matric-minority', 'Post Matric Scholarship (Minority)')
[DEBUG] Returning response: {'intent': 'scholarship', 'response': '...', 'scholarship_slug': 'post-matric-minority', ...}
```

### In Browser Console:
```
Chat response data: {intent: 'scholarship', response: '...', scholarship_slug: 'post-matric-minority', ...}
Has scholarship link: true
Scholarship slug: post-matric-minority
Calling addMessageWithScholarshipLink
```

### In Chat Window:
You should see:
```
For minority students studying after Class 10. Helps cover tuition and academic expenses...

Please go through our scholarship portal for more details.
🔗 View Post Matric Scholarship (Minority) Details →
[clickable blue button with arrow]
```

## Common Issues & Solutions

### Issue 1: No backend debug logs
**Problem**: Server not using updated code
**Solution**: 
- Stop server completely (Ctrl+C)
- Restart with `python new_app.py`

### Issue 2: "has_scholarship_link: false" in console
**Problem**: Backend not detecting scholarship
**Solutions**:
- Check if keyword exists in scholarship_quick_ans.json
- Verify intent detection in app/core/intent.py
- Check server logs for errors

### Issue 3: "has_scholarship_link: true" but no link shown
**Problem**: Frontend function not executing
**Solutions**:
- Check browser console for JavaScript errors
- Clear browser cache (Ctrl+Shift+R)
- Verify addMessageWithScholarshipLink function exists

### Issue 4: Link shows but doesn't highlight on page
**Problem**: JavaScript on scholarship page not working
**Solutions**:
- Check Scholarship/static/js/app.js is loaded
- Verify slug matches in URL and card onclick attribute
- Check browser console on scholarship page for errors

## Test Queries to Try

Once working, test these:
```
1. "tell me about post matric scholarship"
2. "what is aikyashree?"
3. "mcm scholarship"
4. "vivekananda scholarship"
5. "kanyashree details"
6. "virtusa scholarship"
```

## Verify Files Were Modified

Check these files have the changes:

1. **new_app.py** (line ~150):
   - Should have `print(f"[DEBUG] Scholarship intent detected...")` lines
   - Should import `match_scholarship, get_scholarship_response`

2. **templates/index.html** (line ~2890):
   - Should have `console.log("Chat response data:", data);` lines
   - Should have `addMessageWithScholarshipLink` function (line ~2999)

3. **app/core/scholarship_matcher.py**:
   - Should exist with `match_scholarship()` and `get_scholarship_response()` functions

## Quick Verification Commands

```bash
# Test the matcher directly
python test_scholarship_matcher.py

# Check if files were modified
grep -n "has_scholarship_link" new_app.py
grep -n "addMessageWithScholarshipLink" templates/index.html
```

## Next Steps

1. **Restart server** ← MOST IMPORTANT
2. **Clear browser cache**
3. **Test with "tell me about post matric scholarship"**
4. **Check logs in both terminal and browser console**
5. **Report what you see in the logs**

The debug logs will tell us exactly where the issue is!
