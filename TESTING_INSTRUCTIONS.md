# 🧪 Testing Instructions - Food Logging Issue

**Date**: November 2, 2025  
**Issue**: Food parsing works but not appearing on home page

---

## 🎯 What We're Testing

1. ✅ AI parsing (WORKING - "2 eggs" → correctly parsed)
2. ❌ **Data persistence** (SUSPECTED ISSUE - not saving to Firestore?)
3. ❌ **Home page display** (NOT WORKING - shows 0 calories)

---

## 📋 Step-by-Step Local Testing

### Step 1: Start Backend Locally

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity

# Activate virtual environment
source .venv/bin/activate

# Start backend
python -m uvicorn app.main:app --reload --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

### Step 2: Run Automated Test Script

**Open a NEW terminal** (keep backend running):

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity

# Run test script
python test_logging_local.py
```

**What the script does**:
1. ✅ Checks if backend is running
2. ✅ Asks for Firebase ID token (for auth)
3. ✅ Sends test messages to `/chat` endpoint
4. ✅ Checks Firestore directly for saved logs
5. ✅ Calls `/fitness/daily-stats` to verify data retrieval

---

### Step 3: Analyze Test Results

#### ✅ SUCCESS Scenario:
```
✅ Backend is running
✅ Chat response OK
✅ Found X fitness logs in Firestore
✅ Daily stats received: 235 / 1611 calories
```

**Conclusion**: Backend is working! Issue is in frontend.

---

#### ❌ FAILURE Scenario 1: No Logs in Firestore
```
✅ Backend is running
✅ Chat response OK
⚠️  No fitness logs found in Firestore
❌ Daily stats: 0 / 1611 calories
```

**Conclusion**: Backend save is failing! Check console for errors.

**Look for**:
```
ERROR persisting data: <error type>: <error message>
```

---

#### ❌ FAILURE Scenario 2: Logs in Firestore but Not in API
```
✅ Backend is running
✅ Chat response OK
✅ Found X logs in Firestore
❌ Daily stats: 0 / 1611 calories
```

**Conclusion**: Firestore structure mismatch! Backend saves to one path, API reads from another.

---

### Step 4: Check Backend Console

While running tests, watch the backend console for:

```bash
# Good signs:
💾 Saving user message to history: user_id=...
💾 Saving fitness log: user_id=..., content=2 eggs, calories=140
✅ Fitness log saved: log_id=...

# Bad signs:
ERROR persisting data: <error>
Traceback (most recent call last):
  ...
```

---

## 🔍 Manual Firestore Check

If automated tests don't work, check Firestore manually:

1. Go to: https://console.firebase.google.com/project/productivityai-mvp/firestore

2. Navigate to: `users` collection

3. Find your user (e.g., `alice.test@aiproductivity.app`)

4. Check subcollection: `fitness_logs`

5. **Expected**: See documents with:
   - `content`: "2 eggs, 1 apple"
   - `calories`: 235
   - `log_type`: "meal"
   - `timestamp`: recent date

6. **If empty**: Backend save is failing!

---

## 🐛 Common Issues & Fixes

### Issue #1: "ERROR persisting data: PermissionDenied"

**Cause**: Firestore security rules blocking write

**Fix**:
```bash
# Check firestore.rules
cat firestore.rules

# Should allow authenticated users to write their own data:
match /users/{userId}/fitness_logs/{logId} {
  allow write: if request.auth.uid == userId;
}
```

---

### Issue #2: "ERROR persisting data: AttributeError: 'NoneType'"

**Cause**: `dbsvc` not properly initialized

**Fix**: Check `app/main.py` line 55:
```python
from app.services import database as dbsvc
```

---

### Issue #3: Logs in OLD structure, API reads NEW structure

**Cause**: Migration incomplete

**Check**:
```python
# app/services/database.py
USE_NEW_STRUCTURE = True  # Should be True
```

**Fix**: Ensure both save and read use same structure

---

## 📊 Test Checklist

### Local Tests
- [ ] Backend starts without errors
- [ ] Test script runs successfully
- [ ] Chat endpoint responds (200 OK)
- [ ] Firestore shows saved logs
- [ ] Daily stats API returns correct data
- [ ] No errors in backend console

### Cloud Tests (After local tests pass)
- [ ] Deploy to Cloud Run
- [ ] Check Cloud Run logs for errors
- [ ] Verify Firestore console shows logs
- [ ] Test frontend in browser
- [ ] Home page displays logged food
- [ ] Calories update correctly

---

## 🚀 After Tests Pass Locally

### Deploy to Cloud:
```bash
./auto_deploy.sh
```

### Monitor Cloud Run Logs:
```bash
gcloud run services logs read aiproductivity-backend \
  --project=productivityai-mvp \
  --region=us-central1 \
  --limit=100 \
  --format="table(timestamp, textPayload)"
```

### Test in Production:
1. Go to: https://productivityai-mvp.web.app
2. Login
3. Click "Log Food"
4. Type: "2 eggs and banana for breakfast"
5. Send
6. Go back to home
7. **Expected**: See logged food, updated calories

---

## 📝 Reporting Results

After running tests, report:

1. **Test Script Output**: Copy/paste full output
2. **Backend Console Logs**: Any errors or warnings
3. **Firestore Screenshot**: Show if logs exist
4. **Frontend Screenshot**: Show home page state

---

## 🎯 Next Steps Based on Results

### If Local Tests PASS:
1. ✅ Deploy to cloud
2. ✅ Test in production
3. ✅ Monitor for 24 hours

### If Local Tests FAIL:
1. ❌ Fix errors found
2. ❌ Re-run tests
3. ❌ Don't deploy until passing

---

**Ready to test! Run the commands above and share results! 🧪**

