# 🏠 LOCAL DEVELOPMENT SETUP GUIDE

**Date**: November 3, 2025  
**Goal**: Run production code locally for debugging

---

## 📋 PREREQUISITES CHECK

### 1. Backend Requirements:
```bash
# Check Python version (need 3.9+)
python3 --version

# Check if virtual environment exists
ls -la venv/

# Check if dependencies installed
pip list | grep fastapi
```

### 2. Frontend Requirements:
```bash
# Check Flutter version
flutter --version

# Check if dependencies installed
cd flutter_app && flutter pub get
```

### 3. Environment Variables:
```bash
# Check if .env.local exists
cat .env.local | grep -E "(OPENAI|FIREBASE|ADMIN)"
```

---

## 🚀 STEP-BY-STEP LOCAL SETUP

### Step 1: Backend Setup (5 min)

```bash
# Navigate to project root
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity

# Create/activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify .env.local has all keys
cat .env.local

# Start backend server
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Test Backend**:
```bash
# In new terminal
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

---

### Step 2: Frontend Setup (5 min)

```bash
# In new terminal, navigate to flutter_app
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app

# Get dependencies
flutter pub get

# Update API URL to local backend
# Edit: lib/utils/constants.dart
# Change: apiBaseUrl = 'http://localhost:8000'

# Run on web
flutter run -d chrome

# OR run on iOS simulator
flutter run -d ios
```

**Expected Output**:
```
✓ Built build/web
Launching lib/main.dart on Chrome in debug mode...
```

---

## 🔍 COMMON ISSUES & FIXES

### Issue 1: Backend Won't Start
**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Fix**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

### Issue 2: Firebase Credentials Missing
**Error**: `DefaultCredentialsError`

**Fix**:
```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/serviceAccountKey.json"

# OR use gcloud auth
gcloud auth application-default login
```

---

### Issue 3: Flutter Dependencies Error
**Error**: `pub get failed`

**Fix**:
```bash
flutter clean
flutter pub get
```

---

### Issue 4: CORS Error in Browser
**Error**: `Access-Control-Allow-Origin`

**Fix**: Backend already has CORS enabled in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ✅ VERIFICATION CHECKLIST

After setup, verify:
- [ ] Backend running on http://localhost:8000
- [ ] `/health` endpoint returns `{"status":"healthy"}`
- [ ] Frontend running on http://localhost:XXXX
- [ ] Can see login screen
- [ ] Can sign up/login
- [ ] Console shows no errors

---

## 🐛 DEBUG MODE

### Enable Verbose Logging:

**Backend** (`app/main.py`):
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend** (`flutter_app/lib/main.dart`):
```dart
void main() {
  debugPrint('🚀 App starting in DEBUG mode');
  runApp(MyApp());
}
```

---

## 📊 WHAT TO CHECK AFTER LOCAL SETUP

1. **Sign up with new user**
2. **Check console logs** for timezone detection
3. **Log "2 eggs"** in chat
4. **Check if appears in Home/Timeline**
5. **Compare with production behavior**

---

## 🔧 QUICK COMMANDS

```bash
# Start backend (from project root)
source venv/bin/activate && cd app && uvicorn main:app --reload

# Start frontend (from project root)
cd flutter_app && flutter run -d chrome

# Check backend logs
tail -f app/logs/*.log

# Check Flutter logs
flutter logs
```

---

**Next**: Once local is working, we'll debug timezone issue locally before deploying!

