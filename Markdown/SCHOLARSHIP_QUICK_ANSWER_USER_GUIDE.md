# Scholarship Quick Answer - User Guide

## How It Works

When users ask about scholarships in the chatbot, the system will:

1. **Match keywords** from their query with scholarship data
2. **Display intro text** with brief scholarship information
3. **Provide a clickable link** to the scholarship portal
4. **Auto-scroll and highlight** the specific scholarship on the page

## Example Conversations

### Example 1: Post Matric Scholarship
**User**: "tell me about post matric scholarship"

**Bot Response**:
```
For minority students studying after Class 10. Helps cover tuition and academic 
expenses. Focuses on financially weaker families. Encourages continuation of 
higher education. Reduces dropout rates. Easy to understand eligibility. 
Widely used across West Bengal.

Please go through our scholarship portal for more details.
🔗 View Post Matric Scholarship (Minority) Details →
```

Click the link → Opens `/scholarship?highlight=post-matric-minority` with the card highlighted

---

### Example 2: MCM Scholarship
**User**: "mcm scholarship details"

**Bot Response**:
```
For minority students in professional courses. Supports Engineering, Medical, 
Law and Management. Rewards good academic performance. Helps students from 
low-income families. Reduces financial burden of higher education. Encourages 
merit-based growth.

Please go through our scholarship portal for more details.
🔗 View Merit Cum Means Scholarship (MCM) Details →
```

---

### Example 3: General Query
**User**: "what is aikyashree?"

**Bot Response**:
```
For minority students studying after Class 10. Helps cover tuition and academic 
expenses. Focuses on financially weaker families...

Please go through our scholarship portal for more details.
🔗 View Post Matric Scholarship (Minority) Details →
```

---

## Supported Keywords

Try asking about these scholarships:

### State Scholarships (West Bengal)
- "post matric" / "aikyashree" / "wb post matric"
- "mcm" / "merit cum means"
- "svmcm" / "vivekananda scholarship"
- "nabanna" / "cm relief fund"
- "kanyashree" / "k2 scholarship"
- "sc st obc scholarship"

### Central Government
- "central sector scholarship"
- "ishan uday" / "ner scholarship"
- "disability scholarship" / "pwd post matric"
- "beedi scholarship" / "cine workers"

### Private & Corporate
- "virtusa scholarship"
- "reliance foundation"

---

## What Happens When You Click the Link?

1. **Page Opens**: Scholarship portal loads at `/scholarship`
2. **Auto-Scroll**: Page automatically scrolls to the matched scholarship card
3. **Visual Highlight**: 
   - Blue border appears (3px solid #2563eb)
   - Pulsing animation for 2 seconds
   - Glowing shadow effect
4. **Auto-Remove**: Highlight fades after 5 seconds
5. **Navigate**: You can click the card to see full details

---

## Technical Details for Developers

### URL Format
```
/scholarship?highlight={scholarship_slug}
```

### URL Examples
- `/scholarship?highlight=post-matric-minority`
- `/scholarship?highlight=mcm-scholarship`
- `/scholarship?highlight=svmcm`
- `/scholarship?highlight=kanyashree`

### Response Format (API)
```json
{
  "intent": "scholarship",
  "response": "Intro text...\n\nPlease go through our...",
  "scholarship_slug": "post-matric-minority",
  "scholarship_name": "Post Matric Scholarship (Minority)",
  "has_scholarship_link": true
}
```

---

## Troubleshooting

### Issue: Keyword doesn't match
**Solution**: Add the keyword to `scholarship_quick_ans.json` in the `keywords` array

### Issue: Wrong scholarship highlighted
**Solution**: Check the `SCHOLARSHIP_ID_TO_SLUG` mapping in `app/core/scholarship_matcher.py`

### Issue: Highlight doesn't show
**Solution**: Verify the slug in the URL matches the `onclick` attribute in sc_index.html cards

### Issue: Page doesn't scroll
**Solution**: Check browser console for JavaScript errors in app.js

---

## Adding New Scholarships

To add a new scholarship to the quick answer system:

1. **Add to scholarship_quick_ans.json**:
```json
{
  "scholarship_id": "NEW_SCHOLARSHIP_ID",
  "scholarship_name": "New Scholarship Name",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "intro": "Brief introduction text here..."
}
```

2. **Add mapping in scholarship_matcher.py**:
```python
SCHOLARSHIP_ID_TO_SLUG = {
    "NEW_SCHOLARSHIP_ID": "new-scholarship-slug",
    # ... other mappings
}
```

3. **Ensure scholarship exists in scholarships.py** with matching slug

4. **Test with test_scholarship_matcher.py**

---

## Testing

Run the test script:
```bash
python test_scholarship_matcher.py
```

This will verify all keywords match correctly.

---

## Notes

- System uses **logical keyword matching** (no AI)
- **Case insensitive** matching
- **Partial matches** work (e.g., "vivekananda" matches "vivekananda scholarship")
- **First match wins** if multiple scholarships share keywords
- Falls back to **normal AI response** if no match found
