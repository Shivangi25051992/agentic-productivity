# Priority 2 Issues

## 🐛 Authentication & Session Issues

### 1. Browser Refresh Logs Out User
**Issue:** When user refreshes browser, they get logged out  
**Expected:** Session should persist across browser refresh  
**Root Cause:** Auth state not persisted to localStorage/sessionStorage  

**Solution:**
- Store auth token in localStorage
- Restore auth state on app init
- Check token validity on refresh

**Priority:** HIGH (P2)  
**Impact:** Poor UX, users lose context

---

### 2. Browser Back Button Shows Logged-In Experience
**Issue:** After logout, browser back button shows previous logged-in screens  
**Expected:** After logout, back button should not show protected content  
**Root Cause:** Browser cache + route history not cleared on logout  

**Solution:**
- Clear route history on logout
- Use `pushReplacementNamed` instead of `pushNamed` for logout
- Add auth guards to prevent cached page access
- Clear browser cache on logout

**Priority:** MEDIUM (P2)  
**Security Risk:** LOW (token is invalid, but UI shows cached data)

---

## Implementation Plan

### Fix 1: Persist Auth State
```dart
// In AuthProvider
Future<void> _saveAuthState() async {
  final prefs = await SharedPreferences.getInstance();
  if (_idToken != null) {
    await prefs.setString('auth_token', _idToken!);
    await prefs.setString('user_id', _user?.uid ?? '');
  }
}

Future<void> _restoreAuthState() async {
  final prefs = await SharedPreferences.getInstance();
  final token = prefs.getString('auth_token');
  final userId = prefs.getString('user_id');
  
  if (token != null && userId != null) {
    // Validate token and restore session
    await _validateAndRestoreSession(token, userId);
  }
}
```

### Fix 2: Clear History on Logout
```dart
// In logout method
Future<void> logout(BuildContext context) async {
  await _auth.signOut();
  final prefs = await SharedPreferences.getInstance();
  await prefs.clear();
  
  // Clear navigation stack
  Navigator.of(context).pushNamedAndRemoveUntil(
    '/login',
    (route) => false, // Remove all routes
  );
}
```

---

## Testing Checklist

### Scenario 1: Browser Refresh
- [ ] Login to app
- [ ] Navigate to different pages
- [ ] Refresh browser (F5 or Cmd+R)
- [ ] ✅ Should stay logged in
- [ ] ✅ Should maintain current page/state

### Scenario 2: Browser Back After Logout
- [ ] Login to app
- [ ] Navigate to home page
- [ ] Logout
- [ ] Press browser back button
- [ ] ✅ Should NOT show home page
- [ ] ✅ Should redirect to login

### Scenario 3: Token Expiration
- [ ] Login to app
- [ ] Wait for token to expire (or manually expire it)
- [ ] Try to make API call
- [ ] ✅ Should detect expired token
- [ ] ✅ Should redirect to login
- [ ] ✅ Should show friendly message

---

## Related Issues

### Also Need to Fix:
1. **Chat history persistence** - Chat goes blank on navigation
2. **State management** - Some state lost on page change
3. **Loading states** - No loading indicators during auth check

---

## Estimated Time
- **Fix 1 (Persist auth):** 30 minutes
- **Fix 2 (Clear history):** 15 minutes
- **Testing:** 15 minutes
- **Total:** ~1 hour

---

**Status:** Documented for Priority 2 implementation  
**Next:** Complete AI Insights (current priority), then tackle these auth issues

