# System Monitoring Guide

## 🎯 Purpose
Real-time monitoring of backend and frontend to catch issues immediately during testing.

---

## 🚀 Quick Start

### **Option 1: Full System Monitor (Recommended)**
```bash
chmod +x monitor_system.sh
./monitor_system.sh
```

**What it shows:**
- ✅ Backend errors, warnings, and HTTP status codes
- ✅ Frontend errors and build issues
- ✅ Chat requests and responses
- ✅ Dashboard/fitness data updates
- ✅ All logs color-coded by type

**Output:** Console + saved to `/tmp/monitor_[timestamp].log`

---

### **Option 2: Focused Debug Monitor (For Chat → Dashboard)**
```bash
chmod +x monitor_debug.sh
./monitor_debug.sh
```

**What it shows:**
- 📨 Chat requests (when user sends message)
- 📦 Items array in response
- 🍽️  Nutrition logged
- 📊 Dashboard updates
- ❌ Errors only

**Best for:** Debugging the "2 eggs not showing in dashboard" issue

---

## 📊 Backend Monitoring

### **Enhanced Logging Added:**

#### 1. **Chat Endpoint (`POST /chat`)**
Every chat request now logs:
```
📊 [MONITOR] User: wQHjQvwt... | Items: 1 | Categories: ['meal']
   Item 1: meal | 2 eggs | Calories: 140
```

#### 2. **Performance Timing**
```
⏱️ [abc123] ✅ TOTAL TIME: 1234ms
⏱️ [abc123] BREAKDOWN: Save msg=12ms, LLM=456ms, DB=78ms, ...
```

#### 3. **Expandable Fields**
```
✨ [DEBUG] Expandable fields in response:
   - summary: 🥚 Eggs logged! 140 kcal...
   - suggestion: Great protein!...
   - expandable: True
```

#### 4. **Phase 2 Explainable AI**
```
🧠 [DEBUG] Phase 2 Explainable AI fields:
   - confidence_score: 0.83
   - confidence_level: high
   - explanation: Present
   - alternatives: 0 alternatives
```

---

## 🌐 Frontend Monitoring

### **Browser Console (Chrome DevTools)**

**How to open:**
1. Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
2. Click "Console" tab

**What to look for:**

#### ✅ **Successful Chat Flow:**
```javascript
🔍 [API RESPONSE] Keys in result: ["items", "summary", "suggestion", ...]
📊 [FEEDBACK CAPTURED] Positive feedback for message: 1234567890
✨ [EXPANDABLE] Rendering expandable bubble with confidence: 0.83
```

#### ❌ **Errors to Watch:**
```javascript
❌ Failed to fetch
❌ Network request failed
❌ TypeError: Cannot read property 'items' of undefined
❌ [API SERVICE] DELETE DioException: ...
```

#### 📦 **Items Array Verification:**
```javascript
console.log("Items received:", response.items);
// Should show: [{category: "meal", data: {calories: 140}, ...}]
```

---

## 🧪 Testing Scenarios with Monitoring

### **Scenario 1: Test Dashboard Update**

1. **Start monitor:**
   ```bash
   ./monitor_debug.sh
   ```

2. **In browser:**
   - Open Console (F12)
   - Log "2 eggs" in chat

3. **Expected logs:**

   **Backend (monitor_debug.sh):**
   ```
   [12:34:56] 📨 CHAT REQUEST
      POST /chat HTTP/1.1
   
   [12:34:57] 📦 ITEMS ARRAY
      📊 [MONITOR] User: wQHjQvwt... | Items: 1 | Categories: ['meal']
      Item 1: meal | 2 eggs | Calories: 140
   
   [12:34:57] 🍽️  NUTRITION LOGGED
      calories_consumed_today: 140
   ```

   **Frontend (Browser Console):**
   ```
   POST /chat 200 OK
   Items received: Array(1) [{category: "meal", ...}]
   FitnessProvider updated: 1 logs
   ```

4. **Verify:**
   - Dashboard shows 140/1657 calories
   - Today's Meals shows "2 eggs" card

---

### **Scenario 2: Test Feedback Capture**

1. **Start monitor:**
   ```bash
   ./monitor_system.sh
   ```

2. **In browser:**
   - Open Console (F12)
   - Log any food
   - Click thumbs down (👎)
   - Select "Wrong calories" + "Wrong quantity"
   - Type "Should be 200 calories" in text field
   - Click Submit

3. **Expected logs:**

   **Frontend (Browser Console):**
   ```
   📊 [FEEDBACK CAPTURED] Negative feedback for message: 1731024567890
      Corrections selected: ["calories", "quantity"]
      Additional feedback: "Should be 200 calories"
   ```

   **Backend (monitor_system.sh):**
   ```
   (No logs - feedback not saved yet, Phase 3 feature)
   ```

4. **Verify:**
   - Success snackbar appears: "Feedback received. AI will learn from this!"
   - Console shows captured data

---

### **Scenario 3: Test Checkbox State**

1. **In browser:**
   - Open Console (F12)
   - Log any food
   - Click thumbs down (👎)

2. **Try to click checkboxes**

3. **If read-only (not working):**
   - Check console for: `setState is not a function` or similar
   - Do hard refresh: `Cmd+Shift+R`

4. **If working:**
   - Checkboxes toggle on/off
   - Multiple selections possible
   - Console logs selections on submit

---

## 🔧 Troubleshooting

### **Problem: No backend logs appearing**

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check log file exists
ls -lh /tmp/backend_test.log

# Manually tail backend logs
tail -f /tmp/backend_test.log
```

---

### **Problem: Frontend errors in console**

**Common errors and fixes:**

1. **"Failed to fetch" / Network error**
   - Backend is down → Restart backend
   - CORS issue → Check `allowed_origins` in `app/main.py`

2. **"Cannot read property 'items' of undefined"**
   - Backend not returning items array
   - Check backend logs for errors
   - Test with: `curl -X POST http://localhost:8000/test/chat-debug?text=2%20eggs`

3. **"setState is not a function"**
   - Flutter hot reload didn't work
   - Do full restart: Kill Flutter, `flutter clean`, `flutter run`

---

## 📁 Log File Locations

| Service | Log File | Purpose |
|---------|----------|---------|
| Backend | `/tmp/backend_test.log` | All backend activity |
| Frontend | `/tmp/flutter_final.log` | Flutter build and runtime |
| Monitor | `/tmp/monitor_[timestamp].log` | Combined monitoring session |

**To view:**
```bash
# Backend
tail -f /tmp/backend_test.log

# Frontend
tail -f /tmp/flutter_final.log

# Last 100 lines of backend
tail -100 /tmp/backend_test.log
```

---

## 🎨 Log Color Codes

**In monitor scripts:**
- 🔴 **RED:** Errors, exceptions, HTTP 4xx/5xx
- 🟢 **GREEN:** Successful requests (200 OK), chat requests
- 🟡 **YELLOW:** Warnings, hot reloads
- 🔵 **BLUE:** Data updates (dashboard, fitness)
- 🟣 **MAGENTA:** Nutrition data (calories, protein)
- 🔷 **CYAN:** Status checks, builds

---

## 🚨 Critical Patterns to Watch

### **Dashboard Not Updating:**
Look for:
```
❌ Items: 0 | Categories: []
❌ TypeError: Cannot read property 'items' of undefined
❌ FitnessProvider: 0 logs (expected 1+)
```

### **Slow Performance:**
Look for:
```
⏱️ TOTAL TIME: 15000ms  (> 5 seconds is too slow!)
⏱️ LLM=12000ms          (LLM taking too long)
⏱️ DB=3000ms            (Database slow)
```

### **Authentication Issues:**
Look for:
```
❌ 401 Unauthorized
❌ Token is null!
❌ Not authenticated
```

---

## 📈 Best Practices

1. **Always monitor during testing**
   - Start `./monitor_system.sh` before testing
   - Keep browser console open (F12)

2. **Check logs after every action**
   - Send chat → Check monitor
   - Click button → Check console
   - See error → Check both logs

3. **Save logs for bug reports**
   - Monitor saves to `/tmp/monitor_[timestamp].log`
   - Screenshot browser console errors
   - Include in bug reports

4. **Test systematically**
   - One action at a time
   - Verify logs after each action
   - Don't proceed if errors appear

---

## ✅ Verification Checklist

Before reporting "it's working":

- [ ] Backend logs show items array with data
- [ ] Frontend console shows `POST /chat 200 OK`
- [ ] Dashboard updates with correct calories
- [ ] No errors in backend logs
- [ ] No errors in frontend console
- [ ] Performance < 5 seconds for chat
- [ ] Feedback captures selections (console logs)

---

## 🆘 When to Use Which Monitor

| Use Case | Use This | Why |
|----------|----------|-----|
| General testing | `monitor_system.sh` | See everything |
| Dashboard bug | `monitor_debug.sh` | Focused on items/calories |
| Performance issue | Backend logs + timing | See timing breakdown |
| Frontend error | Browser console | See JavaScript errors |
| Feedback testing | Browser console | Capture logs |

---

**Created:** 2025-11-06
**Status:** Ready for use
**Next:** Start monitoring and test!




