# Tier 1, 2, 3 Features - Comprehensive Test Plan

## 🎯 Overview
This document provides a comprehensive test plan for all 14 quick wins implemented across Tier 1, 2, and 3.

## ✅ Pre-Testing Checklist
- [ ] Flutter dependencies installed (`flutter pub get`)
- [ ] Backend running locally (`cd app && uvicorn main:app --reload`)
- [ ] Firebase configured and connected
- [ ] Test user account ready
- [ ] Clear app data for fresh testing

---

## 📱 TIER 1: Super Quick Wins (5-10 min each)

### 1. Profile Edit ✏️
**Feature**: Allow users to edit their profile information

**Test Cases**:
1. **Navigate to Profile Edit**
   - [ ] Open app → Profile tab → "Edit Profile" button
   - [ ] Verify all current profile data is pre-filled
   
2. **Edit Basic Info**
   - [ ] Change name → Save → Verify updated on profile screen
   - [ ] Change age → Save → Verify updated
   - [ ] Change height/weight → Save → Verify updated
   
3. **Edit Goals**
   - [ ] Change fitness goal → Save → Verify updated
   - [ ] Change activity level → Save → Verify updated
   - [ ] Update target weight → Save → Verify updated
   
4. **Edit Preferences**
   - [ ] Change diet preference → Save → Verify updated
   - [ ] Add allergy → Save → Verify appears in list
   - [ ] Remove allergy → Save → Verify removed
   - [ ] Add disliked food → Save → Verify appears
   - [ ] Remove disliked food → Save → Verify removed
   
5. **Validation**
   - [ ] Try saving with empty name → Verify error message
   - [ ] Try invalid age (< 13 or > 120) → Verify error
   - [ ] Try invalid height/weight → Verify error
   
6. **UI/UX**
   - [ ] Verify loading indicator during save
   - [ ] Verify success message after save
   - [ ] Verify navigation back to profile screen
   - [ ] Verify all changes persist after app restart

**Expected Results**:
- All edits save successfully
- Validation prevents invalid data
- UI provides clear feedback
- Changes persist across sessions

---

### 2. Calorie Info Tooltip ℹ️
**Feature**: Info tooltip explaining calorie calculations

**Test Cases**:
1. **Tooltip Display**
   - [ ] Open Home screen
   - [ ] Tap info icon next to "Calories" header
   - [ ] Verify modal bottom sheet appears
   
2. **Content Verification**
   - [ ] Verify title: "About Your Calorie Goal"
   - [ ] Verify explanation includes:
     - Age, gender, height, weight factors
     - Activity level factor
     - Fitness goal factor
     - Calorie deficit/surplus explanation
   - [ ] Verify tip about ±100 calories
   
3. **Interaction**
   - [ ] Tap "Got it!" button → Verify modal closes
   - [ ] Tap outside modal → Verify modal closes
   - [ ] Tap info icon again → Verify modal reopens
   
4. **Macro Info Tooltip**
   - [ ] Tap info icon next to "Macros" header
   - [ ] Verify "About Macronutrients" modal appears
   - [ ] Verify protein, carbs, fat explanations
   - [ ] Verify calorie per gram information

**Expected Results**:
- Tooltips display helpful, accurate information
- Easy to open and close
- Content is clear and educational

---

### 3. Empty States 🎨
**Feature**: Beautiful empty states for no data scenarios

**Test Cases**:
1. **No Meals Logged**
   - [ ] Fresh account or clear meal data
   - [ ] Open Home screen
   - [ ] Verify "No Meals Logged Yet" empty state
   - [ ] Verify illustration/icon present
   - [ ] Verify "Log a Meal" CTA button
   - [ ] Tap CTA → Verify navigates to chat

2. **No Workouts Logged**
   - [ ] Clear workout data
   - [ ] Scroll to Activity card
   - [ ] Verify "No Workouts Logged" empty state
   - [ ] Verify "Log Workout" CTA button
   - [ ] Tap CTA → Verify navigates to chat

3. **No Search Results**
   - [ ] Open Meal Search screen
   - [ ] Search for "xyz123nonexistent"
   - [ ] Verify "No Results Found" empty state
   - [ ] Verify search query displayed in message
   - [ ] Verify suggestion to try different search

4. **No Favorites**
   - [ ] Clear favorites
   - [ ] Open Favorites view
   - [ ] Verify "No Favorites Yet" empty state
   - [ ] Verify explanation about saving favorites

**Expected Results**:
- Empty states are visually appealing
- Clear messaging guides user action
- CTAs navigate to correct screens

---

### 4. Enhanced Workout Display 💪
**Feature**: Better visual display for completed workouts

**Test Cases**:
1. **No Workouts State**
   - [ ] Verify empty state (tested above)

2. **1 Workout Completed**
   - [ ] Log a workout via chat
   - [ ] Return to Home screen
   - [ ] Verify green success card appears
   - [ ] Verify "1 Workout Completed" text
   - [ ] Verify "Great job staying active! 💪" message
   - [ ] Verify checkmark icon in green circle

3. **Multiple Workouts**
   - [ ] Log 2-3 more workouts
   - [ ] Verify count updates: "3 Workouts Completed"
   - [ ] Verify plural form is correct

4. **Visual Design**
   - [ ] Verify green color scheme
   - [ ] Verify rounded corners
   - [ ] Verify icon and text alignment
   - [ ] Verify responsive layout

**Expected Results**:
- Workout completion is celebrated visually
- Count updates accurately
- Design is motivational and clear

---

## 📱 TIER 2: Quick Wins (15-20 min each)

### 5. Water Goal Customization 💧
**Feature**: Ability to set and track custom water goals

**Test Cases**:
1. **Default Goal**
   - [ ] Fresh account
   - [ ] Verify default goal is 2000ml (8 glasses)
   
2. **View Water Widget**
   - [ ] Open Home screen
   - [ ] Scroll to Water Intake widget
   - [ ] Verify current intake / goal display
   - [ ] Verify progress bar
   - [ ] Verify glass icons (filled/unfilled)
   - [ ] Verify percentage display

3. **Log Water**
   - [ ] Open chat
   - [ ] Say "I drank 250ml water"
   - [ ] Verify water logged
   - [ ] Return to Home
   - [ ] Verify water widget updated
   - [ ] Verify glass count increased
   - [ ] Verify progress bar updated

4. **Goal Milestones**
   - [ ] Log water to reach 50% → Verify "Keep going!" message
   - [ ] Log water to reach 100% → Verify "Great hydration! 💧" message
   - [ ] Log water below 50% → Verify "Stay hydrated" message

5. **Timeline Integration**
   - [ ] Open Timeline
   - [ ] Verify water logs appear with correct details
   - [ ] Verify quantity and unit displayed

**Expected Results**:
- Water tracking is accurate
- Visual feedback is motivational
- Goals are clear and achievable

---

### 6. Macro Rings Visualization 📊
**Feature**: Circular ring visualization for macronutrients

**Test Cases**:
1. **Display Macro Rings**
   - [ ] Open Home screen
   - [ ] Verify Macro Rings widget appears next to Macros card
   - [ ] Verify 3 concentric rings (Protein, Carbs, Fat)
   
2. **Ring Colors**
   - [ ] Verify Protein ring is BLUE
   - [ ] Verify Carbs ring is AMBER/YELLOW
   - [ ] Verify Fat ring is PURPLE
   
3. **Progress Visualization**
   - [ ] Log a meal with protein
   - [ ] Verify protein ring fills proportionally
   - [ ] Log carbs → Verify carbs ring fills
   - [ ] Log fat → Verify fat ring fills
   
4. **Percentages**
   - [ ] Verify percentage displayed for each macro
   - [ ] Verify percentages match progress bars in Macros card
   
5. **Interaction**
   - [ ] Tap on rings → Verify no crash
   - [ ] Verify rings animate smoothly

**Expected Results**:
- Rings provide at-a-glance macro overview
- Colors are distinct and clear
- Progress is accurate

---

### 7. Meal Search with Favorites ⭐
**Feature**: Search for meals and mark favorites

**Test Cases**:
1. **Navigate to Search**
   - [ ] Open Home → Tap "Search" or navigate to `/meals/search`
   - [ ] Verify search screen loads

2. **Search Functionality**
   - [ ] Type "chicken" in search bar
   - [ ] Verify results filter in real-time (debounced)
   - [ ] Verify result count displayed
   - [ ] Verify meal cards show name, calories, macros

3. **Recent Searches**
   - [ ] Tap search bar (empty)
   - [ ] Verify recent searches dropdown appears
   - [ ] Tap a recent search → Verify search executes

4. **Suggestions**
   - [ ] Start typing "chi"
   - [ ] Verify suggestions dropdown appears
   - [ ] Verify matching text is highlighted
   - [ ] Tap suggestion → Verify search executes

5. **Favorite a Meal**
   - [ ] Tap heart icon on a meal card
   - [ ] Verify heart fills with red color
   - [ ] Verify animation plays
   - [ ] Tap again → Verify unfavorites

6. **Favorites Filter**
   - [ ] Favorite 2-3 meals
   - [ ] Tap favorites icon in app bar
   - [ ] Verify only favorited meals show
   - [ ] Verify "Favorites" chip appears
   - [ ] Tap chip X → Verify filter clears

7. **Empty States**
   - [ ] Search for nonexistent item → Verify empty state
   - [ ] Filter favorites with none → Verify empty state

**Expected Results**:
- Search is fast and responsive
- Favorites persist across sessions
- UI is intuitive and smooth

---

### 8. Date Toggle 📅
**Feature**: Quick toggle between today/yesterday with date picker

**Test Cases**:
1. **Display Date Toggle**
   - [ ] Open Home screen
   - [ ] Verify Date Toggle widget appears below header
   - [ ] Verify "Today" button is selected (highlighted)
   - [ ] Verify "Yesterday" button is unselected

2. **Toggle to Yesterday**
   - [ ] Tap "Yesterday" button
   - [ ] Verify button becomes selected
   - [ ] Verify "Today" button becomes unselected
   - [ ] Verify dashboard data updates for yesterday
   - [ ] Verify calorie, macro, meal data changes

3. **Toggle Back to Today**
   - [ ] Tap "Today" button
   - [ ] Verify button becomes selected
   - [ ] Verify dashboard data updates for today

4. **Previous Day Navigation**
   - [ ] Tap left chevron (previous day)
   - [ ] Verify date moves back one day
   - [ ] Verify data updates
   - [ ] Verify date label updates

5. **Next Day Navigation**
   - [ ] Tap right chevron (next day)
   - [ ] Verify date moves forward one day
   - [ ] Verify data updates
   - [ ] Verify right chevron disables when reaching today

6. **Date Picker**
   - [ ] Tap on date display (center)
   - [ ] Verify date picker modal appears
   - [ ] Select a date 3 days ago
   - [ ] Verify dashboard updates for that date
   - [ ] Verify date label updates

7. **Future Date Prevention**
   - [ ] Navigate to today
   - [ ] Verify next day button is disabled
   - [ ] Verify cannot select future dates in picker

**Expected Results**:
- Date navigation is smooth and intuitive
- Data updates correctly for each date
- Future dates are prevented

---

## 📱 TIER 3: Medium Wins (30-45 min each)

### 9. Chat Quick Actions ⚡
**Feature**: One-tap shortcuts for common logging actions

**Test Cases**:
1. **Display Quick Actions**
   - [ ] Open Chat screen
   - [ ] Verify Quick Actions bar appears above input
   - [ ] Verify 6 action buttons:
     - Log Meal (orange)
     - Water (cyan)
     - Workout (green)
     - Supplement (pink)
     - Task (purple)
     - Summary (blue)

2. **Log Meal Action**
   - [ ] Tap "Log Meal" button
   - [ ] Verify "Log my meal" appears in input
   - [ ] Verify cursor is ready for additional input
   - [ ] Send message → Verify meal logging flow starts

3. **Water Action**
   - [ ] Tap "Water" button
   - [ ] Verify "I drank 250ml water" appears in input
   - [ ] Send → Verify water logged successfully

4. **Workout Action**
   - [ ] Tap "Workout" button
   - [ ] Verify "Log my workout" appears in input
   - [ ] Complete workout logging flow

5. **Supplement Action**
   - [ ] Tap "Supplement" button
   - [ ] Verify "Log supplement" appears in input
   - [ ] Complete supplement logging flow

6. **Task Action**
   - [ ] Tap "Task" button
   - [ ] Verify "Add a task" appears in input
   - [ ] Complete task creation flow

7. **Summary Action**
   - [ ] Tap "Summary" button
   - [ ] Verify "Show my daily summary" appears in input
   - [ ] Send → Verify AI provides daily summary

8. **Context-Aware Suggestions**
   - [ ] Open chat at 8 AM → Verify "Log breakfast" suggestion
   - [ ] Open chat at 12 PM → Verify "Log lunch" suggestion
   - [ ] Open chat at 7 PM → Verify "Log dinner" suggestion
   - [ ] Tap suggestion → Verify executes action

**Expected Results**:
- Quick actions save time
- Suggestions are contextually relevant
- All actions work correctly

---

### 10. Goal Timeline 🎯
**Feature**: Visual timeline showing progress to goal weight

**Test Cases**:
1. **Display Goal Timeline**
   - [ ] Ensure user has target weight set
   - [ ] Open Profile screen
   - [ ] Verify Goal Timeline widget appears
   - [ ] Verify widget shows:
     - Expected timeline (weeks)
     - Target date
     - Current weight
     - Target weight
     - Weekly change rate

2. **Milestone Visualization**
   - [ ] Verify 4 milestones shown:
     - 25% Complete
     - 50% Complete
     - 75% Complete
     - 100% Complete (Goal!)
   - [ ] Verify each milestone shows:
     - Percentage
     - Target weight at that point
     - Week number

3. **Progress Bar**
   - [ ] Verify progress bar with milestone markers
   - [ ] Verify markers are positioned correctly

4. **Motivational Messages**
   - [ ] If goal is ≤ 4 weeks → Verify "You're so close! Stay focused! 💪"
   - [ ] If goal is 5-12 weeks → Verify "Great pace! Keep up the consistency! 🔥"
   - [ ] If goal is > 12 weeks → Verify "Steady progress wins the race! 🐢"

5. **Calculations**
   - [ ] Verify timeline calculation is accurate:
     - Weight to change / (daily deficit × 7 / 7700)
   - [ ] Verify milestone weights are correct
   - [ ] Verify target date is correct

6. **No Goal State**
   - [ ] User without target weight
   - [ ] Verify Goal Timeline does NOT appear

**Expected Results**:
- Timeline is accurate and motivational
- Milestones provide clear checkpoints
- Calculations are correct

---

### 11. Dark Mode 🌙
**Feature**: Dark theme for the entire app

**Test Cases**:
1. **Enable Dark Mode**
   - [ ] Open Settings
   - [ ] Toggle "Dark Mode" switch ON
   - [ ] Verify immediate theme change
   - [ ] Verify all screens use dark theme

2. **Theme Consistency**
   - [ ] Home screen → Verify dark background, light text
   - [ ] Profile screen → Verify dark theme
   - [ ] Chat screen → Verify dark theme
   - [ ] Timeline screen → Verify dark theme
   - [ ] Settings screen → Verify dark theme

3. **Component Styling**
   - [ ] Verify cards have dark background
   - [ ] Verify text is light colored
   - [ ] Verify buttons have appropriate contrast
   - [ ] Verify input fields have dark background
   - [ ] Verify icons are visible

4. **Color Scheme**
   - [ ] Verify primary colors are visible in dark mode
   - [ ] Verify accent colors pop appropriately
   - [ ] Verify no white flashes during navigation

5. **Disable Dark Mode**
   - [ ] Toggle "Dark Mode" switch OFF
   - [ ] Verify immediate theme change back to light
   - [ ] Verify all screens use light theme

6. **Persistence**
   - [ ] Enable dark mode
   - [ ] Close app completely
   - [ ] Reopen app
   - [ ] Verify dark mode is still enabled

7. **System Theme (Optional)**
   - [ ] If system theme support is implemented
   - [ ] Change device theme → Verify app follows

**Expected Results**:
- Dark mode is visually appealing
- All screens are consistent
- Theme persists across sessions
- No accessibility issues

---

### 12. Meal/Water/Workout Reminders ⏰
**Feature**: Configurable reminders for logging activities

**Test Cases**:
1. **Navigate to Reminders**
   - [ ] Open Settings → Tap "Reminders"
   - [ ] Verify Reminders screen loads

2. **Breakfast Reminder**
   - [ ] Enable "Breakfast" reminder
   - [ ] Set time to 8:00 AM
   - [ ] Tap "Save"
   - [ ] Verify success message
   - [ ] Wait until 8:00 AM next day → Verify notification appears

3. **Lunch Reminder**
   - [ ] Enable "Lunch" reminder
   - [ ] Set time to 12:30 PM
   - [ ] Save → Verify scheduled

4. **Dinner Reminder**
   - [ ] Enable "Dinner" reminder
   - [ ] Set time to 7:00 PM
   - [ ] Save → Verify scheduled

5. **Water Reminders**
   - [ ] Enable "Water Reminders"
   - [ ] Set interval to 2 hours
   - [ ] Save → Verify scheduled
   - [ ] Wait 2 hours → Verify notification appears
   - [ ] Change interval to 3 hours → Verify updates

6. **Workout Reminder**
   - [ ] Enable "Workout" reminder
   - [ ] Set time to 5:00 PM
   - [ ] Save → Verify scheduled

7. **Disable Reminders**
   - [ ] Disable "Breakfast" reminder
   - [ ] Save → Verify no longer scheduled
   - [ ] Verify no notification at 8:00 AM

8. **Notification Content**
   - [ ] Verify notification title is clear
   - [ ] Verify notification body is helpful
   - [ ] Tap notification → Verify opens app to chat

9. **Persistence**
   - [ ] Set reminders
   - [ ] Close app completely
   - [ ] Verify reminders still fire

**Expected Results**:
- Reminders fire at correct times
- Notifications are helpful and actionable
- Settings persist across sessions
- Easy to enable/disable

---

## 🔄 Regression Testing

### Core Features (Must Not Break)
1. **Authentication**
   - [ ] Sign up new user
   - [ ] Log in existing user
   - [ ] Log out
   - [ ] Password reset

2. **Onboarding**
   - [ ] Complete full onboarding flow
   - [ ] Verify profile created
   - [ ] Verify goals calculated

3. **Chat Logging**
   - [ ] Log meal via chat
   - [ ] Log workout via chat
   - [ ] Log task via chat
   - [ ] Log water via chat
   - [ ] Log supplement via chat

4. **Dashboard**
   - [ ] Verify calorie tracking
   - [ ] Verify macro tracking
   - [ ] Verify meal display
   - [ ] Verify workout display

5. **Timeline**
   - [ ] Verify all activities appear
   - [ ] Verify filters work
   - [ ] Verify collapsible sections work
   - [ ] Verify date navigation works

6. **Profile**
   - [ ] Verify profile displays correctly
   - [ ] Verify stats are accurate
   - [ ] Verify preferences display

---

## 🐛 Bug Testing

### Known Issues to Verify Fixed
1. **setState() Errors**
   - [ ] Navigate rapidly between screens → Verify no errors
   - [ ] Close chat while AI is typing → Verify no errors

2. **Timeline Filter Bug**
   - [ ] Click multiple filters rapidly → Verify timeline doesn't disappear
   - [ ] Verify at least one filter is always selected

3. **Mobile Authentication**
   - [ ] Test on mobile browser (Safari/Chrome)
   - [ ] Verify existing users don't redirect to onboarding

4. **Water Display**
   - [ ] Verify water details show correct quantity_ml
   - [ ] Verify water unit displays correctly

5. **Supplement Display**
   - [ ] Verify supplement name displays
   - [ ] Verify dosage displays
   - [ ] Verify supplement type displays

---

## 📊 Performance Testing

1. **Load Times**
   - [ ] Home screen loads < 2 seconds
   - [ ] Timeline loads < 3 seconds
   - [ ] Chat responds < 1 second (excluding AI)

2. **Smooth Animations**
   - [ ] Date toggle animates smoothly
   - [ ] Favorite button animates smoothly
   - [ ] Theme change is smooth (no flashing)

3. **Memory Usage**
   - [ ] No memory leaks during extended use
   - [ ] App doesn't crash after 30 min of use

---

## ✅ Sign-Off Checklist

### Before Production Deployment
- [ ] All Tier 1 features tested and passing
- [ ] All Tier 2 features tested and passing
- [ ] All Tier 3 features tested and passing
- [ ] All regression tests passing
- [ ] No critical bugs found
- [ ] Performance is acceptable
- [ ] Dark mode works on all screens
- [ ] Reminders fire correctly
- [ ] Data persists correctly
- [ ] Mobile testing complete (iOS Safari, Android Chrome)
- [ ] Desktop testing complete (Chrome, Firefox, Safari)

### Documentation
- [ ] Feature flags documented
- [ ] API changes documented (if any)
- [ ] User guide updated (if needed)
- [ ] Rollback plan ready

---

## 🚀 Test Execution Log

| Feature | Tested By | Date | Status | Notes |
|---------|-----------|------|--------|-------|
| Profile Edit | | | ⏳ Pending | |
| Calorie Info | | | ⏳ Pending | |
| Empty States | | | ⏳ Pending | |
| Workout Display | | | ⏳ Pending | |
| Water Goal | | | ⏳ Pending | |
| Macro Rings | | | ⏳ Pending | |
| Meal Search | | | ⏳ Pending | |
| Date Toggle | | | ⏳ Pending | |
| Chat Actions | | | ⏳ Pending | |
| Goal Timeline | | | ⏳ Pending | |
| Dark Mode | | | ⏳ Pending | |
| Reminders | | | ⏳ Pending | |

---

## 📝 Notes
- Test on multiple devices/browsers
- Test with different user profiles (different goals, activity levels)
- Test edge cases (very high/low values)
- Test offline behavior (if applicable)
- Document any issues found in GitHub Issues

---

**Last Updated**: November 4, 2025
**Test Plan Version**: 1.0
**Target Release**: Production


