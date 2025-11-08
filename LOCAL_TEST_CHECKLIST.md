# 🧪 Local Testing Checklist - Quick Smoke Test

**Date**: November 4, 2025  
**Backend**: ✅ Running on http://localhost:8000  
**Frontend**: ✅ Running on http://localhost:9000  
**Tester**: _____________  

---

## 🚀 Pre-Test Setup

- [x] Backend running (verified at http://localhost:8000/health)
- [x] Frontend running (opening in Chrome at http://localhost:9000)
- [ ] Logged in with test account
- [ ] Console open (F12) to check for errors

---

## 📋 Quick Smoke Test (15 minutes)

### **1. Profile Edit** ✏️ (2 min)
- [ ] Navigate to Profile tab
- [ ] Click "Edit Profile" button
- [ ] Change your name
- [ ] Click "Save"
- [ ] ✅ Verify: Name updated on profile screen
- [ ] ✅ Verify: Success message appeared
- [ ] ❌ Issues: _______________

### **2. Calorie Info Tooltip** ℹ️ (1 min)
- [ ] Go to Home screen
- [ ] Find "Calories" card
- [ ] Click the info icon (ℹ️) next to "Calories"
- [ ] ✅ Verify: Modal appears with explanation
- [ ] ✅ Verify: Can close modal
- [ ] Click info icon next to "Macros"
- [ ] ✅ Verify: Macro info modal appears
- [ ] ❌ Issues: _______________

### **3. Empty States** 🎨 (2 min)
- [ ] If you have meals logged, skip this
- [ ] If no meals: ✅ Verify "No Meals Logged Yet" appears
- [ ] ✅ Verify: "Log a Meal" button present
- [ ] Click button → ✅ Verify: Navigates to chat
- [ ] Scroll to Activity card
- [ ] If no workouts: ✅ Verify empty state appears
- [ ] ❌ Issues: _______________

### **4. Enhanced Workout Display** 💪 (2 min)
- [ ] Open Chat
- [ ] Type: "I did 30 min cardio"
- [ ] Send message
- [ ] Wait for AI response
- [ ] Go back to Home screen
- [ ] Scroll to Activity card
- [ ] ✅ Verify: Green success card appears
- [ ] ✅ Verify: "1 Workout Completed" text
- [ ] ✅ Verify: Checkmark icon visible
- [ ] ❌ Issues: _______________

### **5. Water Widget** 💧 (2 min)
- [ ] Scroll to Water Intake widget on Home
- [ ] ✅ Verify: Widget displays with progress bar
- [ ] ✅ Verify: Glass icons visible
- [ ] Open Chat
- [ ] Type: "I drank 250ml water"
- [ ] Send message
- [ ] Go back to Home
- [ ] ✅ Verify: Water widget updated
- [ ] ✅ Verify: Glass count increased
- [ ] ❌ Issues: _______________

### **6. Macro Rings** 📊 (1 min)
- [ ] On Home screen, find Macros section
- [ ] ✅ Verify: Circular rings visible next to macros card
- [ ] ✅ Verify: 3 rings (blue, yellow, purple)
- [ ] ✅ Verify: Rings show progress
- [ ] ❌ Issues: _______________

### **7. Date Toggle** 📅 (2 min)
- [ ] On Home screen, look below header
- [ ] ✅ Verify: Date Toggle widget appears
- [ ] ✅ Verify: "Today" button is highlighted
- [ ] Click "Yesterday" button
- [ ] ✅ Verify: Button becomes highlighted
- [ ] ✅ Verify: Dashboard data updates
- [ ] Click left chevron (previous day)
- [ ] ✅ Verify: Date moves back
- [ ] Click "Today" button
- [ ] ✅ Verify: Returns to today
- [ ] ❌ Issues: _______________

### **8. Dark Mode** 🌙 (2 min)
- [ ] Open Settings (gear icon)
- [ ] Find "Dark Mode" toggle
- [ ] Toggle ON
- [ ] ✅ Verify: Theme changes immediately to dark
- [ ] ✅ Verify: All screens use dark theme
- [ ] Navigate to Profile → ✅ Dark theme
- [ ] Navigate to Chat → ✅ Dark theme
- [ ] Navigate to Timeline → ✅ Dark theme
- [ ] Toggle OFF
- [ ] ✅ Verify: Returns to light theme
- [ ] ❌ Issues: _______________

### **9. Meal Search** ⭐ (1 min)
- [ ] Navigate to `/meals/search` (or find search button)
- [ ] ✅ Verify: Search screen loads
- [ ] Type "chicken" in search bar
- [ ] ✅ Verify: Results appear
- [ ] Click heart icon on a meal
- [ ] ✅ Verify: Heart fills with red
- [ ] ✅ Verify: Animation plays
- [ ] ❌ Issues: _______________

### **10. Reminders** ⏰ (1 min)
- [ ] Open Settings → Click "Reminders"
- [ ] ✅ Verify: Reminders screen loads
- [ ] Enable "Breakfast" reminder
- [ ] Set time to 8:00 AM
- [ ] Click "Save"
- [ ] ✅ Verify: Success message appears
- [ ] ❌ Issues: _______________

---

## 🔍 Console Check

- [ ] Open browser console (F12)
- [ ] Check for errors (red messages)
- [ ] ✅ Verify: No critical errors
- [ ] ❌ Errors found: _______________

---

## 📊 Results Summary

### **Features Tested**: ____ / 10
### **Features Passing**: ____ / 10
### **Critical Issues**: ____
### **Minor Issues**: ____

### **Overall Status**:
- [ ] ✅ All tests passing - Ready for production
- [ ] ⚠️ Minor issues - Can deploy with notes
- [ ] ❌ Critical issues - Need fixes before deployment

---

## 🐛 Issues Found

### **Critical Issues** (Must fix before production)
1. _______________
2. _______________

### **Minor Issues** (Can fix later)
1. _______________
2. _______________

### **Notes**
_______________
_______________
_______________

---

## ✅ Sign-Off

**Tested By**: _____________  
**Date**: _____________  
**Time**: _____________  
**Approved for Production**: [ ] YES [ ] NO  

---

## 📝 Next Steps

If all tests pass:
1. ✅ Mark this checklist complete
2. 🚀 Proceed to production deployment
3. 📊 Follow `TIER_1_2_3_DEPLOYMENT_PLAN.md`

If issues found:
1. 🐛 Document issues above
2. 🔧 Fix critical issues
3. 🔄 Re-test
4. ✅ Then proceed to production

---

**Happy Testing! 🧪**

