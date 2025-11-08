# Testing Feedback Endpoints

## Test 1: Check if backend is receiving the request

In browser console (F12), type "rice" again and click thumbs up/down. Look for these logs:

### Frontend Logs (should see):
```
📊 [FEEDBACK CAPTURED] Positive feedback for message: <message_id>
📊 [FEEDBACK] Submitting: rating=helpful, corrections=[], comment=null
🔵 [API SERVICE] POST /chat/feedback
🔵 [API SERVICE] Data: {message_id: ..., rating: helpful, ...}
```

### What happens next:
- **If you see**: `✅ [API SERVICE] Response status: 200` → Backend received it!
- **If you see**: `❌ [API SERVICE] DioException` → There's an error, copy the full message

---

## Test 2: Check backend logs manually

In your backend terminal (where you ran `uvicorn`), you should see:
```
✅ [FEEDBACK] Saved: <feedback_id> for message <message_id>
```

---

## Test 3: Alternative Selection

When you click "Confirm" on an alternative:

### Frontend Logs (should see):
```
📊 [ALTERNATIVE] User selected index: <index>
🔵 [API SERVICE] POST /chat/select-alternative
```

---

## Common Issues:

1. **"Missing Authorization header"**
   - User is not authenticated
   - Token expired
   - Try logging out and back in

2. **"404 Not Found"**
   - Endpoint doesn't exist
   - Backend not running

3. **"500 Internal Server Error"**
   - Backend code error
   - Need to check backend terminal logs

4. **CORS error**
   - We fixed this, should not happen anymore

---

## Next Steps:

**Please send me the full console output** when you:
1. Type "rice"
2. Click thumbs up
3. Copy all console messages (especially ones starting with 🔵, ❌, ✅)




