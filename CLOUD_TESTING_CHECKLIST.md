# ✅ Cloud Version Testing Checklist

## Status: Cloud App is LIVE and Working!
**URL**: https://productivityai-mvp.web.app
**Backend**: https://aiproductivity-backend-rhwrraai2a-uc.a.run.app

---

## ✅ Completed Tests:
1. ✅ Landing page loads
2. ✅ Sign in navigation works
3. ✅ Login successful
4. ✅ Home page displays

---

## 🧪 Critical Tests to Perform Now:

### Test 1: Food Logging via Chat
1. Click "Log Food" button (floating action button)
2. Type: `2 eggs and banana for breakfast`
3. **Expected**: 
   - AI parses it correctly
   - Shows calories and macros
   - Logs to home page
4. **Check**: Does it appear in "Today's Meals" section?

### Test 2: Chat History Persistence
1. After logging food, go back to home
2. Click "Log Food" again
3. **Expected**: Previous chat message should still be there
4. **Check**: Is chat history persisting?

### Test 3: Multiple Food Items
1. Type: `chicken breast, rice, and broccoli for lunch`
2. **Expected**:
   - AI groups them as one meal
   - Shows combined calories
   - Logs as single "Lunch" entry
3. **Check**: Does it appear correctly in timeline?

### Test 4: AI Insights
1. Check home page
2. **Expected**: AI insights card showing recommendations
3. **Check**: Are insights visible and relevant?

### Test 5: Calorie Tracking
1. Check top bar on home page
2. **Expected**: 
   - Shows calories consumed
   - Shows "Over" or "Under" budget
   - Shows deficit/surplus
3. **Check**: Are numbers accurate?

### Test 6: Feedback Button
1. Look for orange feedback button (floating)
2. Click it
3. **Expected**: Feedback dialog appears
4. **Check**: Can you submit feedback?

### Test 7: Navigation
1. Try clicking back button in chat
2. Try bottom navigation (if visible)
3. **Expected**: Smooth navigation
4. **Check**: No broken routes?

---

## 🐛 Known Issues to Watch For:
- ❌ "Unknown food" classification
- ❌ Duplicate meal entries
- ❌ Chat history not persisting
- ❌ Slow performance
- ❌ Missing calorie deficit

---

## 📝 Report Format:
For each test, report:
- **Test #**: (1-7)
- **Status**: Pass / Fail / Partial
- **Details**: What happened
- **Screenshot**: (if issue found)

---

**Start with Test 1: Log "2 eggs and banana for breakfast" and tell me what happens! 🍳🍌**

