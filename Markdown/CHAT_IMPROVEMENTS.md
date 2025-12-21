# Chat System Improvements - Knowledge Base Strict Mode

## Overview
Updated the chat system to STRICTLY answer only from the loaded JSON files in the project, not from the AI's general knowledge.

## Key Changes Made

### 1. Session Management & Conversation History
- Added per-session conversation history using cookies
- Session ID stored in `chat_session_id` cookie
- History maintained in-memory for up to 10 messages per session
- Enables context-aware responses

### 2. Text Sanitization
- Removes markdown artifacts (`**bold**`, `*italic*`, `` `code` ``)
- Strips control characters (except newlines/tabs)
- Cleans both user inputs and AI outputs

### 3. Knowledge Base Retrieval
- **retrieve_top_k()**: Performs keyword-based search across all loaded JSON files
- Returns top-K most relevant documents with snippets
- Scores documents by keyword frequency

### 4. Strict Context Building
- **build_context_from_docs()**: Creates rich context from JSON files
- Extracts specific fields:
  - Subject name, code, summary
  - Modules (first 3 shown)
  - Course outcomes count
  - Prerequisites count
- Always cites source file paths

### 5. Enhanced Chat Endpoint (`/chat`)
**Request Flow:**
1. Get/create session ID from cookie
2. Sanitize user input
3. Add message to session history
4. Retrieve relevant JSON documents (top-8)
5. Build comprehensive context from retrieved docs
6. Create strict prompt with instructions
7. Send to Gemini API (if configured)
8. Sanitize response
9. Return with source citations
10. Set session cookie

**Strict Instructions Sent to AI:**
```
You are a campus assistant for Brainware University, Department of Computer Science & Engineering (AI).

CRITICAL INSTRUCTIONS:
1. Answer STRICTLY using information from the provided JSON files only
2. DO NOT use your general knowledge or training data
3. If the answer is not in the provided context, say "I don't have this information in the knowledge base"
4. Always cite the source file when answering (e.g., [sem_explain/sem_01/BSCM101.json])
5. Keep answers concise and relevant to the user's question
6. Remember previous messages in this conversation
```

### 6. Fallback Behavior
If Gemini API is not configured or fails:
- Uses local `data.json` for simple keyword matching
- Still includes retrieved JSON snippets
- Returns sources in response

### 7. New Endpoint: `/clear-history`
- POST endpoint to clear chat history for current session
- Useful for testing or privacy

### 8. Frontend Update
- Chat now displays source files used for the answer
- Shows up to 3 source file paths below each response
- Format: `📚 Sources: sem_explain/sem_01/BSCM101.json, ...`

### 9. Updated `ai_prompt.txt`
Enhanced with strict rules:
- 10 critical instructions for the AI
- Explicit mapping of question types to JSON files
- Examples: subjects → sem_explain/, faculty → Faculty/brainware_cse_ai_faculty.json

## How It Works Now

### Example 1: Subject Query
**User:** "Tell me about BSCM101"

**Process:**
1. System searches all JSON files for "BSCM101"
2. Finds `sem_explain/sem_01/BSCM101.json`
3. Extracts: subject name, modules, summary, outcomes, prerequisites
4. Sends ONLY this information to AI with strict instructions
5. AI responds using only the provided JSON data
6. Response includes source citation

### Example 2: General Knowledge Question
**User:** "Tell me about Semiconductor Physics"

**Process:**
1. System searches all JSON files for "Semiconductor Physics"
2. If found in a subject file (e.g., as a module topic), extracts that content
3. If NOT found in any JSON file:
   - AI responds: "I don't have this information in the knowledge base"
4. AI will NOT use its general knowledge about semiconductors

## Files Modified

1. **app.py**
   - Added session management functions
   - Added sanitization function
   - Added retrieval functions
   - Completely rewrote `/chat` endpoint
   - Added `/clear-history` endpoint

2. **templates/index.html**
   - Updated sendMessage() to show source citations
   - Displays sources below bot responses

3. **ai_prompt.txt**
   - Enhanced with strict 10-point ruleset
   - Added file-to-topic mapping

## Testing

### Test the System:
1. Start server: `.\.venv\Scripts\python.exe app/app.py`
2. Open browser: http://127.0.0.1:8000
3. Try these queries:

**Should Work (Data in JSON files):**
- "Tell me about BSCM101"
- "What are the prerequisites for HSMCM101?"
- "List modules in PCC-CSM301"
- "Who are the faculty members?"
- "When is the next holiday?"

**Should Say "Not in Knowledge Base":**
- "Tell me about Semiconductor Physics" (unless it's in a subject JSON)
- "What is quantum computing?"
- "How does machine learning work?"

### Verify Sources:
Each response should show:
```
📚 Sources: sem_explain/sem_01/BSCM101.json
```

### Test Conversation Memory:
1. Ask: "Tell me about BSCM101"
2. Follow up: "What are its prerequisites?"
3. System should remember context from message 1

### Clear History:
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/clear-history -Method Post
```

## Configuration

### Required Environment Variables (.env):
```env
GEMINI_API_KEY=your_api_key_here
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent
```

### Optional Improvements:
1. **Semantic Search**: Replace keyword matching with embeddings (e.g., OpenAI embeddings, sentence-transformers)
2. **Persistent History**: Store chat history in database instead of memory
3. **Admin UI**: Add interface to view loaded files and refresh knowledge base
4. **Rate Limiting**: Add rate limits to prevent API abuse

## Benefits

✅ **Accuracy**: Answers come only from your verified JSON files
✅ **Transparency**: Every answer includes source citations
✅ **Consistency**: Same questions get same answers based on data
✅ **No Hallucination**: AI cannot make up information
✅ **Contextual**: Remembers conversation for follow-up questions
✅ **Clean Output**: No markdown artifacts or special characters
✅ **Verifiable**: Users can check source files themselves

## Limitations

⚠️ **Keyword-Based**: Current retrieval uses simple keyword matching (can miss paraphrases)
⚠️ **In-Memory**: Session history lost on server restart
⚠️ **API-Dependent**: Best performance requires Gemini API access
⚠️ **Static Knowledge**: Requires server restart to load new JSON files

## Next Steps

1. **Test thoroughly** with various queries
2. **Monitor** source citations to ensure accuracy
3. **Consider** implementing semantic search for better retrieval
4. **Add** `/refresh-knowledge` endpoint to reload files without restart
5. **Implement** persistent session storage if needed
