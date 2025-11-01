# 🧪 Manual End-to-End Testing Guide
## Complete User Journey with Action Logging

---

## 🎯 Overview

This guide walks you through the complete user experience from signup to all major features, with every action logged for debugging and analysis.

---

## 🚀 Pre-Test Setup

### Step 1: Clear All Caches

```bash
# Navigate to project
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity

# Stop all running servers
./stop-dev.sh

# Clear browser cache (Manual)
# Chrome/Edge: Cmd+Shift+Delete → Clear all data
# Safari: Cmd+Option+E → Empty Caches

# Clear Flutter build cache
cd flutter_app
flutter clean
flutter pub get

# Clear backend cache (if any)
cd ..
rm -rf .pytest_cache
rm -rf __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Restart servers
./start-dev.sh
```

### Step 2: Verify Servers Running

```bash
# Check backend
curl http://localhost:8000/health

# Expected: {"status":"healthy",...}

# Check frontend
curl http://localhost:8080

# Expected: HTML response
```

### Step 3: Open Browser DevTools

```
1. Open Chrome/Safari
2. Press F12 (or Cmd+Option+I on Mac)
3. Go to Console tab
4. Go to Network tab
5. Keep DevTools open throughout testing
```

---

## 📋 Test Journey

### **PHASE 1: SIGNUP & ONBOARDING** (15 minutes)

#### Test 1.1: Access App

**Action**: Open browser and navigate to app
```
URL: http://localhost:8080
```

**Log**:
```
✅ ACTION: page_load
   Screen: landing
   Timestamp: [RECORD]
   Load Time: [CHECK NETWORK TAB]
```

**Expected**:
- App loads within 2 seconds
- Landing page or login screen appears
- No console errors

**Screenshot**: Take screenshot of initial screen

---

#### Test 1.2: Navigate to Signup

**Action**: Click "Sign Up" or "Create Account" button

**Log**:
```
✅ ACTION: button_tap
   Button: signup_button
   Screen: landing
   Timestamp: [RECORD]
```

**Expected**:
- Signup form appears
- Email, password, name fields visible
- Form is responsive

**Screenshot**: Signup form

---

#### Test 1.3: Fill Signup Form

**Action**: Enter test user details

**Test Data**:
```
Email: test_[TIMESTAMP]@manual.test
Password: TestPass123!
Name: Manual Test User
```

**Log**:
```
✅ ACTION: form_input
   Field: email
   Screen: signup
   Timestamp: [RECORD]

✅ ACTION: form_input
   Field: password
   Screen: signup
   Timestamp: [RECORD]

✅ ACTION: form_input
   Field: name
   Screen: signup
   Timestamp: [RECORD]
```

**Expected**:
- Fields accept input
- Password is masked
- No validation errors

---

#### Test 1.4: Submit Signup

**Action**: Click "Sign Up" button

**Log**:
```
✅ ACTION: form_submit
   Form: signup
   Screen: signup
   Timestamp: [RECORD]
```

**Check DevTools Network Tab**:
```
POST /auth/signup
Status: 200 OK
Response: {"uid": "...", "email": "...", "token": "..."}
```

**Expected**:
- Loading indicator appears
- Success message or redirect
- User is authenticated
- No errors in console

**Screenshot**: Success state

---

#### Test 1.5: Welcome Screen

**Action**: View welcome screen

**Log**:
```
✅ ACTION: screen_view
   Screen: onboarding_welcome
   Timestamp: [RECORD]
```

**Expected**:
- Welcome message with user's name
- "Get Started" or "Continue" button
- App branding visible

**Screenshot**: Welcome screen

---

#### Test 1.6: Basic Info - Height & Weight

**Action**: Enter height and weight

**Test Data**:
```
Height: 170 cm (or 5'7")
Weight: 70 kg (or 154 lbs)
Age: 30
Gender: Male/Female
```

**Log**:
```
✅ ACTION: form_input
   Field: height
   Value: 170
   Unit: cm
   Screen: onboarding_basic_info
   Timestamp: [RECORD]

✅ ACTION: form_input
   Field: weight
   Value: 70
   Unit: kg
   Screen: onboarding_basic_info
   Timestamp: [RECORD]

✅ ACTION: form_input
   Field: age
   Value: 30
   Screen: onboarding_basic_info
   Timestamp: [RECORD]

✅ ACTION: button_tap
   Button: gender_select
   Value: male
   Screen: onboarding_basic_info
   Timestamp: [RECORD]
```

**Expected**:
- Unit toggle works (Kg ↔ Lb, Cm ↔ Ft/In)
- Real-time validation
- "Next" button enabled

**Screenshot**: Filled form

---

#### Test 1.7: BMI Result Screen

**Action**: Click "Next" and view BMI

**Log**:
```
✅ ACTION: button_tap
   Button: next
   Screen: onboarding_basic_info
   Timestamp: [RECORD]

✅ ACTION: screen_view
   Screen: onboarding_bmi_result
   Timestamp: [RECORD]
```

**Expected**:
- BMI calculated and displayed
- BMI category shown (Normal/Overweight/etc.)
- Ideal weight range shown
- Suggested target weight

**Verify Calculation**:
```
BMI = weight(kg) / (height(m))²
Example: 70 / (1.70)² = 24.2

Expected: ~24.2 (Normal range)
```

**Screenshot**: BMI result

---

#### Test 1.8: Select Fitness Goal

**Action**: Choose fitness goal

**Test Data**: Select "Lose Weight" (or any goal)

**Log**:
```
✅ ACTION: button_tap
   Button: goal_select
   Value: lose_weight
   Screen: onboarding_fitness_goal
   Timestamp: [RECORD]
```

**Expected**:
- All goal options visible
- Selected goal highlighted
- Description updates

**Screenshot**: Goal selection

---

#### Test 1.9: Activity Level

**Action**: Select activity level

**Test Data**: Select "Moderately Active"

**Log**:
```
✅ ACTION: button_tap
   Button: activity_select
   Value: moderately_active
   Screen: onboarding_activity_level
   Timestamp: [RECORD]
```

**Expected**:
- Activity levels with descriptions
- Selected level highlighted

**Screenshot**: Activity selection

---

#### Test 1.10: Review & Calculate Goals

**Action**: Review and confirm

**Log**:
```
✅ ACTION: button_tap
   Button: calculate_goals
   Screen: onboarding_review
   Timestamp: [RECORD]

✅ ACTION: screen_view
   Screen: onboarding_setup_loading
   Timestamp: [RECORD]
```

**Check DevTools Network Tab**:
```
POST /fitness/calculate-goals
Status: 200 OK
Response: {
    "calories": 2000,
    "protein_g": 150,
    "carbs_g": 200,
    "fat_g": 67
}
```

**Expected**:
- Loading animation (4 steps)
- Goals calculated
- Success screen appears

**Screenshot**: Loading & Success

---

#### Test 1.11: Onboarding Complete

**Action**: View success screen

**Log**:
```
✅ ACTION: screen_view
   Screen: onboarding_success
   Timestamp: [RECORD]
```

**Expected**:
- Confetti animation
- Personalized message
- Daily goals displayed
- "Get Started" button

**Screenshot**: Success screen

---

### **PHASE 2: DASHBOARD & HOME** (10 minutes)

#### Test 2.1: Navigate to Dashboard

**Action**: Click "Get Started" or navigate to home

**Log**:
```
✅ ACTION: button_tap
   Button: get_started
   Screen: onboarding_success
   Timestamp: [RECORD]

✅ ACTION: screen_view
   Screen: home_dashboard
   Timestamp: [RECORD]
```

**Expected**:
- Dashboard loads
- Activity rings visible
- Today's progress shown
- Bottom navigation visible

**Screenshot**: Dashboard

---

#### Test 2.2: Verify Dashboard Data

**Action**: Review displayed information

**Check**:
```
✅ Calories: 0 / 2000 kcal
✅ Protein: 0g / 150g
✅ Carbs: 0g / 200g
✅ Fat: 0g / 67g
✅ Activity rings: Empty (0%)
✅ Meal timeline: Empty state
```

**Log**:
```
✅ ACTION: data_verification
   Screen: home_dashboard
   Calories_Goal: 2000
   Protein_Goal: 150
   Carbs_Goal: 200
   Fat_Goal: 67
   Timestamp: [RECORD]
```

**Expected**:
- All goals match calculated values
- Empty states have helpful messages
- No overlapping text
- Hamburger menu works

**Screenshot**: Dashboard with empty state

---

### **PHASE 3: AI CHAT & MEAL LOGGING** (20 minutes)

#### Test 3.1: Navigate to Chat

**Action**: Tap "Assistant" in bottom navigation

**Log**:
```
✅ ACTION: navigation_tap
   Tab: assistant
   From_Screen: home_dashboard
   To_Screen: chat
   Timestamp: [RECORD]

✅ ACTION: screen_view
   Screen: chat
   Timestamp: [RECORD]
```

**Expected**:
- Chat screen loads
- Empty state with welcome message
- Input field at bottom
- Send button visible

**Screenshot**: Chat empty state

---

#### Test 3.2: Log Simple Meal - "2 eggs"

**Action**: Type "2 eggs" and send

**Log**:
```
✅ ACTION: text_input
   Field: chat_message
   Value: "2 eggs"
   Screen: chat
   Timestamp: [RECORD]

✅ ACTION: button_tap
   Button: send_message
   Screen: chat
   Timestamp: [RECORD]
```

**Check DevTools Network Tab**:
```
POST /chat
Request: {"user_input": "2 eggs"}
Status: 200 OK
Response: {
    "items": [{
        "category": "meal",
        "data": {
            "calories": 140,
            "protein_g": 12,
            "carbs_g": 1,
            "fat_g": 10
        }
    }],
    "message": "✅ 2 eggs logged - 140 cal, 12g protein"
}
```

**Expected**:
- User message appears immediately
- AI response appears within 2 seconds
- Meal card shows:
  - Food name: "Egg, Large, Boiled"
  - Calories: 140 kcal
  - Protein: 12g
  - Carbs: 1g
  - Fat: 10g
- No errors

**Log**:
```
✅ ACTION: message_received
   Type: meal
   Food: eggs
   Calories: 140
   Response_Time: [MEASURE]
   Screen: chat
   Timestamp: [RECORD]
```

**Screenshot**: Chat with meal logged

---

#### Test 3.3: Verify Dashboard Updates

**Action**: Navigate back to dashboard

**Log**:
```
✅ ACTION: navigation_tap
   Tab: home
   From_Screen: chat
   To_Screen: home_dashboard
   Timestamp: [RECORD]
```

**Check**:
```
✅ Calories: 140 / 2000 kcal (7%)
✅ Protein: 12g / 150g (8%)
✅ Carbs: 1g / 200g (0.5%)
✅ Fat: 10g / 67g (15%)
✅ Activity ring: Partially filled
✅ Meal timeline: Shows "2 eggs" entry
```

**Expected**:
- Dashboard updated in real-time
- Activity rings show progress
- Meal appears in timeline
- Percentages correct

**Screenshot**: Dashboard with data

---

#### Test 3.4: Log Ambiguous Meal - "eggs"

**Action**: Go back to chat, type "eggs" (no quantity)

**Log**:
```
✅ ACTION: navigation_tap
   Tab: assistant
   Screen: chat
   Timestamp: [RECORD]

✅ ACTION: text_input
   Value: "eggs"
   Screen: chat
   Timestamp: [RECORD]

✅ ACTION: button_tap
   Button: send_message
   Screen: chat
   Timestamp: [RECORD]
```

**Expected**:
- User message: "eggs"
- AI response: "How many eggs? (e.g., '1 egg', '2 eggs')"
- No meal card created yet
- Clarification question visible

**Log**:
```
✅ ACTION: clarification_received
   Question: "How many eggs?"
   Screen: chat
   Timestamp: [RECORD]
```

**Screenshot**: Clarification question

---

#### Test 3.5: Answer Clarification

**Action**: Type "3" and send

**Log**:
```
✅ ACTION: text_input
   Value: "3"
   Screen: chat
   Timestamp: [RECORD]

✅ ACTION: button_tap
   Button: send_message
   Screen: chat
   Timestamp: [RECORD]
```

**Expected**:
- AI logs 3 eggs
- Meal card shows 210 kcal (3 × 70)
- Dashboard updates

**Screenshot**: Clarification answered

---

#### Test 3.6: Log Multi-Food Meal

**Action**: Type "2 eggs, 1 bowl rice, 5 pistachios"

**Log**:
```
✅ ACTION: text_input
   Value: "2 eggs, 1 bowl rice, 5 pistachios"
   Screen: chat
   Timestamp: [RECORD]

✅ ACTION: button_tap
   Button: send_message
   Screen: chat
   Timestamp: [RECORD]
```

**Expected**:
- 3 separate meal cards created:
  1. Eggs: ~140 kcal
  2. Rice: ~200 kcal
  3. Pistachios: ~15 kcal
- Total: ~355 kcal
- All cards show macros

**Log**:
```
✅ ACTION: multi_food_logged
   Foods: ["eggs", "rice", "pistachios"]
   Total_Calories: 355
   Items_Count: 3
   Screen: chat
   Timestamp: [RECORD]
```

**Screenshot**: Multi-food cards

---

#### Test 3.7: Verify Chat History

**Action**: Refresh browser (Cmd+Shift+R)

**Log**:
```
✅ ACTION: page_refresh
   Screen: chat
   Timestamp: [RECORD]
```

**Expected**:
- All previous messages visible
- User messages and AI responses
- Meal cards intact
- No data loss

**Screenshot**: Chat history after refresh

---

### **PHASE 4: PROFILE & SETTINGS** (10 minutes)

#### Test 4.1: Navigate to Profile

**Action**: Tap "Profile" in bottom navigation

**Log**:
```
✅ ACTION: navigation_tap
   Tab: profile
   From_Screen: chat
   To_Screen: profile
   Timestamp: [RECORD]

✅ ACTION: screen_view
   Screen: profile
   Timestamp: [RECORD]
```

**Expected**:
- Profile screen loads
- User info displayed
- Daily goals visible
- Settings options

**Screenshot**: Profile screen

---

#### Test 4.2: View Profile Details

**Action**: Review displayed information

**Check**:
```
✅ Name: Manual Test User
✅ Email: test_[timestamp]@manual.test
✅ Height: 170 cm
✅ Weight: 70 kg
✅ Age: 30
✅ Fitness Goal: Lose Weight
✅ Activity Level: Moderately Active
✅ Daily Calories: 2000
✅ Protein: 150g
✅ Carbs: 200g
✅ Fat: 67g
```

**Log**:
```
✅ ACTION: data_verification
   Screen: profile
   All_Fields_Correct: true
   Timestamp: [RECORD]
```

**Screenshot**: Profile details

---

### **PHASE 5: FEEDBACK SYSTEM** (10 minutes)

#### Test 5.1: Open Feedback Button

**Action**: Tap floating feedback button (bottom right)

**Log**:
```
✅ ACTION: button_tap
   Button: feedback_floating
   Screen: profile
   Timestamp: [RECORD]
```

**Expected**:
- Menu expands
- 4 options visible:
  - Report Bug
  - Suggest Feature
  - UX Feedback
  - General Feedback

**Screenshot**: Feedback menu

---

#### Test 5.2: Submit Bug Report

**Action**: Tap "Report Bug"

**Log**:
```
✅ ACTION: button_tap
   Button: report_bug
   Screen: profile
   Timestamp: [RECORD]

✅ ACTION: dialog_open
   Dialog: feedback_form
   Type: bug
   Timestamp: [RECORD]
```

**Expected**:
- Feedback dialog opens
- Title: "Report a Bug"
- Message field visible
- Screenshot button
- Follow-up checkbox

**Screenshot**: Feedback dialog

---

#### Test 5.3: Fill & Submit Feedback

**Action**: Fill form and submit

**Test Data**:
```
Message: "This is a test bug report for manual testing"
Screenshot: [Optional - add one]
Follow-up: ✓ Checked
```

**Log**:
```
✅ ACTION: form_input
   Field: feedback_message
   Value: "This is a test bug report..."
   Screen: feedback_dialog
   Timestamp: [RECORD]

✅ ACTION: checkbox_toggle
   Field: wants_followup
   Value: true
   Screen: feedback_dialog
   Timestamp: [RECORD]

✅ ACTION: button_tap
   Button: submit_feedback
   Screen: feedback_dialog
   Timestamp: [RECORD]
```

**Check DevTools Network Tab**:
```
POST /feedback/submit
Status: 200 OK
Response: {
    "feedback_id": "fb_abc123",
    "message": "Thanks for reporting! We've logged it...",
    "status": "received"
}
```

**Expected**:
- Success dialog appears
- Feedback ID shown
- Confirmation message
- "Done" button

**Screenshot**: Success confirmation

---

### **PHASE 6: ERROR HANDLING** (10 minutes)

#### Test 6.1: Network Error Simulation

**Action**: Open DevTools → Network tab → Enable "Offline"

**Log**:
```
✅ ACTION: network_offline
   Screen: chat
   Timestamp: [RECORD]
```

**Action**: Try to log a meal

**Expected**:
- Error message appears
- User-friendly text (not technical)
- Retry option available
- No crash

**Screenshot**: Offline error

---

#### Test 6.2: Invalid Input

**Action**: Type very long text (1000+ characters)

**Log**:
```
✅ ACTION: text_input
   Value: [1000 chars]
   Screen: chat
   Timestamp: [RECORD]
```

**Expected**:
- Validation error
- Character limit message
- Input prevented or truncated

**Screenshot**: Validation error

---

#### Test 6.3: Special Characters

**Action**: Type "<script>alert('test')</script>"

**Log**:
```
✅ ACTION: text_input
   Value: "<script>alert('test')</script>"
   Screen: chat
   Timestamp: [RECORD]
```

**Expected**:
- Input sanitized
- No script execution
- Safe handling

---

### **PHASE 7: LOGOUT & LOGIN** (5 minutes)

#### Test 7.1: Logout

**Action**: Tap hamburger menu → Logout

**Log**:
```
✅ ACTION: button_tap
   Button: hamburger_menu
   Screen: home_dashboard
   Timestamp: [RECORD]

✅ ACTION: button_tap
   Button: logout
   Screen: menu
   Timestamp: [RECORD]
```

**Expected**:
- Confirmation dialog
- "Are you sure?" message
- Logout successful
- Redirect to login

**Screenshot**: Logout confirmation

---

#### Test 7.2: Login with Same User

**Action**: Login with test user credentials

**Test Data**:
```
Email: [same as signup]
Password: TestPass123!
```

**Log**:
```
✅ ACTION: form_input
   Field: email
   Screen: login
   Timestamp: [RECORD]

✅ ACTION: form_input
   Field: password
   Screen: login
   Timestamp: [RECORD]

✅ ACTION: button_tap
   Button: login
   Screen: login
   Timestamp: [RECORD]
```

**Expected**:
- Login successful
- Dashboard loads
- Previous data intact
- Chat history preserved

**Screenshot**: Dashboard after login

---

## 📊 Test Summary Template

### Copy and fill this after testing:

```
=================================================================
MANUAL TEST REPORT
=================================================================

Test Date: [DATE]
Tester: [YOUR NAME]
Environment: Development (localhost)
Browser: [Chrome/Safari/etc] [VERSION]

-----------------------------------------------------------------
PHASE 1: SIGNUP & ONBOARDING
-----------------------------------------------------------------
✅/❌ Test 1.1: Access App
✅/❌ Test 1.2: Navigate to Signup
✅/❌ Test 1.3: Fill Signup Form
✅/❌ Test 1.4: Submit Signup
✅/❌ Test 1.5: Welcome Screen
✅/❌ Test 1.6: Basic Info
✅/❌ Test 1.7: BMI Result
✅/❌ Test 1.8: Fitness Goal
✅/❌ Test 1.9: Activity Level
✅/❌ Test 1.10: Calculate Goals
✅/❌ Test 1.11: Success Screen

Issues Found:
1. [DESCRIBE ANY ISSUES]

-----------------------------------------------------------------
PHASE 2: DASHBOARD & HOME
-----------------------------------------------------------------
✅/❌ Test 2.1: Navigate to Dashboard
✅/❌ Test 2.2: Verify Dashboard Data

Issues Found:
1. [DESCRIBE ANY ISSUES]

-----------------------------------------------------------------
PHASE 3: AI CHAT & MEAL LOGGING
-----------------------------------------------------------------
✅/❌ Test 3.1: Navigate to Chat
✅/❌ Test 3.2: Log Simple Meal
✅/❌ Test 3.3: Dashboard Updates
✅/❌ Test 3.4: Ambiguous Input
✅/❌ Test 3.5: Clarification
✅/❌ Test 3.6: Multi-Food
✅/❌ Test 3.7: Chat History

Issues Found:
1. [DESCRIBE ANY ISSUES]

-----------------------------------------------------------------
PHASE 4: PROFILE & SETTINGS
-----------------------------------------------------------------
✅/❌ Test 4.1: Navigate to Profile
✅/❌ Test 4.2: Profile Details

Issues Found:
1. [DESCRIBE ANY ISSUES]

-----------------------------------------------------------------
PHASE 5: FEEDBACK SYSTEM
-----------------------------------------------------------------
✅/❌ Test 5.1: Feedback Button
✅/❌ Test 5.2: Bug Report
✅/❌ Test 5.3: Submit Feedback

Issues Found:
1. [DESCRIBE ANY ISSUES]

-----------------------------------------------------------------
PHASE 6: ERROR HANDLING
-----------------------------------------------------------------
✅/❌ Test 6.1: Network Error
✅/❌ Test 6.2: Invalid Input
✅/❌ Test 6.3: Special Characters

Issues Found:
1. [DESCRIBE ANY ISSUES]

-----------------------------------------------------------------
PHASE 7: LOGOUT & LOGIN
-----------------------------------------------------------------
✅/❌ Test 7.1: Logout
✅/❌ Test 7.2: Login

Issues Found:
1. [DESCRIBE ANY ISSUES]

-----------------------------------------------------------------
OVERALL SUMMARY
-----------------------------------------------------------------
Total Tests: 27
Passed: [COUNT]
Failed: [COUNT]
Pass Rate: [PERCENTAGE]%

Critical Issues: [COUNT]
Major Issues: [COUNT]
Minor Issues: [COUNT]

Overall Assessment: [PASS/FAIL/NEEDS WORK]

=================================================================
```

---

## 🔍 What to Look For

### Performance
- ⏱️ Page load < 2 seconds
- ⏱️ API response < 500ms
- ⏱️ UI interactions < 100ms
- 🎨 Smooth animations (60fps)

### UI/UX
- 📱 Mobile-responsive
- 👆 Touch targets ≥ 44x44pt
- 🎨 No overlapping text
- 🌈 Consistent colors/fonts
- ✨ Loading states present
- 📝 Empty states helpful

### Functionality
- ✅ All features work
- 🔄 Data persists
- 🔐 Authentication secure
- 📊 Calculations accurate
- 💬 Chat intelligent
- 🐛 No crashes

### Errors
- ❌ No console errors
- 🔴 No 404/500 errors
- 🟡 Warnings acceptable
- 📝 Error messages friendly

---

## 📸 Screenshots Checklist

Take screenshots of:
1. ✅ Landing page
2. ✅ Signup form
3. ✅ Welcome screen
4. ✅ Basic info form
5. ✅ BMI result
6. ✅ Goal selection
7. ✅ Success screen
8. ✅ Dashboard (empty)
9. ✅ Dashboard (with data)
10. ✅ Chat (empty)
11. ✅ Chat (with messages)
12. ✅ Multi-food cards
13. ✅ Profile screen
14. ✅ Feedback dialog
15. ✅ Error states

---

## 🚀 Ready to Test!

**Start here:**
```bash
# 1. Clear cache
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
./stop-dev.sh
cd flutter_app && flutter clean && cd ..
./start-dev.sh

# 2. Open browser
open http://localhost:8080

# 3. Follow the guide above
# 4. Fill the test summary
# 5. Report issues
```

Good luck! 🎯

