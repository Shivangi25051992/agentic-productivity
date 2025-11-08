# 🐛 Meal Planning Feature - Bug Fixes

**Date**: November 5, 2025  
**Status**: 🔧 **FIXED - Action Required**  
**Testing Session**: Meal Plan Generation  

---

## 🎯 Issue Reported

**User Error**: "Failed to generate meal plan : API error while generating Generate Meal plan"

---

## 🔍 Root Cause Analysis

After investigating the backend logs and code, I found **TWO critical issues**:

### **Issue #1: CORS Configuration Error** ❌ → ✅ **FIXED**

**Problem**:
- Backend CORS allowed origins: `localhost:3000`, `localhost:8080`, `localhost:9090`
- Flutter app runs on: `localhost:9000` ⚠️ **NOT IN THE LIST!**
- All API requests were being blocked with `400 Bad Request` on OPTIONS preflight

**Evidence from logs**:
```
INFO:     127.0.0.1:56774 - "OPTIONS /meal-planning/plans/generate HTTP/1.1" 400 Bad Request
INFO:     127.0.0.1:56790 - "OPTIONS /meal-planning/plans/generate HTTP/1.1" 400 Bad Request
INFO:     127.0.0.1:56897 - "OPTIONS /meal-planning/plans/generate HTTP/1.1" 400 Bad Request
```

**Fix Applied**:
```python
# app/main.py (lines 43-50)
allowed_origins = [
    "https://productivityai-mvp.web.app",
    "https://productivityai-mvp.firebaseapp.com",
    "http://localhost:3000",  # Allow local dev
    "http://localhost:8080",  # Allow local dev
    "http://localhost:9000",  # ✅ ADDED - Flutter web app
    "http://localhost:9090",  # Allow local dev (fitness app)
]
```

**Status**: ✅ **FIXED** - Backend automatically restarted with new configuration

---

### **Issue #2: Missing OpenAI API Key** ❌ → ⚠️ **ACTION REQUIRED**

**Problem**:
- The meal planning feature uses OpenAI GPT to generate personalized meal plans
- Current `.env` file has: `OPENAI_API_KEY=` (empty!)
- Without a valid API key, meal plan generation will fail

**Why this happens**:
- The AI needs to generate recipes based on:
  - Dietary preferences (vegetarian, keto, high protein, etc.)
  - Calorie and protein targets
  - Prep time preferences
  - Number of people
  - Ingredients to avoid

**Status**: ⚠️ **ACTION REQUIRED FROM USER**

---

## ✅ What I Fixed

1. **✅ CORS Configuration**
   - Added `localhost:9000` to allowed origins
   - Backend restarted automatically
   - API requests from Flutter app will now work

2. **✅ Created Setup Script**
   - Created `setup_openai_key.sh` to help with API key setup
   - Added instructions below

---

## 🔐 Action Required: Set Up OpenAI API Key

### **Option 1: Quick Setup (Recommended)**

Run the helper script:
```bash
./setup_openai_key.sh
```

This will check your current configuration and provide instructions.

---

### **Option 2: Manual Setup**

#### **Step 1: Get Your OpenAI API Key**

1. Go to: https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (it starts with `sk-proj-...`)

**⚠️ Important**: 
- The key will only be shown once!
- Store it securely
- Never commit it to git

#### **Step 2: Add to .env File**

**Method A - Using Command Line**:
```bash
# Navigate to project directory
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity

# Add your OpenAI key (replace with your actual key)
echo 'OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE' >> .env
```

**Method B - Edit .env Directly**:
```bash
# Open .env file in your editor
nano .env

# Or
code .env

# Add this line:
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE
```

#### **Step 3: Restart Backend**

The backend with `--reload` should pick up the change automatically, but if not:

```bash
# Find and kill the backend process
kill $(cat backend.pid)

# Start it again
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
echo $! > backend.pid
```

#### **Step 4: Verify Setup**

```bash
# Check that the key is set
grep OPENAI_API_KEY .env

# Should show:
# OPENAI_API_KEY=sk-proj-abc123...

# Key should be ~50+ characters long
```

---

## 🧪 Test Again

After setting up the OpenAI API key:

### **Test 1: Verify CORS Fix**

1. Open the app: http://localhost:9000
2. Open browser DevTools (F12) → Network tab
3. Navigate to Plan → Meal Planning
4. Try to generate a meal plan
5. **Expected**: No more CORS errors in Network tab

### **Test 2: Generate Meal Plan**

1. Click "Generate Meal Plan"
2. Select preferences:
   - ✅ High Protein
   - ✅ Low Carb
   - Calories: 2000
   - Protein: 150g
   - Prep time: Medium
   - 1 person
3. Click "Generate Meal Plan"
4. **Wait 30-60 seconds** (AI generation takes time)
5. **Expected**: 
   - Success message
   - Weekly calendar populates with meals
   - Each day shows breakfast, lunch, dinner

### **Test 3: View Generated Meals**

1. Click through different days of the week
2. **Expected**: Each day shows:
   - Daily nutrition summary
   - 3 meal cards with details
   - Calorie and macro information

### **Test 4: Generate Grocery List**

1. Click "View Grocery List"
2. Click "Generate Grocery List"
3. **Expected**:
   - Categorized list (Produce, Meat, Dairy, etc.)
   - Items with quantities
   - Check-off functionality works

---

## 📊 Technical Details

### What Happens When You Generate a Meal Plan

1. **Frontend** sends request to: `POST /meal-planning/plans/generate`
   - Includes: dietary preferences, calories, protein, etc.

2. **Backend** receives request:
   - Validates user authentication
   - Calls `MealPlanningService.generate_meal_plan_ai()`

3. **AI Service** (`meal_planning_service.py`):
   ```python
   async def generate_meal_plan_ai(user_id: str, request: GenerateMealPlanRequest):
       # Uses OpenAI GPT to generate:
       # - 7 days of meals (breakfast, lunch, dinner)
       # - Each meal with recipe details
       # - Nutrition information
       # - Cooking instructions
   ```

4. **OpenAI API** generates structured meal plan

5. **Backend** saves to Firestore:
   - `meal_plans/{plan_id}` - Plan metadata
   - `meal_plans/{plan_id}/meals/{day}` - Daily meals

6. **Frontend** receives meal plan and displays

### Error Flow Without API Key

```
Frontend → Backend → MealPlanningService → OpenAI API ❌
                                           ↓
                                    "Invalid API key"
                                           ↓
                            500 Internal Server Error
                                           ↓
                            "API error while generating"
```

---

## 🎯 Expected Behavior After Fixes

### ✅ CORS Fixed
- All API requests succeed
- No 400 errors in browser console
- Smooth communication between frontend and backend

### ✅ OpenAI Key Set
- Meal plan generation completes in 30-60 seconds
- Returns structured JSON with recipes
- Saves to database successfully

### ✅ User Experience
- Click "Generate" → Loading indicator
- Wait 30-60s → Success message
- Calendar populates → Can view meals
- Can generate grocery list → Can check items off

---

## 🔍 How to Debug Future Issues

### Check Backend Logs
```bash
tail -f backend.log
```

Look for:
- `🟢 [MEAL PLANNING API] generate_meal_plan called` - Request received
- `✅ [MEAL PLANNING API] Meal plan generated successfully` - Success
- `❌ [MEAL PLANNING API] Error generating meal plan` - Failure

### Check Frontend Console
```javascript
// Browser DevTools (F12) → Console
// Look for:
🟡 [MEAL PLANNING API SERVICE] Calling _api.post...
✅ [MEAL PLANNING API SERVICE] Generated meal plan: {id}
// Or
❌ [MEAL PLANNING API SERVICE] Error generating meal plan: {error}
```

### Check OpenAI API Status
```bash
# Test your API key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Should return list of available models
```

---

## 📝 Summary

### Issues Found
1. ❌ CORS blocking requests from `localhost:9000`
2. ❌ Missing OpenAI API key in `.env`

### Fixes Applied
1. ✅ Added `localhost:9000` to CORS allowed origins
2. ✅ Backend restarted with new configuration
3. ✅ Created setup script for OpenAI key

### Action Required
1. ⚠️ **YOU MUST**: Add your OpenAI API key to `.env`
2. ⚠️ **THEN**: Restart backend
3. ✅ **THEN**: Test meal plan generation again

---

## 🚀 Next Steps

1. **Set up OpenAI key** (see instructions above)
2. **Test meal plan generation** (should work now!)
3. **Test grocery list** (depends on meal plan)
4. **Continue with testing checklist** (`MEAL_PLANNING_MANUAL_TEST_GUIDE.md`)

---

## 💡 Pro Tips

### Free OpenAI Credits
- New OpenAI accounts get $5 free credits
- Enough to test the feature thoroughly
- Each meal plan generation costs ~$0.10-0.30

### Alternative: Mock Data
If you don't want to use OpenAI yet, I can create a mock version that returns sample data for testing the UI.

### Production Considerations
- Store API key in environment variables (not in code)
- Monitor API usage and costs
- Implement rate limiting
- Cache common meal plans
- Add fallback to pre-generated plans

---

## 📧 Need Help?

If you encounter any issues:
1. Check `backend.log` for errors
2. Check browser console for frontend errors
3. Verify API key is set correctly
4. Try the test again
5. Let me know the specific error message

---

**Status**: 🟢 **Ready to Test** (after OpenAI key is set)  
**Fixes Applied**: 1/2  
**User Action Required**: Set OpenAI API key  

---

Happy Testing! 🧪✨

