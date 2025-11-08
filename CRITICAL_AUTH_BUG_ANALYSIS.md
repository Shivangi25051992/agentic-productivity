# 🚨 CRITICAL: Auth Token Mismatch - Production Security Issue

## ❌ Problem Statement

**User logged in as**: `test14@test.com`  
**Frontend shows user**: `test@test15.com` (`ACjSKgsfS0NkgSQYCvAEtnRvMO43`)  
**Backend decodes token as**: `v8Opsbu6omZMRQyjmMqs6vLe18r1`

**Result**: User sees wrong data (or no data) because backend queries for wrong user ID.

---

## 🔍 Root Cause Analysis

### 1. **Firebase Auth State Persistence**

Firebase Auth persists login state in browser's `IndexedDB` and `localStorage`:
- `firebaseLocalStorageDb` (IndexedDB)
- `firebase:authUser:*` (localStorage)

**Issue**: When you log out and log in as a different user, Firebase may not fully clear the old session, especially if:
- Multiple tabs are open
- Browser cache is not cleared
- Firebase SDK has a bug/race condition

### 2. **Token Caching**

The frontend code (`api_service.dart` line 52) calls:
```dart
final token = await _authProvider.getIdToken();
```

This should fetch a fresh token from Firebase, but if Firebase's internal state is corrupted, it returns a stale token for the wrong user.

### 3. **No Backend Validation**

The backend (`auth.py` line 80) extracts `uid` from token:
```python
uid = claims.get("uid")
```

But it **trusts** the token completely. If Firebase returns a token for user A when user B is logged in, the backend has no way to detect this.

---

## 🎯 Immediate Fixes (Development)

### Fix 1: Force Clear All Auth State

Add this to your Flutter logout function:

```dart
Future<void> signOut() async {
  await _auth.signOut();
  
  // CRITICAL: Clear all Firebase persistence
  if (kIsWeb) {
    // Clear IndexedDB
    await html.window.indexedDB?.deleteDatabase('firebaseLocalStorageDb');
    
    // Clear localStorage
    html.window.localStorage.clear();
    html.window.sessionStorage.clear();
  }
}
```

### Fix 2: Add User ID Verification

In backend `auth.py`, add logging to detect mismatches:

```python
def get_current_user(authorization: Optional[str] = Header(default=None)) -> User:
    token = _extract_bearer_token(authorization)
    claims = verify_firebase_id_token(token)
    uid = claims.get("uid")
    email = claims.get("email")
    
    # CRITICAL: Log for debugging
    print(f"🔐 [AUTH] Token decoded: uid={uid}, email={email}")
    
    if not uid or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing required claims")
    
    user = get_user(uid)
    
    # CRITICAL: Verify email matches
    if user and user.email != email:
        print(f"🚨 [AUTH] EMAIL MISMATCH! Token email={email}, DB email={user.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token/user mismatch")
    
    return user
```

### Fix 3: Frontend Token Validation

Add this check in Flutter before making API calls:

```dart
Future<String?> getIdToken() async {
  final u = _auth.currentUser;
  if (u == null) return null;
  
  final token = await u.getIdToken();
  
  // CRITICAL: Verify token matches current user
  final decodedToken = await u.getIdTokenResult();
  if (decodedToken.claims?['email'] != u.email) {
    print('🚨 [AUTH] Token mismatch! Forcing re-auth...');
    await signOut();
    return null;
  }
  
  return token;
}
```

---

## 🏭 Production Fixes (Required Before Launch)

### 1. **Implement Session Validation**

Add a session table in Firestore:
```
sessions/{session_id}
  - user_id: string
  - created_at: timestamp
  - last_active: timestamp
  - device_info: string
```

On every API call:
1. Extract session ID from token
2. Verify it matches user_id in database
3. Reject if mismatch

### 2. **Add Request Fingerprinting**

Include device/browser fingerprint in API requests:
```dart
headers: {
  'X-Device-ID': deviceId,
  'X-User-Agent': userAgent,
}
```

Backend validates:
- Same device ID for same session
- Reject if sudden change (possible token theft)

### 3. **Implement Token Rotation**

Force token refresh every 5 minutes:
```dart
Timer.periodic(Duration(minutes: 5), (_) async {
  await _auth.currentUser?.getIdToken(true); // Force refresh
});
```

### 4. **Add Audit Logging**

Log every API call with:
- Token UID
- Request IP
- Timestamp
- Endpoint

Monitor for:
- Same token used from different IPs
- Rapid user ID changes
- Suspicious patterns

---

## 🧪 How to Test

### Test 1: Multi-User Login
1. Log in as user A
2. Open new incognito tab
3. Log in as user B
4. Go back to first tab
5. Make API call
6. ✅ Should see user A's data (not B's)

### Test 2: Logout/Login
1. Log in as user A
2. Log out
3. Log in as user B
4. ✅ Should see user B's data (not A's)

### Test 3: Token Expiry
1. Log in
2. Wait 60 minutes (token expires)
3. Make API call
4. ✅ Should auto-refresh or show login

### Test 4: Concurrent Sessions
1. Log in on desktop as user A
2. Log in on mobile as user A
3. Make API calls from both
4. ✅ Both should work correctly

---

## 📊 Monitoring (Production)

### Metrics to Track:
1. **Auth errors per minute**
   - Spike = potential attack or bug
2. **User ID changes per session**
   - Should be 0 (if >0, investigate)
3. **Token refresh failures**
   - High rate = Firebase issue
4. **Concurrent sessions per user**
   - Unusual patterns = account sharing/theft

### Alerts:
- ⚠️ Warning: >10 auth errors/min
- 🚨 Critical: User ID mismatch detected
- 🚨 Critical: Token used from >2 IPs in 5 min

---

## ✅ Immediate Action Items

### For Development (Now):
- [ ] Add detailed auth logging to backend
- [ ] Clear all browser data and test
- [ ] Add email verification in `get_current_user`
- [ ] Test with multiple users

### For Production (Before Launch):
- [ ] Implement session validation
- [ ] Add request fingerprinting
- [ ] Set up audit logging
- [ ] Configure monitoring alerts
- [ ] Add token rotation
- [ ] Security audit by external team

---

## 🔒 Security Best Practices

1. **Never trust tokens blindly**
   - Always validate against database
   - Check for tampering
   - Verify expiry

2. **Implement defense in depth**
   - Multiple layers of validation
   - Audit logging
   - Anomaly detection

3. **Regular security audits**
   - Penetration testing
   - Code review
   - Dependency updates

4. **User education**
   - Don't share accounts
   - Log out on shared devices
   - Report suspicious activity

---

## 📝 Incident Response Plan

If user reports seeing wrong data:

1. **Immediate**:
   - Force logout all sessions for that user
   - Invalidate all tokens
   - Check audit logs for unauthorized access

2. **Investigation**:
   - Review last 24h of API calls
   - Check for IP anomalies
   - Verify no data leakage

3. **Communication**:
   - Notify affected users
   - Explain what happened
   - Steps taken to prevent recurrence

4. **Prevention**:
   - Implement additional fixes
   - Update security policies
   - Train team on secure coding

---

**Status**: 🚨 CRITICAL - Must fix before production
**Priority**: P0 - Blocks launch
**Owner**: Engineering team
**ETA**: Immediate (development fixes) + 1 week (production hardening)


