# 🧪 Manual Testing Scenarios - Ready to Test!

## ✅ **Servers Running**

- **Backend**: http://localhost:8000 ✅
- **Frontend**: http://localhost:8080 ✅
- **Status**: All systems ready for testing!

---

## 📋 **Test Scenario 1: New User Signup & Complete Flow**

### **Step 1: Sign Up New Account** 👤

1. **Open Browser**
   ```
   URL: http://localhost:8080
   ```

2. **Click "Sign Up"**
   - Should see sign-up form

3. **Enter Details**
   ```
   Email: test_user_nov1_2025@test.com
   Password: TestPass123!
   Name: Test User Nov 1
   ```

4. **Click "Sign Up" Button**

5. **Expected Result** ✅
   - Account created successfully
   - Redirected to onboarding
   - No error messages

---

### **Step 2: Complete Onboarding - Basic Info** 📝

1. **Enter Basic Information**
   ```
   Height: 170 cm (or toggle to Ft/In: 5'7")
   Weight: 70 kg (or toggle to Lb: 154 lb)
   Age: 30
   Gender: Male/Female (select one)
   ```

2. **Click "Next" or "Continue"**

3. **Expected Result** ✅
   - BMI calculated and displayed
   - BMI category shown (e.g., "Normal", "Overweight")
   - Ideal weight range displayed
   - Smooth transition to next screen

---

### **Step 3: BMI Result Screen** 📊

1. **Review BMI Results**
   - Check BMI value (should be ~24.2 for 170cm, 70kg)
   - Check BMI category
   - Check ideal weight range

2. **Click "Continue"**

3. **Expected Result** ✅
   - Animated BMI visualization
   - Color-coded category (green/yellow/red)
   - Suggested target weight

---

### **Step 4: Select Activity Level** 🏃

1. **Choose Activity Level**
   ```
   Options:
   - Sedentary (little or no exercise)
   - Lightly Active (1-3 days/week)
   - Moderately Active (3-5 days/week)
   - Very Active (6-7 days/week)
   - Extra Active (athlete)
   ```

2. **Select One** (e.g., "Moderately Active")

3. **Click "Next"**

4. **Expected Result** ✅
   - Selection highlighted
   - Smooth transition

---

### **Step 5: Select Fitness Goal** 🎯

1. **Choose Fitness Goal**
   ```
   Options:
   - Lose Weight
   - Gain Weight
   - Maintain Weight
   - Improve Fitness
   ```

2. **Select One** (e.g., "Lose Weight")

3. **Enter Target Weight** (if applicable)
   ```
   Target: 65 kg
   ```

4. **Click "Calculate Goals"**

5. **Expected Result** ✅
   - Daily calorie target calculated (~1800 kcal for weight loss)
   - Macro breakdown shown:
     - Protein: ~135g (30%)
     - Carbs: ~180g (40%)
     - Fat: ~60g (30%)
   - Timeline estimate shown

---

### **Step 6: Review & Confirm Goals** 📋

1. **Review All Information**
   - Check daily calorie target
   - Check macro breakdown
   - Check timeline

2. **Click "Confirm" or "Start Journey"**

3. **Expected Result** ✅
   - Success animation (confetti)
   - Personalized message
   - Redirect to dashboard

---

### **Step 7: Explore Dashboard** 🏠

1. **Check Dashboard Elements**
   - [ ] Welcome message with your name
   - [ ] Today's date displayed
   - [ ] Activity rings (Calories, Protein, Carbs, Fat)
   - [ ] All rings at 0% (no meals logged yet)
   - [ ] "Log Food" button visible
   - [ ] Hamburger menu accessible

2. **Expected Result** ✅
   - Clean, modern UI
   - All elements visible
   - No overlapping text
   - Responsive layout

---

### **Step 8: Log First Meal** 🍳

1. **Click "Log Food" or Chat Icon**

2. **Type in Chat**
   ```
   Test 1: "2 eggs"
   ```

3. **Send Message**

4. **Expected Result** ✅
   - Message appears in chat
   - AI responds with:
     ```
     ✅ Logged: 2 eggs
     Calories: 140 kcal
     Protein: 12g
     Carbs: 1g
     Fat: 10g
     ```
   - Dashboard updates immediately
   - Activity rings animate
   - Calorie ring shows progress

---

### **Step 9: Log Multi-Food Meal** 🍽️

1. **Type in Chat**
   ```
   Test 2: "2 eggs, 1 bowl rice, 5 pistachios"
   ```

2. **Send Message**

3. **Expected Result** ✅
   - AI parses 3 separate items
   - Response shows:
     ```
     ✅ Logged 3 items:
     1. 2 eggs - 140 kcal
     2. 1 bowl rice - 300 kcal
     3. 5 pistachios - 15 kcal
     
     Total: 455 kcal
     ```
   - Dashboard updates with new totals
   - All rings update

---

### **Step 10: Test Ambiguous Input** ❓

1. **Type in Chat**
   ```
   Test 3: "eggs"
   ```

2. **Send Message**

3. **Expected Result** ✅
   - AI asks clarification question:
     ```
     How many eggs did you have?
     ```
   - Your original message visible in chat
   - AI's question visible

4. **Reply with**
   ```
   "3"
   ```

5. **Expected Result** ✅
   - AI logs 3 eggs
   - Calories calculated (210 kcal)
   - Dashboard updates

---

### **Step 11: Log Meal with Units** ⚖️

1. **Type in Chat**
   ```
   Test 4: "100g chicken breast"
   ```

2. **Send Message**

3. **Expected Result** ✅
   - AI logs chicken with correct macros:
     ```
     ✅ Logged: 100g chicken breast
     Calories: 165 kcal
     Protein: 31g
     Carbs: 0g
     Fat: 4g
     ```
   - Dashboard updates

---

### **Step 12: Check Dashboard Progress** 📊

1. **Review Dashboard**
   - [ ] Total calories = sum of all meals
   - [ ] Protein total correct
   - [ ] Carbs total correct
   - [ ] Fat total correct
   - [ ] Activity rings show correct percentages
   - [ ] Meal timeline shows all logged meals

2. **Expected Result** ✅
   - All numbers accurate
   - Rings animate smoothly
   - Timeline shows all meals with timestamps

---

### **Step 13: Test Meal Timeline** 📅

1. **Scroll Down to Meal Timeline**

2. **Check Each Meal Entry**
   - [ ] Meal name displayed
   - [ ] Calories shown
   - [ ] Timestamp shown
   - [ ] All meals in chronological order

3. **Expected Result** ✅
   - All meals visible
   - Clean card layout
   - Easy to read

---

### **Step 14: Test Navigation** 🧭

1. **Click Hamburger Menu**

2. **Navigate to Different Screens**
   - [ ] Home/Dashboard
   - [ ] Chat
   - [ ] Plan (goals)
   - [ ] Profile
   - [ ] Settings (if available)

3. **Expected Result** ✅
   - All screens load
   - Navigation smooth
   - No errors

---

### **Step 15: Test Profile Screen** 👤

1. **Go to Profile**

2. **Check Profile Data**
   - [ ] Name displayed
   - [ ] Email displayed
   - [ ] Height/Weight shown
   - [ ] BMI displayed
   - [ ] Goals shown

3. **Expected Result** ✅
   - All data matches what you entered
   - No missing fields

---

## 📋 **Test Scenario 2: Sign Out & Sign In**

### **Step 16: Sign Out** 🚪

1. **Open Hamburger Menu**

2. **Click "Sign Out" or "Logout"**

3. **Expected Result** ✅
   - Signed out successfully
   - Redirected to login/welcome screen
   - No errors

---

### **Step 17: Sign In with Same Account** 🔐

1. **Click "Sign In" or "Login"**

2. **Enter Credentials**
   ```
   Email: test_user_nov1_2025@test.com
   Password: TestPass123!
   ```

3. **Click "Sign In"**

4. **Expected Result** ✅
   - Logged in successfully
   - Redirected to dashboard
   - All previous data still there

---

### **Step 18: Verify Data Persistence** 💾

1. **Check Dashboard**
   - [ ] All previous meals still logged
   - [ ] Activity rings show same progress
   - [ ] Calorie totals match
   - [ ] Meal timeline shows all meals

2. **Expected Result** ✅
   - All data persisted
   - No data loss
   - Same state as before logout

---

### **Step 19: Log New Meal After Re-login** 🍎

1. **Open Chat**

2. **Type**
   ```
   Test 5: "1 apple, 200g spinach"
   ```

3. **Send Message**

4. **Expected Result** ✅
   - AI logs both items
   - Dashboard updates
   - New totals calculated
   - Meal added to timeline

---

### **Step 20: Test Refresh/Reload** 🔄

1. **Hard Refresh Browser**
   ```
   Mac: Cmd + Shift + R
   Windows: Ctrl + Shift + R
   ```

2. **Expected Result** ✅
   - Still logged in
   - All data still there
   - Dashboard loads correctly
   - No errors

---

## 🐛 **What to Look For (Bugs to Report)**

### **Critical Issues** 🔴
- [ ] Can't sign up
- [ ] Can't log in
- [ ] App crashes
- [ ] Data loss after logout
- [ ] Chat doesn't respond
- [ ] Meals not logging

### **Major Issues** 🟠
- [ ] Wrong calorie calculations
- [ ] Dashboard not updating
- [ ] Navigation broken
- [ ] BMI calculation wrong
- [ ] Goals calculation wrong

### **Minor Issues** 🟡
- [ ] Overlapping text
- [ ] Slow loading
- [ ] Animation glitches
- [ ] Typos
- [ ] Layout issues

### **UI/UX Issues** 🔵
- [ ] Confusing navigation
- [ ] Unclear labels
- [ ] Poor contrast
- [ ] Hard to read text
- [ ] Buttons too small

---

## 📊 **Expected Results Summary**

### **After Scenario 1** (New User)
```
✅ Account created
✅ Onboarding completed
✅ Goals calculated
✅ 5 meals logged:
   - 2 eggs (140 kcal)
   - 2 eggs, 1 bowl rice, 5 pistachios (455 kcal)
   - 3 eggs (210 kcal)
   - 100g chicken breast (165 kcal)
   - 1 apple, 200g spinach (100 kcal)

Total Calories: ~1070 kcal
Dashboard: All rings updated
Timeline: 5 meals visible
```

### **After Scenario 2** (Sign Out/In)
```
✅ Signed out successfully
✅ Signed in successfully
✅ All data persisted
✅ 1 new meal logged
✅ Total: 6 meals

Total Calories: ~1170 kcal
Dashboard: Updated with new meal
Timeline: 6 meals visible
```

---

## 🎯 **Testing Checklist**

### **Functionality** ✅
- [ ] Sign up works
- [ ] Sign in works
- [ ] Sign out works
- [ ] Onboarding works
- [ ] BMI calculation correct
- [ ] Goal calculation correct
- [ ] Chat works
- [ ] Meal logging works
- [ ] Multi-food parsing works
- [ ] Clarification questions work
- [ ] Dashboard updates
- [ ] Data persists
- [ ] Navigation works

### **UI/UX** ✅
- [ ] No overlapping text
- [ ] All buttons clickable
- [ ] Forms work correctly
- [ ] Animations smooth
- [ ] Responsive layout
- [ ] Readable text
- [ ] Clear navigation
- [ ] Good contrast

### **Data Accuracy** ✅
- [ ] Calories correct
- [ ] Macros correct
- [ ] BMI correct
- [ ] Goals correct
- [ ] Totals correct
- [ ] Percentages correct

---

## 📝 **How to Report Issues**

If you find any bugs, note:

1. **What you did** (exact steps)
2. **What you expected** (expected result)
3. **What happened** (actual result)
4. **Screenshot** (if possible)
5. **Browser** (Chrome, Safari, etc.)
6. **Time** (when it happened)

---

## 🚀 **Ready to Test!**

**Servers Running**:
- ✅ Backend: http://localhost:8000
- ✅ Frontend: http://localhost:8080

**Start Testing**:
1. Open http://localhost:8080 in your browser
2. Follow Scenario 1 (Steps 1-15)
3. Then follow Scenario 2 (Steps 16-20)
4. Report any issues you find

**Good luck with testing!** 🎯

---

**Last Updated**: 2025-11-01 11:15 AM


