# 🧪 Phase 2: Explainable AI - Testing Guide

**Status:** Backend + Frontend Running  
**Test Time:** 15-20 minutes  
**Goal:** Verify all Phase 2 features work correctly

---

## 🌐 **ACCESS THE APP**

**URL:** http://localhost:9000  
**Backend:** Running on port 8000  
**Frontend:** Running on port 9000

**Please open Chrome/Safari and navigate to: `http://localhost:9000`**

---

## 📋 **TESTING CHECKLIST**

### **✅ Test 1: High Confidence Response (2 min)**
**Purpose:** Test confidence badge, explanation sheet

**Steps:**
1. Log in to the app
2. Go to Chat tab
3. Type: `"2 large eggs, scrambled"`
4. Send the message

**Expected Results:**
- ✅ AI responds with meal logged
- ✅ **Confidence badge** appears (should be green, ~85-95%)
- ✅ **"Why?" button** appears next to badge
- ✅ **Feedback buttons** (👍/👎) appear at bottom

**Test the UI:**
- Tap the **Confidence Badge** (green percentage)
  - ✅ Bottom sheet should slide up
  - ✅ Shows "How AI Understood This"
  - ✅ Shows step-by-step reasoning
  - ✅ Shows data sources (USDA, etc.)
  - ✅ Shows assumptions (egg size, cooking method)
  - ✅ Shows confidence breakdown with progress bars
  - ✅ "Got it" button closes the sheet

- Tap the **"Why?" button**
  - ✅ Same explanation sheet should open

**Screenshot areas:**
- Confidence badge in green
- Explanation sheet with full reasoning

---

### **✅ Test 2: Medium Confidence with Alternatives (3 min)**
**Purpose:** Test alternative picker

**Steps:**
1. In Chat tab, type: `"chicken"`
2. Send the message

**Expected Results:**
- ✅ AI responds with meal logged
- ✅ **Confidence badge** appears (should be yellow/orange, ~70-80%)
- ✅ **Alternative picker** appears (⚠️ "I'm not 100% sure. Did you mean:")
- ✅ Shows 2-3 alternatives:
  - Small portion (115 kcal)
  - Standard portion (165 kcal) - pre-selected
  - Large portion (215 kcal)
  - Possibly: Fried chicken (231 kcal)
- ✅ Each alternative shows:
  - Radio button
  - Description
  - Calorie count
  - Confidence percentage
  - Explanation text

**Test the UI:**
- Select different alternatives
  - ✅ Radio button changes
  - ✅ Selection is highlighted

- Tap **"Confirm"** button
  - ✅ Shows success message
  - ✅ "Updated! Thanks for the feedback."

- Tap **"Something else"** button
  - ✅ Dialog opens asking "What did you mean?"
  - ✅ Text input available
  - ✅ Can submit correction

**Screenshot areas:**
- Alternative picker with multiple options
- Selected alternative highlighted
- Confirmation success message

---

### **✅ Test 3: Explanation Sheet Details (2 min)**
**Purpose:** Verify explanation completeness

**Steps:**
1. Type: `"1 orange"`
2. Send and tap "Why?" button

**Expected Results:**
In the explanation sheet, verify:
- ✅ **Reasoning section:**
  - "1. You said 'X'"
  - "2. Identified Y as food"
  - "3. Looked up nutrition data"
  - "4. Calculated Z calories"
  - "5. Checked progress: X remaining"

- ✅ **Data Sources section:**
  - Lists sources (USDA, Standard portions, etc.)
  - Bullet points for each

- ✅ **Assumptions section:**
  - Lists what AI assumed
  - Example: "Medium-sized orange"
  - Example: "Assumed breakfast/lunch/dinner"

- ✅ **Classification section:**
  - "Why This Classification" explanation
  - Time-based reasoning if applicable

- ✅ **Confidence Factors:**
  - Progress bars for each factor
  - Input clarity: X%
  - Data completeness: X%
  - Model certainty: X%
  - Color-coded (green for high, yellow for medium, red for low)

**Screenshot areas:**
- Full explanation sheet
- Confidence factor progress bars

---

### **✅ Test 4: Feedback Buttons (2 min)**
**Purpose:** Test feedback collection UI

**Steps:**
1. After any AI response, find feedback buttons at bottom
2. Tap **👍 (Thumbs Up)**

**Expected Results:**
- ✅ Button lights up (blue background)
- ✅ Shows "Thanks for the feedback!"
- ✅ Checkmark icon appears

**Steps:**
3. In a new message, tap **👎 (Thumbs Down)**

**Expected Results:**
- ✅ **Correction Dialog** opens
- ✅ Title: "Help AI Learn"
- ✅ Shows checkboxes:
  - Wrong food item
  - Wrong quantity
  - Wrong calories
  - Wrong meal timing
  - Other
- ✅ Text input: "Tell us more (optional)"
- ✅ Cancel and Submit buttons

**Test the dialog:**
- Select a checkbox
  - ✅ Checkbox is checked
- Type in text field
  - ✅ Can enter text
- Tap **Submit**
  - ✅ Dialog closes
  - ✅ Shows "Feedback received. AI will learn from this!"

**Screenshot areas:**
- Feedback buttons
- Correction dialog
- Success message

---

### **✅ Test 5: Multiple Chat Messages (2 min)**
**Purpose:** Verify Phase 2 works across different message types

**Test these inputs:**
1. `"2 eggs"`
   - ✅ High confidence (green badge)
   - ✅ No alternatives

2. `"some chicken"`
   - ✅ Medium confidence (yellow/orange badge)
   - ✅ Shows alternatives (vague quantity)

3. `"rice"`
   - ✅ Medium confidence
   - ✅ Shows alternatives (no quantity + no prep method)

4. `"150g grilled chicken breast"`
   - ✅ Very high confidence (green badge ~90%+)
   - ✅ No alternatives (very specific)

5. `"1 banana"`
   - ✅ High confidence
   - ✅ Explanation shows assumptions about size

**Expected:** Confidence varies appropriately based on input clarity

---

### **✅ Test 6: Expandable Chat Integration (2 min)**
**Purpose:** Verify Phase 2 works with existing expandable chat

**Steps:**
1. Send: `"2 eggs + 1 toast for breakfast"`
2. Verify the response shows:
   - ✅ Summary: "🍳 2 eggs + toast logged! 350 kcal"
   - ✅ Confidence badge (top right)
   - ✅ "Why?" button
   - ✅ Suggestion: "💡 Great protein! 🥚"
   - ✅ "More details" button (expandable)
   - ✅ Feedback buttons (👍/👎)

3. Tap **"More details"**
   - ✅ Expands to show nutrition breakdown
   - ✅ Shows progress bar
   - ✅ Phase 2 features still visible

4. Tap confidence badge or "Why?"
   - ✅ Explanation sheet opens ON TOP of expanded details
   - ✅ No UI conflicts

**Screenshot areas:**
- Full message with all Phase 2 + expandable chat features
- Expanded view with Phase 2 features

---

### **✅ Test 7: Performance Check (1 min)**
**Purpose:** Verify no performance degradation

**Steps:**
1. Open browser DevTools (F12 or Cmd+Option+I)
2. Go to Network tab
3. Send a chat message: `"2 eggs"`
4. Check the `/chat` request

**Expected Results:**
- ✅ Response time: < 5 seconds total
- ✅ No console errors
- ✅ Smooth animations (confidence badge fade-in, sheet slide-up)
- ✅ No UI lag

**Check backend logs:**
- ✅ Phase 2 processing time should show: "PHASE 2 - Explainable AI: X ms"
- ✅ Should be < 5ms
- ✅ Confidence score logged: "Confidence: 0.XX (high/medium/low)"

---

### **✅ Test 8: Edge Cases (2 min)**
**Purpose:** Test unusual scenarios

**Test these:**
1. Very short input: `"egg"`
   - ✅ Lower confidence (missing quantity)
   - ✅ Shows alternatives or clarification

2. Very detailed input: `"2 large eggs, scrambled with 1 tbsp olive oil, and 2 slices of whole wheat toast"`
   - ✅ Very high confidence (90%+)
   - ✅ No alternatives needed

3. Ambiguous input: `"food"`
   - ✅ Very low confidence
   - ✅ Might trigger clarification
   - ✅ If not, shows low confidence badge

4. Multiple items: `"2 eggs + 1 toast + 1 banana"`
   - ✅ Confidence calculated for entire input
   - ✅ Phase 2 features present

---

## 📊 **TESTING SCORECARD**

| Feature | Status | Notes |
|---------|--------|-------|
| Confidence Badge (High) | ⬜ | Green, 85-100% |
| Confidence Badge (Medium) | ⬜ | Yellow, 70-85% |
| Confidence Badge (Low) | ⬜ | Orange/Red, <70% |
| "Why?" Button | ⬜ | Opens explanation |
| Explanation Sheet | ⬜ | All sections present |
| Reasoning Steps | ⬜ | Clear and logical |
| Data Sources | ⬜ | Listed correctly |
| Assumptions | ⬜ | Disclosed properly |
| Confidence Breakdown | ⬜ | Progress bars work |
| Alternative Picker | ⬜ | Shows 2-3 options |
| Alternative Selection | ⬜ | Radio buttons work |
| Confirm Button | ⬜ | Success feedback |
| Something Else Button | ⬜ | Opens text input |
| Feedback 👍 | ⬜ | Lights up, shows thanks |
| Feedback 👎 | ⬜ | Opens correction dialog |
| Correction Dialog | ⬜ | All options present |
| Submit Feedback | ⬜ | Success message |
| Expandable Chat Integration | ⬜ | No conflicts |
| Performance | ⬜ | < 5s response time |
| No Errors | ⬜ | Console clean |

---

## 🐛 **IF YOU FIND ISSUES**

### **Issue: Confidence badge not showing**
**Check:**
- Backend logs: Look for "🧠 [PHASE 2] Confidence: X.XX"
- If not present, Phase 2 might have errored (check for warnings)

### **Issue: Explanation sheet empty**
**Check:**
- Backend logs: Look for explanation data
- Console errors in browser DevTools

### **Issue: Alternatives not showing**
**Check:**
- Confidence score should be < 0.85 for alternatives
- If confidence is high (>0.85), alternatives won't show (by design)

### **Issue: Feedback buttons not working**
**Check:**
- Console errors
- Message ID should be present

---

## ✅ **AFTER TESTING**

### **If Everything Works:**
🎉 **Phase 2 is production-ready!**

Next steps:
1. ✅ Mark all features as tested
2. 🚀 Deploy to production, OR
3. 🔧 Start Phase 3 (Continuous Learning)

### **If Issues Found:**
1. 📝 Document the issue
2. 🐛 I'll fix it immediately
3. 🔄 Retest

---

## 📸 **RECOMMENDED SCREENSHOTS**

Please take screenshots of:
1. ✨ High confidence message (green badge + "Why?" button)
2. ⚠️ Medium confidence message (alternatives shown)
3. 🧠 Explanation sheet (full view)
4. 📊 Confidence breakdown (progress bars)
5. 🔄 Alternative picker (with selection)
6. 👍 Feedback buttons (with correction dialog)

---

**Ready to test!** 🚀  
**URL:** http://localhost:9000  
**Time:** 15-20 minutes  
**Have fun exploring the explainable AI!** 🧠✨

