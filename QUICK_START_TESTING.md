# 🚀 Quick Start: Testing Chat History & 7-Day Simulation

## ⚡ 5-Minute Manual Test

### 1. Start Servers (if not running)
```bash
# Terminal 1: Backend
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd flutter_app
flutter run -d web-server --web-port 8080
```

### 2. Open Browser
```
http://localhost:8080
```

### 3. Login
```
Email:    alice.test@aiproductivity.app
Password: TestPass123!
```

### 4. Test These Inputs (Copy-Paste)

#### Test 1: Clarification
```
eggs
```
**Expected:** AI asks "How many eggs?"

---

#### Test 2: Direct Log
```
2 eggs
```
**Expected:** "✅ 2 eggs logged - 140 cal, 12g protein"

---

#### Test 3: Multi-Food
```
2 eggs, 1 bowl rice, 5 pistachios
```
**Expected:** 3 separate meal cards

---

#### Test 4: Complex Meal
```
chicken breast with vegetables
```
**Expected:** Meal logged with calories

---

#### Test 5: Indian Food
```
2 roti with dal
```
**Expected:** 2 separate items

---

### 5. Check Chat History (Backend)

#### Option A: Browser DevTools
1. Open DevTools (F12)
2. Go to Application > Local Storage
3. Find `firebase:authUser`
4. Copy the `stsTokenManager.accessToken` value
5. Run this in terminal:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8000/chat/history | json_pp
```

#### Option B: Python Script
```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
source .venv/bin/activate

# Edit tests/test_chat_manually.py to add your token
# Then run:
python3 tests/test_chat_manually.py
```

---

## 📊 What to Check

### ✅ Chat Functionality
- [ ] User message appears in chat
- [ ] AI response appears in chat
- [ ] Clarification question displays
- [ ] Multi-food creates separate cards
- [ ] Calories display correctly
- [ ] Dashboard updates

### ✅ Backend (via API)
- [ ] `/chat/history` returns messages
- [ ] `/chat/stats` shows statistics
- [ ] Messages have timestamps
- [ ] Messages have metadata (calories, etc.)
- [ ] 7-day expiry is set

---

## 🐛 Common Issues

### Issue: "eggs" logs directly instead of asking
**Fix:** Check `backend_simulation.log` for errors

### Issue: Chat history empty
**Fix:** Check Firestore console for `chat_history` collection

### Issue: Wrong calories
**Fix:** Check `app/data/indian_foods.py` for food entry

### Issue: Multi-food creates single entry
**Fix:** Check `app/services/multi_food_parser.py` logs

---

## 📝 Report Results

After testing, report:

1. **What worked:** ✅
2. **What didn't work:** ❌
3. **Screenshots:** 📸
4. **Error messages:** 🐛
5. **Suggestions:** 💡

---

## 🎯 Quick Verification Checklist

```
[ ] Backend running on port 8000
[ ] Frontend running on port 8080
[ ] Logged in successfully
[ ] "eggs" triggers clarification
[ ] "2 eggs" logs 140 cal
[ ] Multi-food creates 3 cards
[ ] Dashboard shows updated calories
[ ] /chat/history returns data
[ ] /chat/stats shows statistics
```

---

## 🚀 Next: Automated Testing

Once manual testing passes, we'll:
1. Fix Firebase auth for automated tests
2. Run 100-user, 7-day simulation
3. Generate comprehensive report
4. Verify 7-day auto-expiry

---

**Ready? Open http://localhost:8080 and start testing!** 🎉


