# 🛡️ SAFETY CHECKLIST - Zero Regression Policy

**Critical Rule**: NEVER break existing working features while adding new ones.

---

## 🚨 CURRENT RISK ASSESSMENT

### ⚠️ HIGH RISK CHANGES MADE

#### 1. Modified `app/main.py` - Chat Endpoint
**What Changed**:
- Added water and supplement logging (lines 845-885)
- Modified LLM system prompt (added water/supplement categories)
- Added timezone context to prompt

**Risk Level**: 🔴 **HIGH**
- This is the **CORE CHAT ENDPOINT** used by all users
- Any bug here breaks meal logging, workout logging, task creation

**Existing Features That Could Break**:
- ✅ Meal logging (breakfast, lunch, dinner, snacks)
- ✅ Workout logging
- ✅ Task/reminder creation
- ✅ Chat history persistence
- ✅ AI insights generation
- ✅ Calorie calculation
- ✅ Macro tracking

**Testing Required Before Deployment**:
1. ✅ Test meal logging: "2 eggs for breakfast"
2. ✅ Test workout logging: "ran 5km"
3. ✅ Test task creation: "remind me to call doctor"
4. ✅ Test multi-item meals: "2 eggs and toast for breakfast"
5. ✅ Test water logging: "drank 2 glasses of water"
6. ✅ Test supplement logging: "took multivitamin"
7. ✅ Test mixed input: "2 eggs, ran 5km, drank water"
8. ✅ Check Firestore: Verify all logs are saved correctly
9. ✅ Check chat history: Verify messages persist
10. ✅ Check dashboard: Verify data displays correctly

---

#### 2. Modified `app/routers/profile.py` - Onboarding
**What Changed**:
- Added timezone field to OnboardRequest
- Store timezone in user profile

**Risk Level**: 🟡 **MEDIUM**
- Affects new user onboarding
- Existing users unaffected (already onboarded)

**Existing Features That Could Break**:
- ✅ User onboarding flow
- ✅ Profile creation
- ✅ Goal calculation

**Testing Required**:
1. ✅ Complete onboarding as new user
2. ✅ Verify profile created with timezone
3. ✅ Verify goals calculated correctly
4. ✅ Verify existing users can still log in

---

#### 3. Modified `app/services/multi_food_parser.py`
**What Changed**:
- Added user_id parameter to __init__
- Get user's local time for meal classification

**Risk Level**: 🟡 **MEDIUM**
- Used for multi-food meal parsing
- Backward compatible (user_id is optional)

**Existing Features That Could Break**:
- ✅ Multi-food parsing ("2 eggs and toast")
- ✅ Meal type classification

**Testing Required**:
1. ✅ Test multi-food parsing
2. ✅ Test meal type classification
3. ✅ Test with and without user_id

---

#### 4. Created New Files (Low Risk)
**What Changed**:
- `app/services/timezone_service.py` (new)
- `flutter_app/lib/screens/profile/edit_profile_screen.dart` (new)

**Risk Level**: 🟢 **LOW**
- New files don't affect existing code
- Only used when explicitly called

---

## 🎯 ZERO-REGRESSION TESTING PLAN

### Phase 1: Backend API Testing (CRITICAL)

**Test Environment**: Local or staging, NOT production

#### Test 1: Meal Logging (MUST PASS)
```bash
# Test simple meal
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "2 eggs for breakfast"}'

Expected:
- ✅ Returns meal item with calories
- ✅ Saves to fitness_logs collection
- ✅ Meal type = "breakfast"
- ✅ Chat history saved
```

#### Test 2: Workout Logging (MUST PASS)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "ran 5km"}'

Expected:
- ✅ Returns workout item with calories burned
- ✅ Saves to fitness_logs collection
- ✅ Log type = "workout"
```

#### Test 3: Water Logging (NEW FEATURE)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "drank 2 glasses of water"}'

Expected:
- ✅ Returns water item
- ✅ Saves to users/{userId}/water_logs
- ✅ quantity_ml = 500
```

#### Test 4: Supplement Logging (NEW FEATURE)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "took multivitamin"}'

Expected:
- ✅ Returns supplement item
- ✅ Saves to users/{userId}/supplement_logs
```

#### Test 5: Mixed Input (CRITICAL)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "2 eggs for breakfast, ran 5km, drank water, took vitamin d"}'

Expected:
- ✅ Returns 4 items (meal, workout, water, supplement)
- ✅ Each saved to correct collection
- ✅ No errors or data loss
```

#### Test 6: Profile Update (MUST PASS)
```bash
curl -X PUT http://localhost:8000/profile/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"weight_kg": 75.5}'

Expected:
- ✅ Profile updated
- ✅ Goals recalculated
- ✅ No data loss
```

---

### Phase 2: Frontend Testing (CRITICAL)

**Test on**: Browser (Chrome, Safari) + Mobile (iOS Safari PWA)

#### Test 1: Existing Dashboard (MUST WORK)
1. ✅ Login
2. ✅ Dashboard loads
3. ✅ Today's meals display
4. ✅ Calorie progress bar shows
5. ✅ Timeline view works
6. ✅ Profile screen works

#### Test 2: Chat Functionality (MUST WORK)
1. ✅ Open chat
2. ✅ Type "2 eggs for breakfast"
3. ✅ AI responds with confirmation
4. ✅ Meal appears in dashboard
5. ✅ Calories update
6. ✅ Chat history persists

#### Test 3: Profile Edit (NEW FEATURE)
1. ✅ Go to Profile
2. ✅ Click "Edit Profile"
3. ✅ Update weight
4. ✅ Save changes
5. ✅ Verify profile updated
6. ✅ Verify dashboard reflects new goals

---

### Phase 3: Database Integrity Check

**Check Firestore Collections**:

1. ✅ `fitness_logs` - Meals and workouts still saving
2. ✅ `users/{userId}/water_logs` - New water logs present
3. ✅ `users/{userId}/supplement_logs` - New supplement logs present
4. ✅ `user_profiles` - Timezone field added
5. ✅ `chat_history` - Messages still saving
6. ✅ No orphaned documents
7. ✅ No duplicate logs

---

## 🚫 DEPLOYMENT BLOCKERS

**DO NOT DEPLOY if ANY of these fail**:

1. ❌ Meal logging broken
2. ❌ Workout logging broken
3. ❌ Dashboard not loading
4. ❌ Chat history not persisting
5. ❌ Profile update fails
6. ❌ Existing users cannot log in
7. ❌ Timeline view broken
8. ❌ Calorie calculation wrong

---

## ✅ SAFE DEPLOYMENT CHECKLIST

Before deploying to production:

### Pre-Deployment
- [ ] All backend API tests pass (6/6)
- [ ] All frontend tests pass (3/3)
- [ ] Database integrity verified
- [ ] No linting errors
- [ ] No console errors
- [ ] Code reviewed for breaking changes

### Deployment Strategy
- [ ] Deploy to staging first
- [ ] Test with real user account
- [ ] Monitor logs for errors
- [ ] Check Firestore for correct data
- [ ] Verify existing features work
- [ ] Test new features (water, supplements)

### Post-Deployment
- [ ] Monitor Cloud Run logs for errors
- [ ] Check Firestore usage (no spikes)
- [ ] Test with multiple users
- [ ] Verify no 500 errors
- [ ] Check chat response times
- [ ] Verify dashboard loads < 2 seconds

### Rollback Plan
If ANY issue detected:
1. ⚠️ Immediately rollback to previous version
2. ⚠️ Investigate issue in staging
3. ⚠️ Fix and re-test
4. ⚠️ Re-deploy only after all tests pass

---

## 🎯 CURRENT STATUS

### Completed Changes
1. ✅ Timezone detection (backend + frontend)
2. ✅ Profile update UI
3. ✅ Water tracking (backend only)
4. ✅ Supplement tracking (backend only)

### Testing Status
- ❌ Backend API tests: NOT RUN
- ❌ Frontend tests: NOT RUN
- ❌ Database integrity: NOT VERIFIED
- ❌ Staging deployment: NOT DONE

### Ready to Deploy?
**🔴 NO - Testing required first**

---

## 📋 NEXT STEPS (SAFE APPROACH)

### Step 1: Local Testing (2-3 hours)
1. Start local backend
2. Run all 6 backend API tests
3. Start local frontend
4. Run all 3 frontend tests
5. Verify Firestore data
6. Fix any issues found

### Step 2: Staging Deployment (1 hour)
1. Deploy backend to staging
2. Deploy frontend to staging
3. Test with real user account
4. Monitor logs
5. Verify all features work

### Step 3: Production Deployment (30 min)
1. Only if staging tests pass 100%
2. Deploy during low-traffic hours
3. Monitor closely for 1 hour
4. Be ready to rollback

### Step 4: Frontend Widgets (4-6 hours)
**ONLY AFTER** backend is stable:
1. Create water intake widget
2. Create supplement widget
3. Add to dashboard
4. Test thoroughly
5. Deploy separately

---

## 🛡️ SAFETY PRINCIPLES

1. **Test Everything**: Never assume code works
2. **Deploy Incrementally**: One feature at a time
3. **Monitor Closely**: Watch logs after deployment
4. **Rollback Fast**: Don't hesitate to revert
5. **User First**: Existing features > New features
6. **No Surprises**: Test before users see it

---

**Remember**: It's better to delay a feature than to break existing functionality!

---

*Last Updated: November 2, 2025*

