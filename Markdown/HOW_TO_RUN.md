# 🚀 Quick Start Guide - College Chatbot

## ⚡ Fastest Way to Run

### Option 1: Double-click the batch file
```
START_CHATBOT.bat
```

### Option 2: PowerShell script
```
START_CHATBOT.ps1
```

### Option 3: Command Line
```bash
# Windows Command Prompt or PowerShell
cd "C:\Users\Seratul Mustakim\Downloads\College_chatbot\College_chatbot"
python app/app.py
```

### Option 4: Using Virtual Environment
```bash
cd "C:\Users\Seratul Mustakim\Downloads\College_chatbot\College_chatbot"
.venv\Scripts\python.exe app\app.py
```

## 🌐 Access the App

Once started, open your browser to:
- **Main Chatbot**: http://localhost:8081
- **Or**: http://127.0.0.1:8081

## 🧪 Run Tests

All test files work from the root directory:

```bash
# Test scholarship retrieval
python quick_test.py

# Test general queries
python test_general_queries.py

# Test chat functionality
python test_chat.py

# Test scholarship formatting
python test_formatting.py

# And more...
```

## 🛠️ Admin Panel

The Admin Panel is separate and has its own startup:

```bash
cd "Admin Panel"
python start.py

# Or double-click:
Admin Panel\START_BOTH.bat
```

Admin Panel runs on: **http://localhost:3000**

## 📂 Project Structure

```
College_chatbot/
├── START_CHATBOT.bat           ← Double-click to run! ⭐
├── START_CHATBOT.ps1           ← PowerShell version
├── app/
│   └── app.py                  ← Main application
├── test_*.py                   ← Test files
└── Admin Panel/
    └── START_BOTH.bat          ← Admin panel
```

## 🔍 Common Issues

### Issue: Import errors
**Solution**: Make sure you're running from the project root directory

### Issue: Port already in use
**Solution**: Check if the app is already running, or change the port:
```bash
set PORT=5000
python app/app.py
```

### Issue: Module not found
**Solution**: Activate the virtual environment:
```bash
.venv\Scripts\activate
```

## 💡 Tips

1. **Always run from project root** - The path `app/app.py` is relative to root
2. **Use the batch file** - Easiest way to start
3. **Check the terminal** - It shows when the server is ready
4. **Test files are standalone** - They set up their own imports

## 📞 Need Help?

- Check [PATH_FIX_SUMMARY.md](PATH_FIX_SUMMARY.md) for detailed information
- Read [QUICKSTART.md](QUICKSTART.md) for full documentation
- All tests should pass with `python <test_file>.py`

---

**Last Updated**: December 14, 2025
**Status**: ✅ All paths fixed and working!
