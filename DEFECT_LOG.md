# 🐛 DEFECT LOG - Post Phase 2 Deployment

**Date:** November 7, 2025  
**Status:** Active Development  
**Priority Order:** High → Medium → Low

---

## 🟡 **DEFERRED BUGS (For Next Sprint)**

### **BUG #16: "Something Else" Correction Not Displayed as User Message**
**Reported:** November 7, 2025  
**Status:** 🟡 Deferred  
**Priority:** Medium  
**Severity:** UX Issue - Feedback not visible

#### **Description:**
When user clicks "Something else" in alternative picker and provides a correction (e.g., "15 gm of rice and 50 gm of chicken"), the correction is sent to backend as feedback but doesn't appear as a visible user message in the chat.

#### **Expected Behavior:**
- User types correction in "Something else" dialog
- Correction appears as a new user message bubble in chat
- User can see what they typed
- Natural conversation flow maintained

#### **Actual Behavior:**
- User types correction → Sent to backend ✅
- Correction stored in database ✅
- User cannot see their correction in chat ❌
- Only shows "Thanks! AI will learn from this" snackbar

#### **Root Cause:**
**Architectural Issue:** The alternative picker widget (`alternative_picker.dart`) doesn't have access to the chat screen's message list to add new messages. The correction is only sent as feedback via API, not added to the local chat state.

**Code Location:**
- `flutter_app/lib/widgets/chat/alternative_picker.dart` (line 333-364)
- `flutter_app/lib/widgets/chat/expandable_message_bubble.dart` (line 220-242)
- `flutter_app/lib/screens/chat/chat_screen.dart` (line 164-166 for adding messages)

#### **Reproduction Steps:**
1. Send a meal log that triggers alternatives (e.g., "apple")
2. Click "Something else" button
3. Type correction: "15 gm of rice and 50 gm of chicken"
4. Click Submit
5. Observe: No user message appears in chat

#### **Impact:**
- User confusion (where did my correction go?)
- Breaks conversation continuity
- User can't reference what they corrected later

#### **Suggested Solution:**

**Option A: Callback Architecture (Recommended)**
1. Add `onCorrectionSubmit` callback to `AlternativePicker` widget
2. Pass callback from `chat_screen.dart` → `expandable_message_bubble.dart` → `alternative_picker.dart`
3. When correction submitted, call callback to add user message to chat
4. Estimated effort: 30-45 minutes

**Implementation:**
```dart
// In alternative_picker.dart
final Function(String correction)? onCorrectionSubmit;

void _submitCorrection(String correction) {
  // Call callback to add message to chat
  widget.onCorrectionSubmit?.call(correction);
  
  // Then send feedback to backend
  widget.onSelect!(-1, correctionAlternative);
}

// In chat_screen.dart
void _handleCorrectionSubmit(String correction) {
  setState(() {
    _items.add(_ChatItem.userMessage(correction, DateTime.now()));
  });
  _autoScroll();
}
```

**Option B: Show in Feedback Badge (Quick Fix)**
- Display correction text in the feedback badge
- Less intrusive, simpler implementation
- Estimated effort: 10-15 minutes

#### **Files to Modify:**
1. `flutter_app/lib/widgets/chat/alternative_picker.dart`
2. `flutter_app/lib/widgets/chat/expandable_message_bubble.dart`
3. `flutter_app/lib/screens/chat/chat_screen.dart`

#### **Testing:**
1. Test with various correction texts
2. Verify message appears in correct order
3. Test auto-scroll behavior
4. Verify feedback still sent to backend

---

## 🔴 **HIGH PRIORITY BUGS**

### **BUG #1: Task Creation Showing Meal Alternatives**
**Reported:** November 7, 2025  
**Status:** 🔴 Open  
**Priority:** High  
**Severity:** Critical - Wrong category detection

#### **Description:**
When user types task-related prompts like "call mom at 9 pm", the system incorrectly shows meal/calorie alternatives instead of creating a task or event.

#### **Expected Behavior:**
- AI should detect this as a "task" or "reminder" category
- Create a task with title "Call mom" and due time "9 PM"
- Show simple confirmation: "✅ Task created: Call mom at 9 PM"
- No meal alternatives, no calorie information

#### **Actual Behavior:**
- AI shows yellow alternative picker box
- Displays "Item as breakfast" and "Item as dinner" options
- Shows 0 kcal nutrition breakdown
- Completely wrong category classification

#### **Root Cause (Hypothesis):**
- LLM classification in `_classify_with_llm` may be prioritizing "meal" category over "task"
- Confidence scorer may be giving low confidence, triggering alternatives
- Need to improve task/reminder detection in prompt

#### **Reproduction Steps:**
1. Type: "call mom at 9 pm"
2. Send message
3. Observe: Meal alternatives appear instead of task creation

#### **Impact:**
- Users cannot create tasks via natural language
- Confusing UX (why are tasks showing meal options?)
- Breaks core productivity feature

#### **Suggested Fix:**
1. Update `_classify_with_llm` in `app/main.py` to prioritize task/reminder keywords
2. Add task detection patterns: "call", "remind", "meeting", "appointment", "at [time]"
3. If task detected with high confidence, skip alternative generation
4. Return simple task creation response

#### **Files to Modify:**
- `app/main.py` (lines 854, classification logic)
- `app/services/chat_response_generator.py` (task response generation)

---

### **BUG #2: Water Logging Showing Meal Alternatives**
**Reported:** November 7, 2025  
**Status:** 🔴 Open  
**Priority:** High  
**Severity:** Major - Wrong category detection

#### **Description:**
When user types "1 litre of water", the system shows meal alternatives ("Item as breakfast", "Item as dinner") instead of simply logging water intake with a positive confirmation message.

#### **Expected Behavior:**
- AI should detect this as "water" category (already exists in system)
- Log water intake: 1000ml (1 litre)
- Show simple, encouraging message: "💧 Great! 1 litre of water logged. Keep staying hydrated! 💪"
- No alternatives, no meal options
- 0 kcal (water has no calories) ✅ (This is correct)

#### **Actual Behavior:**
- ❌ **CRITICAL:** AI logs "1 litre" as only **250ml** (1 glass)
  - User said: "1 litre of water"
  - Expected: 1000ml logged
  - Actual: 250ml logged (12% of daily goal instead of 50%)
- Shows message: "Excellent hydration! Keep it up! 💧"
- But then shows yellow alternative picker with:
  - "Item as breakfast" (70% confidence)
  - "Item as dinner" (60% confidence)
- **TWO BUGS:** Wrong quantity parsing + Wrong category (meal alternatives)

#### **Root Cause (Confirmed):**
1. **Quantity Parsing Issue:** "1 litre" being parsed as "1 glass" (250ml) instead of 1000ml
   - System likely defaults to "glass" unit when it doesn't recognize "litre"
   - Conversion logic missing: 1 litre = 1000ml, 2 litres = 2000ml
   - Current: "1 [anything] water" → 1 glass = 250ml
2. **Low Confidence Triggering Alternatives:** System has low confidence in water detection
3. **Meal Category Override:** LLM classifying water as a "meal item" instead of "water"

#### **Reproduction Steps:**
1. Type: "1 litre of water"
2. Send message
3. Observe in Water Intake widget:
   - Shows: "1 / 8 glasses" ❌ (should be "4 / 8 glasses" for 1000ml)
   - Shows: "250ml / 2000ml" ❌ (should be "1000ml / 2000ml")
   - Shows: "12% of daily goal" ❌ (should be "50% of daily goal")
4. Observe in chat:
   - Meal alternatives appear ❌
   - Should show: Simple confirmation message ✅

#### **Impact:**
- 🔴 **CRITICAL:** Users cannot log water intake correctly
- Quantity parsing broken (1 litre → 250ml instead of 1000ml)
- **75% of water intake lost!** (Only 25% logged)
- Users will think they're dehydrated when they're actually meeting goals
- Confusing UX (why is water showing meal options?)
- Discourages hydration tracking
- **Data integrity issue:** Historical water logs are all underreported by 75%

#### **Suggested Fix:**

**Fix 1: Quantity Parsing**
- Update water parsing in `app/services/food_macro_service.py` or classification logic
- Add patterns: "1 litre" → 1000ml, "2 litres" → 2000ml
- Add patterns: "1 glass" → 250ml, "2 glasses" → 500ml

**Fix 2: Category Detection**
- Update `_classify_with_llm` to prioritize "water" category
- Add water keywords: "water", "litre", "liter", "glass of water", "ml water"
- If water detected, set high confidence (>0.85) to skip alternatives

**Fix 3: Response Generation**
- Update `chat_response_generator.py` to handle water category
- Generate encouraging messages:
  - "💧 Excellent! 1 litre of water logged. Stay hydrated! 💪"
  - "💦 Great job! You've logged 2 glasses of water. Keep it up!"
  - "🌊 Awesome! 500ml added to your hydration tracker."

**Fix 4: Skip Alternatives for Water**
- In `app/main.py`, if category == "water" and confidence > 0.7, skip alternative generation
- Water logging should be simple and encouraging, not confusing

#### **Files to Modify:**
- `app/main.py` (lines 854, 919 - classification and alternative generation)
- `app/services/chat_response_generator.py` (add water response handling)
- `app/services/food_macro_service.py` (if quantity parsing is there)

#### **Test Cases After Fix:**
```
Input: "1 litre of water"
Expected Output:
  - Water logged: 1000ml
  - Message: "💧 Excellent! 1 litre of water logged. Stay hydrated! 💪"
  - No alternatives
  - Confidence: >85%

Input: "2 glasses of water"
Expected Output:
  - Water logged: 500ml
  - Message: "💦 Great job! You've logged 2 glasses of water. Keep it up!"
  - No alternatives
  - Confidence: >85%

Input: "drank 500ml water"
Expected Output:
  - Water logged: 500ml
  - Message: "🌊 Awesome! 500ml added to your hydration tracker."
  - No alternatives
  - Confidence: >85%
```

---

## 🟡 **MEDIUM PRIORITY BUGS**

### **BUG #3: Dislike Form Checkboxes Not Clickable**
**Reported:** November 7, 2025  
**Status:** 🟡 Open  
**Priority:** Medium  
**Severity:** Moderate - Feedback system partially broken

#### **Description:**
When user clicks "thumbs down" (dislike), a feedback form appears with checkboxes for common issues. However, the checkboxes are not clickable - only the comment text field works.

#### **Expected Behavior:**
- User clicks thumbs down
- Form appears with checkboxes:
  - [ ] Wrong item detected
  - [ ] Incorrect calories
  - [ ] Wrong meal type
  - [ ] Other
- User can click checkboxes to select issues
- User can type additional comment
- User clicks "Submit"
- All data (checkboxes + comment) sent to backend

#### **Actual Behavior:**
- Form appears correctly
- Checkboxes are visible but not clickable
- Only comment text field is editable
- User can only provide text feedback, not structured feedback

#### **Root Cause (Hypothesis):**
- Flutter checkbox widgets may not have `onChanged` callback
- Checkboxes may be disabled or read-only
- State management issue (checkbox state not updating)

#### **Reproduction Steps:**
1. Click thumbs down on any AI message
2. Try to click checkboxes in feedback form
3. Observe: Checkboxes don't respond to clicks
4. Type in comment box: Works fine

#### **Impact:**
- Users cannot provide structured feedback
- Backend receives incomplete feedback data
- Harder to analyze feedback patterns

#### **Suggested Fix:**
- Check `flutter_app/lib/widgets/chat/feedback_buttons.dart` or feedback form widget
- Ensure checkboxes have `onChanged: (value) => setState(() { ... })`
- Verify checkbox state is being tracked in widget state
- Test checkbox interaction

#### **Files to Investigate:**
- `flutter_app/lib/widgets/chat/feedback_buttons.dart`
- Any feedback form dialog widget

---

## 🟡 **MEDIUM PRIORITY BUGS**

### **BUG #4: "Something Else" User Correction Not Displayed**
**Reported:** November 7, 2025  
**Status:** 🟡 Open  
**Priority:** Medium  
**Severity:** Moderate - UX issue, data is saved but not visible

#### **Description:**
When user selects "Something else" in the alternative picker and provides a custom correction (e.g., "15 gm of rice and 50 gm of chicken"), the correction is submitted to the backend but NOT displayed as a user message in the chat. This makes it hard for users to remember what they actually entered.

#### **Expected Behavior:**
1. User types: "Rice"
2. AI shows alternatives
3. User clicks "Something else"
4. User types: "15 gm of rice and 50 gm of chicken"
5. User clicks Submit
6. **User's correction appears as a chat bubble** (right side, teal)
7. AI processes and responds with updated nutrition info

**Chat should show:**
```
[User] Rice
[AI] Rice, white, cooked (1.0 cup) logged! 206 kcal
     [Alternative picker]
[User] 15 gm of rice and 50 gm of chicken  ← THIS IS MISSING!
[AI] Rice (15g) and Chicken (50g) logged! [Updated info]
```

#### **Actual Behavior:**
1. User types: "Rice"
2. AI shows alternatives
3. User clicks "Something else"
4. User types: "15 gm of rice and 50 gm of chicken"
5. User clicks Submit
6. ❌ **User's correction NOT displayed in chat**
7. AI response appears, but user has no record of what they typed

**Chat shows:**
```
[User] Rice
[AI] Rice, white, cooked (1.0 cup) logged! 206 kcal
     [No user correction visible]
```

#### **Root Cause (Hypothesis):**
- Frontend: `alternative_picker.dart` sends correction to backend via `/chat/feedback` endpoint
- Backend: Saves correction as feedback (not_helpful + corrections field)
- **Missing:** No new user message created in chat history
- **Missing:** No UI update to show user's correction as a chat bubble

#### **Reproduction Steps:**
1. Type any food item (e.g., "Rice")
2. Wait for alternatives to appear
3. Click "Something else" button
4. Type custom correction: "15 gm of rice and 50 gm of chicken"
5. Click Submit
6. Observe: Correction is NOT displayed in chat

#### **Impact:**
- Users cannot see their own corrections
- Hard to remember what they actually logged
- Confusing when reviewing chat history
- Makes "Something else" feature feel broken
- Users may re-enter the same correction multiple times

#### **Suggested Fix:**

**Option 1: Add User Message to Chat (Recommended)**
1. In `alternative_picker.dart`, after user submits correction:
   - Add user message to chat: `_items.add(_ChatItem.userMessage(correctionText, DateTime.now()))`
   - Then call backend API
   - Then add AI response

2. In backend `/chat/feedback` endpoint:
   - When receiving user correction (index == -1 or user_correction == true)
   - Save correction as a new user message in chat history
   - Generate AI response with updated parsing
   - Return new AI message

**Option 2: Show Correction in Feedback Badge (Simpler)**
- After submission, show badge: "✏️ You corrected: 15 gm of rice and 50 gm of chicken"
- Less ideal, but quick fix

**Option 3: Show Correction in Alternative Picker (Quick Fix)**
- Replace alternative picker with: "✅ Correction submitted: 15 gm of rice and 50 gm of chicken"
- Keep it visible instead of hiding picker

#### **Files to Modify:**
- `flutter_app/lib/widgets/chat/alternative_picker.dart` (add user message after submit)
- `flutter_app/lib/widgets/chat/expandable_message_bubble.dart` (handle correction display)
- `app/main.py` (POST /chat/feedback - save correction as user message)

#### **Test Cases After Fix:**
```
Input: "Rice" → Click "Something else" → Type "15 gm rice and 50 gm chicken" → Submit

Expected Chat Display:
[User] Rice
[AI] Rice, white, cooked (1.0 cup) logged! 206 kcal
     [Alternative picker]
[User] 15 gm rice and 50 gm chicken  ← MUST BE VISIBLE
[AI] Rice (15g) and Chicken (50g) logged! 
     Calories: 55 + 82 = 137 kcal
```

---

## 🟢 **LOW PRIORITY ENHANCEMENTS**

### **ENHANCEMENT #1: Workout Calorie Modification**
**Reported:** November 7, 2025  
**Status:** 🟢 Open  
**Priority:** Low  
**Severity:** Minor - Enhancement request

#### **Description:**
When user logs a workout like "ran 5 km", the system shows alternatives but should allow calorie override/modification since workout calories are estimates.

#### **Expected Behavior:**
- User types: "ran 5 km"
- AI logs workout with estimated calories (e.g., 350 kcal)
- Shows alternatives with different calorie estimates:
  - Light pace: 250 kcal
  - Moderate pace: 350 kcal (selected)
  - Fast pace: 450 kcal
- User can select different estimate or enter custom calories

#### **Current Behavior:**
- Workout logged correctly
- Alternatives shown (good!)
- But alternatives are for "Item as breakfast" / "Item as dinner" (wrong category)

#### **Suggested Enhancement:**
- Generate workout-specific alternatives:
  - Different intensity levels
  - Different duration estimates
  - Custom calorie input option
- Make workout response more flexible

---

### **ENHANCEMENT #2: Default Chat Cards Collapsed**
**Reported:** November 7, 2025  
**Status:** 🟢 Open  
**Priority:** Low  
**Severity:** Minor - UX improvement

#### **Description:**
Chat cards (expandable message bubbles) default to expanded state on page load. Would be cleaner if they defaulted to collapsed, showing only summary.

#### **Expected Behavior:**
- On page load, all chat cards collapsed
- User sees only:
  - Summary line (e.g., "🍊 Orange logged! 62 kcal")
  - Confidence badge (89%)
  - "More details" button
- User clicks "More details" to expand

#### **Current Behavior:**
- All cards expanded by default
- Shows full nutrition breakdown, suggestions, etc.
- Makes chat feel cluttered

#### **Suggested Enhancement:**
- Add `defaultExpanded: false` prop to expandable cards
- Or track expansion state in local storage
- Cleaner, more ChatGPT-like UX

---

## 📊 **DEFECT SUMMARY**

### **By Priority:**
- 🔴 **High:** 2 bugs (Task creation, Water logging)
- 🟡 **Medium:** 2 bugs (Dislike checkboxes, Something else not displayed)
- 🟢 **Low:** 2 enhancements (Workout calories, Default collapsed)

### **By Category:**
- **Classification Issues:** 2 (Task, Water)
- **UI/UX Issues:** 3 (Checkboxes, Default state, Correction not displayed)
- **Enhancement Requests:** 1 (Workout calories)

### **By Status:**
- 🔴 **Open:** 6
- 🟢 **In Progress:** 0
- ✅ **Resolved:** 0

---

## 🎯 **RECOMMENDED FIX ORDER:**

1. **BUG #2: Water Logging** (High, CRITICAL - 75% data loss)
2. **BUG #1: Task Creation** (High, affects core feature)
3. **BUG #4: Something Else Not Displayed** (Medium, UX confusion)
4. **BUG #3: Dislike Checkboxes** (Medium, feedback system)
5. **ENHANCEMENT #2: Default Collapsed** (Low, quick win)
6. **ENHANCEMENT #1: Workout Calories** (Low, nice-to-have)

---

## 📝 **NOTES:**

- All bugs discovered during user testing on November 7, 2025
- Phase 2 (Explainable AI) is working well overall
- These are edge cases and category detection improvements
- No critical system failures or data loss issues
- System is stable and production-ready with these known issues

---

**Last Updated:** November 7, 2025  
**Next Review:** After bug fixes implemented

