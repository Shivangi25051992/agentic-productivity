# 🧪 Meal Planning Feature - Manual Testing Guide

**Date**: November 5, 2025  
**Backend**: http://localhost:8000  
**Frontend**: http://localhost:9000  
**Testing Time**: ~15-20 minutes  

---

## ✅ Prerequisites

### Services Running
- [x] Backend running on port 8000
- [x] Frontend running on port 9000 (Chrome)
- [ ] Logged in to the app

### How to Check
```bash
# Backend health
curl http://localhost:8000/health

# Frontend (should return 200)
curl -I http://localhost:9000
```

---

## 🎯 Test Scenarios

### **Test 1: Access Meal Planning Tab** (2 min)

#### Steps:
1. Open http://localhost:9000 in Chrome
2. If not logged in, sign up/login with your Google account
3. Navigate to the **Plan** tab (bottom navigation)
4. You should see two tabs: "Fasting" and "Meal Planning"
5. Click on the **"Meal Planning"** tab

#### Expected Results:
- ✅ Meal Planning tab loads successfully
- ✅ You see a weekly day selector (Sun-Sat)
- ✅ Today's date is highlighted
- ✅ Empty state message: "No meals planned for this day"
- ✅ "Generate Meal Plan" button is visible
- ✅ "View Grocery List" button is visible

#### Screenshots:
📸 Take a screenshot if there are any issues

---

### **Test 2: Generate AI Meal Plan** (3-5 min)

#### Steps:
1. Click the **"Generate Meal Plan"** button
2. You should see a beautiful form with:
   - Dietary preferences chips (Vegetarian, Vegan, Keto, etc.)
   - Calorie slider (1200-4000)
   - Protein slider (50-300g)
   - Prep time selector (Quick, Medium, Long)
   - Number of people (1-10)

3. **Select your preferences:**
   - Select "High Protein" and "Low Carb"
   - Set calories to 2000
   - Set protein to 150g
   - Keep prep time as "Medium"
   - Keep 1 person
   
4. Click **"Generate Meal Plan"** button

5. **Wait 30-60 seconds** for AI to generate the plan
   - You should see a loading indicator
   - Progress message: "AI is generating your personalized meal plan..."

#### Expected Results:
- ✅ Form loads with all options visible
- ✅ Can select multiple dietary preferences
- ✅ Sliders work smoothly
- ✅ Generate button shows loading state
- ✅ After generation, you're returned to the meal planning tab
- ✅ Weekly calendar now shows meals for each day
- ✅ Success message appears

#### What the AI Generates:
- 7 days of meals (breakfast, lunch, dinner)
- Each meal has:
  - Recipe name
  - Calorie count
  - Protein, carbs, fat breakdown
  - Meal time (e.g., 8:00 AM, 12:00 PM, 7:00 PM)
  - Cooking time

#### Common Issues:
- ⚠️ If generation takes more than 2 minutes, check backend logs
- ⚠️ If you get an error about OpenAI API key, check your `.env` file
- ⚠️ If the plan doesn't appear, try refreshing the page

---

### **Test 3: View Daily Meals** (2 min)

#### Steps:
1. On the Meal Planning tab, click through different days of the week
2. Click **"Yesterday"**, **"Today"**, **"Tomorrow"** in the day selector
3. For each day with meals, observe the meal cards

#### Expected Results for Each Day:
- ✅ Daily nutrition summary card shows:
  - Total calories for the day
  - Total protein for the day
  - Progress bars (if goals are set)
  - Beautiful gradient background

- ✅ Three meal cards visible:
  - **Breakfast** (morning icon, salmon/pink color)
  - **Lunch** (sun icon, orange color)
  - **Dinner** (moon icon, indigo color)

- ✅ Each meal card shows:
  - Recipe name
  - Meal time (e.g., "8:00 AM")
  - Calories (e.g., "520 kcal")
  - Macros: P: 35g | C: 45g | F: 18g
  - Cooking time: "25 min"

- ✅ Tapping a meal card shows more details (if implemented)

#### Visual Check:
- Cards are beautifully styled with shadows
- Icons are colorful and appropriate
- Text is readable
- Layout is clean and organized

---

### **Test 4: Generate Grocery List** (3-5 min)

#### Steps:
1. From the Meal Planning tab, click **"View Grocery List"** button
2. If no list exists, you should see a button to generate one
3. Click **"Generate Grocery List"**
4. Wait 5-10 seconds for generation

#### Expected Results:
- ✅ Grocery list screen opens
- ✅ Progress card at top shows:
  - "0 / X items checked"
  - Progress bar (empty initially)
  - "Let's get shopping! 🛒" message

- ✅ Items are categorized:
  - **Produce** (green) - Fruits, vegetables
  - **Meat & Seafood** (red) - Chicken, fish, etc.
  - **Dairy** (blue) - Milk, cheese, yogurt
  - **Grains** (yellow) - Rice, pasta, bread
  - **Pantry** (orange) - Spices, oils, sauces
  - **Frozen** (cyan) - Frozen items
  - **Beverages** (purple) - Drinks
  - **Snacks** (pink) - Snack items
  - **Condiments** (brown) - Sauces, condiments

- ✅ Each item shows:
  - Checkbox (unchecked)
  - Item name
  - Quantity and unit (e.g., "2 lbs", "1 cup")

#### Sample Items You Might See:
```
Produce (Green)
○ Broccoli - 1 head
○ Spinach - 2 cups
○ Bell Peppers - 3 pieces

Meat & Seafood (Red)
○ Chicken Breast - 1.5 lbs
○ Salmon - 8 oz

Pantry (Orange)
○ Olive Oil - 3 tbsp
○ Garlic - 4 cloves
```

---

### **Test 5: Check Off Grocery Items** (2 min)

#### Steps:
1. On the grocery list, tap the checkbox next to any item
2. Check off 5-10 items
3. Observe the changes

#### Expected Results:
- ✅ Checkbox fills with checkmark (✓)
- ✅ Item text gets strikethrough
- ✅ Smooth animation on check/uncheck
- ✅ Progress bar at top updates in real-time
- ✅ Item count updates (e.g., "5 / 25 items checked")
- ✅ When reaching 50%, message changes to "Great progress! 💪"
- ✅ When reaching 100%, message changes to "All done! 🎉"

#### Interactive Test:
- Try checking and unchecking items quickly
- Progress should update smoothly
- No lag or glitches

---

### **Test 6: Navigate Between Days** (2 min)

#### Steps:
1. Go back to Meal Planning tab
2. Use the day selector to navigate:
   - Click on individual days (Sun, Mon, Tue, etc.)
   - Use left/right arrows to move days
   - Click "Today" button to jump to current day

#### Expected Results:
- ✅ Clicking a day highlights it
- ✅ Meals for that day load immediately
- ✅ Arrow buttons navigate forward/backward
- ✅ "Today" button always returns to current day
- ✅ Smooth transitions between days
- ✅ No loading delays

---

### **Test 7: Edit/Delete Meals** (1 min)

#### Steps:
1. Long-press or right-click on any meal card
2. Look for edit/delete options

#### Expected Results:
- ⏳ **If not implemented**: No options appear (this is a future feature)
- ✅ **If implemented**: Context menu with Edit/Delete options

*Note: This feature may not be implemented yet according to the roadmap*

---

## 🐛 Bug Tracking

### Issues Found

#### Issue #1:
- **Description**: _______________
- **Steps to Reproduce**: _______________
- **Severity**: Critical / High / Medium / Low
- **Screenshot**: _______________

#### Issue #2:
- **Description**: _______________
- **Steps to Reproduce**: _______________
- **Severity**: Critical / High / Medium / Low

---

## 📊 Test Results Summary

### Features Tested: ____ / 7

| Feature | Status | Notes |
|---------|--------|-------|
| 1. Access Meal Planning Tab | ⬜ Pass ⬜ Fail | |
| 2. Generate AI Meal Plan | ⬜ Pass ⬜ Fail | |
| 3. View Daily Meals | ⬜ Pass ⬜ Fail | |
| 4. Generate Grocery List | ⬜ Pass ⬜ Fail | |
| 5. Check Off Items | ⬜ Pass ⬜ Fail | |
| 6. Navigate Between Days | ⬜ Pass ⬜ Fail | |
| 7. Edit/Delete Meals | ⬜ Pass ⬜ Fail | |

---

## 🎨 UI/UX Quality Check

### Visual Design
- [ ] Colors are consistent and appealing
- [ ] Icons are appropriate and clear
- [ ] Typography is readable
- [ ] Spacing feels natural
- [ ] Animations are smooth

### User Experience
- [ ] Navigation is intuitive
- [ ] Loading states are clear
- [ ] Error messages are helpful
- [ ] Empty states are informative
- [ ] Actions have immediate feedback

### Performance
- [ ] Pages load quickly (< 1 second)
- [ ] No lag when scrolling
- [ ] Smooth animations (60 FPS)
- [ ] No memory issues or crashes

---

## 🔍 Backend API Testing (Optional)

If you want to test the backend directly:

### Check Meal Plans
```bash
# Get your auth token from browser (F12 → Application → Local Storage → firebase:authUser)
TOKEN="your_token_here"

# Get current week's meal plans
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/meal-planning/meal-plans?start_date=2025-11-05&end_date=2025-11-12"

# Get today's meals
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/meal-planning/meals/by-date/2025-11-05"
```

### Check Grocery List
```bash
# Get grocery lists
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/meal-planning/grocery-lists"

# Check off an item
curl -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"checked": true}' \
  "http://localhost:8000/meal-planning/grocery-lists/{list_id}/items/{item_id}"
```

---

## ✅ Sign-Off

**Tested By**: _____________  
**Date**: _____________  
**Time Spent**: _____ minutes  
**Overall Status**: [ ] All Pass [ ] Some Issues [ ] Critical Issues  

**Recommendation**:
- [ ] ✅ Ready for production
- [ ] ⚠️ Minor fixes needed
- [ ] ❌ Major issues, needs rework

**Notes**:
_______________________________________________
_______________________________________________
_______________________________________________

---

## 🚀 Next Steps

After testing:

1. **If all tests pass**:
   - Document any UX improvements
   - Prepare for production deployment
   - Update user documentation

2. **If issues found**:
   - Log all issues in GitHub/Jira
   - Prioritize by severity
   - Fix critical issues first
   - Re-test after fixes

3. **Feedback**:
   - Share with team
   - Gather user feedback
   - Plan next iteration

---

**Happy Testing! 🧪✨**

