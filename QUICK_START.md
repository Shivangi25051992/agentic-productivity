# 🚀 QUICK START - Local Development

**Status**: ✅ Environment Ready  
**Credentials**: ✅ Same as production (will separate later)

---

## ⚡ START LOCAL (2 Commands)

### Terminal 1 - Backend:
```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/app
source ../venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected**: `INFO: Uvicorn running on http://0.0.0.0:8000`

---

### Terminal 2 - Frontend:
```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app

# IMPORTANT: First time only - update API URL
# Edit: lib/utils/constants.dart
# Line 6: Change to 'http://localhost:8000'

flutter run -d chrome
```

**Expected**: `✓ Built build/web` and browser opens

---

## ✅ VERIFY IT WORKS

```bash
# Test backend health
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# Test admin login
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# Should return: {"token":"..."}
```

---

## 🔍 DEBUG TIMEZONE ISSUE

### In Browser Console (F12):

**During signup, look for**:
```
🔍 TimezoneHelper.getLocalTimezone() called
🔍 Platform: WEB
🔍 UTC Offset detected: 5:30:00.000000
🌍 Mapping offset +5:30 to timezone
✅ Web timezone (from offset): Asia/Kolkata
🔍 ONBOARDING: Timezone detected: Asia/Kolkata
```

**If missing**: TimezoneHelper not being called  
**If shows UTC**: Offset detection failed

---

## 📊 USEFUL COMMANDS

```bash
# Check what's running
lsof -i :8000  # Backend
lsof -i :XXXX  # Frontend (Flutter shows port)

# View backend logs
tail -f app/logs/*.log

# View Flutter logs
flutter logs

# Restart backend (if needed)
# Ctrl+C in Terminal 1, then re-run uvicorn command

# Restart frontend (if needed)
# Ctrl+C in Terminal 2, then re-run flutter command
```

---

## 🐛 COMMON ISSUES

### Backend won't start:
```bash
# Activate venv first
source venv/bin/activate

# Check if port is busy
lsof -i :8000
kill -9 <PID>  # If needed
```

### Frontend won't start:
```bash
# Clean and retry
flutter clean
flutter pub get
flutter run -d chrome
```

### CORS errors:
- Backend already has CORS enabled
- Make sure apiBaseUrl is 'http://localhost:8000' (not https)

---

## 📝 FILES TO READ

1. **TODAY_PLAN.md** - Complete execution plan
2. **LOCAL_SETUP_GUIDE.md** - Detailed setup instructions
3. **TOMORROW_PRIORITY.md** - Timezone fix priority

---

## 🎯 TODAY'S GOAL

1. ✅ Local running
2. ⏳ Debug timezone detection
3. ⏳ Fix frontend filtering
4. ⏳ Test locally
5. ⏳ Deploy to production

---

**Start with Terminal 1 (Backend), then Terminal 2 (Frontend)!** 🚀
