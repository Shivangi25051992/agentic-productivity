# QA Sprint Plan - Comprehensive Testing & Audit

**Objective:** Ensure zero regression, optimal performance, and enterprise-grade quality  
**Duration:** 4-6 hours (systematic approach)  
**Status:** Not Started  
**Owner:** Development Team  
**Last Updated:** 2024-11-06

---

## 📋 **SCOPE**

### **In Scope:**
✅ Automated testing (unit, integration)  
✅ Manual testing (critical user flows)  
✅ Performance benchmarking  
✅ Security audit  
✅ Regression testing  
✅ Error handling & edge cases  
✅ Mobile responsiveness  
✅ Data integrity  

### **Out of Scope (for this sprint):**
❌ Load testing (1000+ concurrent users)  
❌ Penetration testing (external security firm)  
❌ Browser compatibility (IE, Safari < 14)  
❌ Accessibility (WCAG 2.1 AA) - Quick review only  

---

## 🎯 **TEST CATEGORIES**

### **1. Automated Testing (Backend)**
**Goal:** 80%+ code coverage for critical paths  
**Time:** 2 hours  

#### **1.1 Unit Tests**
**Status:** ✅ Partial (87 tests exist for Phase 1 LLM services)  
**Gaps to Fill:**

- [ ] `test_chat_endpoint.py` - Chat classification & response generation
  - Test all food categories (meal, workout, water, supplement)
  - Test multi-item inputs
  - Test clarification flows
  - Test cache hit/miss scenarios
  
- [ ] `test_meal_planning_service.py` - Meal plan generation
  - Test AI meal plan generation
  - Test dietary preferences
  - Test week deactivation logic
  
- [ ] `test_context_service.py` - User context & caching
  - Test realtime calorie fetch
  - Test cache TTL behavior
  - Test streak calculation (when re-enabled)
  
- [ ] `test_fasting_service.py` - Fasting tracker
  - Test start/stop fasting
  - Test status calculation
  - Test stage transitions

**Command to run:**
```bash
pytest tests/unit/ -v --cov=app --cov-report=html
```

**Acceptance Criteria:**
- All tests pass
- Coverage ≥ 75% for critical services
- No test takes > 5 seconds
- Zero flaky tests

#### **1.2 Integration Tests**
**Status:** ✅ Partial (12 tests for chat regression)  
**Gaps to Fill:**

- [ ] End-to-end chat flow (user → LLM → DB → response)
- [ ] Firestore data persistence & retrieval
- [ ] LLM Router fallback behavior
- [ ] Multi-provider quota management

**Command to run:**
```bash
pytest tests/integration/ -v --cov=app
```

**Acceptance Criteria:**
- All integration tests pass
- DB operations verified
- LLM responses validated
- Error handling tested

---

### **2. Manual Testing (Critical User Flows)**
**Goal:** Validate end-to-end functionality  
**Time:** 1.5 hours  

#### **2.1 Authentication & Onboarding**
- [ ] Sign up with email/password
- [ ] Sign in with Google
- [ ] Sign in with Apple
- [ ] Password reset flow
- [ ] Profile creation (goals, weight, height)
- [ ] Session persistence (refresh page)
- [ ] Logout and re-login

**Acceptance Criteria:**
- All auth flows work without errors
- User data persists correctly
- No console errors
- Smooth UX transitions

#### **2.2 Chat Feature (Core Functionality)**
- [ ] **Food Logging:**
  - Single item: "1 apple"
  - Multiple items: "2 eggs and 1 banana"
  - Complex meal: "grilled chicken breast 200g with rice and salad"
  - Portion sizes: "half a pizza", "2 slices of bread"
  - Ambiguous input: "fruit" (expect clarification)
  
- [ ] **Workout Logging:**
  - Simple: "ran 5k"
  - With duration: "gym for 1 hour"
  - Multiple: "30 min run and 20 min weights"
  
- [ ] **Water & Supplements:**
  - "1 glass of water"
  - "vitamin D"
  - "2 liters of water"
  
- [ ] **Fasting Commands:**
  - "start fast"
  - "fast status"
  - "end fast"
  
- [ ] **Chat History:**
  - Verify 24-hour retention
  - Scroll through history
  - Messages persist across sessions

**Acceptance Criteria:**
- Chat response time < 8 seconds
- Expandable UI works correctly
- Progress bar is cumulative
- Dashboard updates immediately
- No "Unknown" items
- Correct emoji & meal type classification

#### **2.3 Meal Planning Feature**
- [ ] Generate meal plan (default dietary preference)
- [ ] Generate with dietary preferences:
  - High protein
  - Low carb
  - Vegetarian
  - Vegan
  - Gluten-free
- [ ] View current week plan
- [ ] Navigate between days (Mon → Sun)
- [ ] View meal details (calories, macros)
- [ ] Generate new plan (deactivates old one)
- [ ] Verify only ONE active plan per week

**Acceptance Criteria:**
- Meal plans generate in < 15 seconds
- All 21 meals populate (7 days × 3 meals)
- Day selection works correctly
- New plan replaces old one
- No duplicate active plans

#### **2.4 Dashboard & Timeline**
- [ ] Dashboard shows correct totals:
  - Calories consumed
  - Protein
  - Carbs
  - Fat
- [ ] Today's meals card:
  - Breakfast
  - Lunch
  - Dinner
  - Snacks
- [ ] Timeline shows chronological logs
- [ ] Progress bars accurate
- [ ] Water intake tracked
- [ ] Supplement logs visible

**Acceptance Criteria:**
- Dashboard matches chat progress bar (within 5 kcal)
- Timeline chronological order
- All meal types displayed correctly
- No missing data
- Real-time updates work

#### **2.5 Profile & Settings**
- [ ] Edit profile (name, goals, weight)
- [ ] Update dietary preferences
- [ ] Change daily calorie goal
- [ ] Toggle dark mode
- [ ] Wipe all logs (confirm it works)
- [ ] Logout

**Acceptance Criteria:**
- All edits save correctly
- Changes reflect immediately
- Wipe all logs clears data (may show error but works)
- Dark mode persists

---

### **3. Performance Testing**
**Goal:** Identify bottlenecks and optimize  
**Time:** 1 hour  

#### **3.1 Backend Performance Benchmarks**

**Test Scenarios:**

1. **Chat Response Time** (Target: < 5 seconds)
   ```bash
   # Run 10 chat requests, measure average
   python tests/performance/test_chat_latency.py
   ```
   - Measure: LLM classification time
   - Measure: DB persistence time
   - Measure: Context retrieval time
   - Measure: Total end-to-end time

2. **Firestore Query Performance** (Target: < 500ms)
   - Test `list_fitness_logs_by_user()` with 100 logs
   - Test `get_today_calories_realtime()` with 50 logs
   - Test meal plan queries

3. **LLM Router Performance** (Target: < 4 seconds)
   - Test OpenAI provider response time
   - Test fallback behavior
   - Test quota management overhead

4. **Cache Effectiveness**
   - Test context service cache hit rate (target > 70%)
   - Test food macro cache hit rate (target > 80%)

**Acceptance Criteria:**
- Chat response < 8 seconds (95th percentile)
- Firestore queries < 500ms
- LLM Router < 4 seconds
- Cache hit rate > 70%
- No memory leaks

#### **3.2 Frontend Performance**

- [ ] Page load time (Target: < 3 seconds)
- [ ] Chat message render time (Target: < 100ms)
- [ ] Dashboard data fetch (Target: < 2 seconds)
- [ ] Smooth scrolling (60 FPS)
- [ ] No UI blocking operations

**Tools:**
- Chrome DevTools (Performance tab)
- Lighthouse audit
- Flutter DevTools (Performance overlay)

**Acceptance Criteria:**
- First contentful paint < 1.5s
- Time to interactive < 3s
- No layout shifts (CLS = 0)
- Smooth animations (60 FPS)

---

### **4. Security Audit**
**Goal:** Identify and fix security vulnerabilities  
**Time:** 1 hour  

#### **4.1 Authentication & Authorization**
- [ ] Test unauthenticated API access (should return 401)
- [ ] Test accessing other user's data (should return 403)
- [ ] Verify Firebase token validation
- [ ] Check session expiration
- [ ] Test CSRF protection
- [ ] Verify secure cookie flags

**Tools:**
```bash
# Test unauthorized access
curl -X GET http://localhost:8000/profile/me
curl -X GET http://localhost:8000/fitness/logs

# Test with invalid token
curl -X GET http://localhost:8000/profile/me \
  -H "Authorization: Bearer invalid_token"
```

**Acceptance Criteria:**
- All protected endpoints require authentication
- Invalid tokens rejected
- Users can only access own data
- No sensitive data in error messages

#### **4.2 Data Protection**
- [ ] PII (Personally Identifiable Information) encrypted at rest
- [ ] Passwords never logged
- [ ] API keys not exposed in frontend
- [ ] HTTPS enforced in production
- [ ] Firestore security rules validated

**Firestore Security Rules Check:**
```javascript
// Verify these rules are in place:
match /users/{userId} {
  allow read, write: if request.auth != null && request.auth.uid == userId;
}
```

**Acceptance Criteria:**
- No hardcoded secrets in code
- Environment variables used for API keys
- Firestore rules prevent unauthorized access
- HTTPS only in production

#### **4.3 Input Validation**
- [ ] SQL injection (N/A - using Firestore)
- [ ] XSS (Cross-Site Scripting) in chat input
- [ ] Large payload handling (> 10KB)
- [ ] Special characters in food names
- [ ] Unicode/emoji handling

**Test Cases:**
```python
# XSS attempts
"<script>alert('XSS')</script>"
"<img src=x onerror=alert('XSS')>"

# Injection attempts
"'; DROP TABLE users; --"
"../../etc/passwd"

# Large payloads
"A" * 100000  # 100KB string
```

**Acceptance Criteria:**
- All inputs sanitized
- No XSS vulnerabilities
- Large payloads rejected gracefully
- Special characters handled correctly

#### **4.4 API Security**
- [ ] Rate limiting on chat endpoint
- [ ] CORS configured correctly
- [ ] No sensitive data in API responses
- [ ] Error messages don't leak internal info

**Acceptance Criteria:**
- CORS allows only trusted origins
- Rate limiting prevents abuse
- Error messages user-friendly, not technical

---

### **5. Regression Testing**
**Goal:** Ensure no existing features broke  
**Time:** 30 minutes  

#### **5.1 Feature Checklist (Quick Smoke Test)**

**Core Features:**
- [ ] Chat - food, workout, water, supplement logging
- [ ] Dashboard - calories, macros, progress bars
- [ ] Timeline - chronological view, all log types
- [ ] Meal Planning - generate, view, switch days
- [ ] Fasting - start, status, end
- [ ] Profile - edit, save, persist
- [ ] Wipe Logs - clears all data

**Recent Changes (Focus on Expandable Chat):**
- [ ] Expandable chat UI works
- [ ] Summary shows specific food (not generic)
- [ ] No duplicate calories in summary
- [ ] Progress bar cumulative (not stuck at 0)
- [ ] Progress bar matches dashboard (within 5 kcal)
- [ ] No double counting
- [ ] Food emojis correct
- [ ] Expand/collapse animation smooth
- [ ] User preference persists

**Acceptance Criteria:**
- All core features working
- No console errors
- No unexpected behavior
- Recent changes stable

---

### **6. Error Handling & Edge Cases**
**Goal:** Graceful degradation, no crashes  
**Time:** 30 minutes  

#### **6.1 Network Failures**
- [ ] Test offline mode (disable network)
- [ ] Test slow network (3G throttling)
- [ ] Test backend down (stop server)
- [ ] Test Firestore unavailable
- [ ] Test OpenAI API timeout

**Acceptance Criteria:**
- User-friendly error messages
- No white screens of death
- Retry mechanisms work
- Offline banner shown

#### **6.2 Invalid Inputs**
- [ ] Empty chat message
- [ ] Very long chat message (> 1000 chars)
- [ ] Non-English text
- [ ] Only emojis
- [ ] Nonsensical input: "asdfghjkl"

**Acceptance Criteria:**
- No crashes
- Clarification requested when needed
- Graceful fallbacks

#### **6.3 Edge Cases**
- [ ] User has 0 logs (empty state)
- [ ] User has 1000+ logs (pagination)
- [ ] Day with no meals (empty meal card)
- [ ] Fasting for 72+ hours
- [ ] Over daily calorie goal (red progress bar)

**Acceptance Criteria:**
- Empty states shown correctly
- Large datasets handled
- UI doesn't break

---

### **7. Mobile Responsiveness**
**Goal:** Works on all screen sizes  
**Time:** 15 minutes  

#### **7.1 Screen Sizes to Test**
- [ ] Mobile (375px - iPhone SE)
- [ ] Mobile (414px - iPhone 14 Pro)
- [ ] Tablet (768px - iPad)
- [ ] Desktop (1920px)

**Acceptance Criteria:**
- No horizontal scrolling
- All buttons accessible
- Text readable (no overflow)
- Chat input not obscured by keyboard

---

## 📊 **TEST EXECUTION TRACKING**

### **Progress Tracker:**

| Category | Tests Planned | Tests Passed | Tests Failed | Coverage |
|----------|---------------|--------------|--------------|----------|
| Unit Tests | TBD | 0 | 0 | 0% |
| Integration Tests | 12 | 0 | 0 | 0% |
| Manual Tests | 50+ | 0 | 0 | 0% |
| Performance | 10 | 0 | 0 | 0% |
| Security | 15 | 0 | 0 | 0% |
| Regression | 20 | 0 | 0 | 0% |

**Overall Progress:** 0% (Not Started)

---

## 🐛 **BUG TRACKING**

### **Bugs Found:**

| ID | Severity | Category | Description | Status |
|----|----------|----------|-------------|--------|
| (Empty - to be filled during testing) | | | | |

**Severity Levels:**
- **P0 (Blocker):** App crashes, data loss, security vulnerability
- **P1 (Critical):** Core feature broken, major UX issue
- **P2 (High):** Feature partially broken, workaround exists
- **P3 (Medium):** Minor bug, cosmetic issue
- **P4 (Low):** Nice to have, enhancement

---

## ✅ **DEFINITION OF DONE**

### **Sprint Completion Criteria:**

**Must Have (Blockers):**
- [ ] Zero P0 bugs
- [ ] Zero P1 bugs
- [ ] All manual critical flows pass
- [ ] Performance benchmarks met
- [ ] Security audit clean (no high-risk issues)
- [ ] Regression tests pass (no broken features)

**Should Have:**
- [ ] Unit test coverage ≥ 70%
- [ ] All P2 bugs documented (fix plan exists)
- [ ] Performance report documented
- [ ] Security recommendations documented

**Nice to Have:**
- [ ] All P3 bugs fixed
- [ ] Integration test coverage ≥ 80%
- [ ] Lighthouse score ≥ 90
- [ ] Mobile responsiveness perfect

---

## 📋 **DELIVERABLES**

At sprint completion, we'll have:

1. **`QA_TEST_RESULTS.md`** - Detailed test results
2. **`PERFORMANCE_REPORT.md`** - Benchmarks & bottlenecks
3. **`SECURITY_AUDIT_REPORT.md`** - Vulnerabilities & fixes
4. **`BUG_REGISTRY.md`** - All bugs found (with severity & status)
5. **Updated `KNOWN_ISSUES_BACKLOG.md`** - Any deferred issues
6. **`QA_SPRINT_SUMMARY.md`** - Executive summary for stakeholders

---

## 🚀 **NEXT STEPS**

**Ready to start?**

**Phase 1: Automated Testing** (2 hours)
- Run existing tests
- Fill gaps in unit tests
- Add integration tests
- Generate coverage report

**Phase 2: Manual Testing** (1.5 hours)
- Test all critical flows
- Document any bugs
- Verify recent changes

**Phase 3: Performance & Security** (1.5 hours)
- Run performance benchmarks
- Security audit
- Document findings

**Phase 4: Reporting** (30 minutes)
- Compile all results
- Create deliverables
- Prioritize any issues found

**Total: 5.5 hours**

---

**Shall we start with Phase 1 (Automated Testing)?** 🧪

