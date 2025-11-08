# Phase 1 Testing - Quick Start (5 Minutes)

## 🚀 Super Fast Test

### Step 1: Start Backend (1 min)

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Look for:** `✅ [AGENTIC AI] LLM Router initialized successfully`

---

### Step 2: Start Frontend (1 min)

**New terminal:**
```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app
flutter run -d chrome
```

**Wait for:** App opens in browser → Login

---

### Step 3: Test Chat (3 min)

**Go to Chat tab, send these messages:**

1. **Test Meal:**
   ```
   2 eggs for breakfast
   ```
   **Expected:** AI confirms, meal logged

2. **Test Multi-Item:**
   ```
   ran 5km
   1 multivitamin
   drank 2 glasses of water
   ```
   **Expected:** All 3 items logged separately

---

## ✅ Success = All messages work, no errors

## 📋 Full Testing Guide

See `PHASE_1_MANUAL_TESTING_GUIDE.md` for:
- 8 detailed test cases
- Fallback testing
- Troubleshooting guide
- Complete checklist

---

## 🎯 Key Things to Watch

**Backend Logs (GOOD):**
```
🤖 [AGENTIC AI] Using LLM Router for chat classification
✅ [AGENTIC AI] Router success! Provider: openai, Tokens: 150
```

**Frontend (GOOD):**
- Messages send successfully
- AI responds
- No errors in console

**If Router Fails (ALSO GOOD):**
```
⚠️ [AGENTIC AI] Router failed, falling back to direct OpenAI
```
→ Chat still works (zero regression!)

---

**Ready? Start with Step 1 above! 🚀**

