# 🚨 CRITICAL BUGS - Nov 6, 2025

## Current Status: MULTIPLE CRITICAL ISSUES

---

## 🐛 **BUG #1: "Unknown - 2.0" Instead of "2 eggs"**

### **What User Sees:**
- Dashboard shows: "Unknown - 2.0"
- Timeline shows: "Unknown - 2.0"
- Expected: "2 eggs" or "Eggs 2"

### **Root Cause:**
Backend logs show:
```
Message 1: role=user, content=2 eggs  ← Received correctly
```

But dashboard shows:
```
📝 Processing log: type=meal, content=2.0, calories=140  ← WRONG!
```

**PROBLEM:** The AI classification or database save is converting "2 eggs" → "2.0"

### **Impact:** 🔴 HIGH - Users can't see what they ate

---

## 🐛 **BUG #2: Chat is SLOW (20-30 seconds)**

### **Evidence:**
```
POST /chat - Status: 200 - Time: 24.172s
POST /chat - Status: 200 - Time: 30.665s
POST /chat - Status: 200 - Time: 20.970s
POST /chat - Status: 200 - Time: 24.863s
POST /chat - Status: 200 - Time: 26.712s
```

### **Root Cause:** LLM Router is not working

From earlier logs:
```
⚠️ [AGENTIC AI] Router failed, falling back to direct OpenAI
```

The router fix from earlier didn't solve the performance issue.

### **Impact:** 🔴 CRITICAL - Users will abandon the app if every message takes 25+ seconds

---

## 🐛 **BUG #3: Wipe All Timeout (Still Failing)**

### **Evidence:**
```
❌ [API SERVICE] DELETE DioException: DioExceptionType.unknown
❌ [API SERVICE] DELETE Message: null
❌ [API SERVICE] DELETE Response: null
```

### **Root Cause:** 60-second timeout fix didn't apply

**WHY:** Flutter rebuild may have used cached code OR the change didn't take effect.

### **Impact:** 🟡 MEDIUM - Feature works but shows error (confusing UX)

---

## 🎯 **FIX PRIORITY:**

1. **🔴 BUG #2 (Chat Slow)** - Abandon app risk
2. **🔴 BUG #1 ("2.0" content)** - Core functionality broken
3. **🟡 BUG #3 (Wipe timeout)** - UX issue only

---

## 📋 **FIX PLAN:**

### **Fix #1: Chat Performance** ⚡
**Goal:** Reduce from 25s → <5s

**Actions:**
1. Check if LLM Router is actually initializing
2. Check if OpenAI API key is valid
3. Check if router config exists in Firestore
4. Consider reducing prompt size
5. Check if there are unnecessary retries

---

### **Fix #2: "2.0" Content Bug** 🐛
**Goal:** Show "2 eggs" correctly on dashboard

**Actions:**
1. Find where "2 eggs" becomes "2.0"
2. Check AI classification response
3. Check database save logic
4. Check dashboard display logic

---

### **Fix #3: Wipe Timeout** ⏱️
**Goal:** No error when wiping (even though it works)

**Actions:**
1. Verify 60s timeout is in compiled code
2. Alternative: Increase backend speed
3. Alternative: Show "Processing..." instead of error

---

## ⚠️ **USER FRUSTRATION LEVEL: HIGH**

**User Quote:**
> "Frustrating everytime you fix one and break another...now I am frustrated with your efficiency"

**Action Required:**
- Stop rushing
- Test each fix thoroughly
- Ensure zero regression
- One fix at a time

---

## 🎯 **NEXT STEP:**

**Focus on BUG #2 (Chat Performance) first** - This is causing the most pain.

Once chat is fast, tackle the "2.0" content bug, then the wipe timeout.

