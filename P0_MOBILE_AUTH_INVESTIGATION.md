# 🚨 P0: Mobile Safari Authentication Issue - Investigation

**Date**: November 3, 2025  
**Priority**: P0 - CRITICAL  
**Status**: 🔍 Investigating with Debug Logs  
**Impact**: Existing users cannot access app on mobile Safari

---

## 📋 **Issue Summary**

### **Symptoms**:
1. ❌ Shows "Hi, there" instead of user name (e.g., "Shivangi")
2. ❌ "No Plan" displayed
3. ❌ No profile data loaded
4. ❌ Timeline shows "Error: API error"
5. ❌ Redirects to onboarding ("Get Started") for existing users
6. ✅ Works perfectly on laptop/desktop browser
7. ❌ **Only happens on mobile Safari** (iOS)
8. ❌ Happens on **multiple mobile devices** (confirmed by user)

### **User Impact**:
- **CRITICAL**: Existing users completely locked out of app on mobile
- Users forced through onboarding again
- If they skip onboarding, treated as non-existent user
- All existing data inaccessible on mobile

---

## 🔍 **Root Cause Analysis**

### **Hypothesis**:
The issue is in the `_HomeOrOnboarding` widget's `_checkProfile()` method:

```dart
try {
  await profile.fetchProfile(auth);
} catch (e) {
  // Profile fetch failed, but continue
  debugPrint('Profile fetch error: $e');
}

// If no profile or onboarding not completed, redirect to welcome
if (!profile.hasProfile) {
  Navigator.of(context).pushReplacementNamed('/onboarding/welcome');
}
```

**The Problem**:
- `profile.fetchProfile(auth)` is **silently failing** on mobile Safari
- Error is caught but execution continues
- `profile.hasProfile` remains `false`
- User gets redirected to onboarding

### **Possible Causes**:

#### **1. CORS Issue (Most Likely)**
- Mobile Safari has stricter CORS policies
- Backend might not be returning proper CORS headers for mobile
- Token might not be included in request due to CORS preflight failure

#### **2. Token Persistence Issue**
- Firebase Auth token not persisting properly on mobile Safari
- LocalStorage/IndexedDB restrictions in iOS Safari
- Token refresh failing on mobile

#### **3. Network Timeout**
- Mobile network slower than desktop
- Request timing out before profile loads
- No proper timeout handling

#### **4. iOS Safari Specific Bug**
- Known iOS Safari bugs with service workers
- PWA mode behaving differently than browser mode
- Cache issues in "Add to Home Screen" mode

---

## ✅ **Fixes Implemented**

### **1. Comprehensive Debug Logging** ✅

Added extensive logging to identify the exact failure point:

**In `main.dart` (_HomeOrOnboarding)**:
```dart
Future<void> _checkProfile() async {
  debugPrint('🔍 [MOBILE DEBUG] Starting profile check...');
  
  // Check authentication
  if (!auth.isAuthenticated || auth.currentUser == null) {
    debugPrint('❌ [MOBILE DEBUG] User not authenticated!');
    return;
  }
  debugPrint('✅ [MOBILE DEBUG] User authenticated: ${auth.currentUser?.email}');

  // Check token
  String? token;
  try {
    token = await auth.getIdToken();
    debugPrint('✅ [MOBILE DEBUG] Got ID token: ${token?.substring(0, 20)}...');
  } catch (e) {
    debugPrint('❌ [MOBILE DEBUG] Failed to get ID token: $e');
    return;
  }

  // Fetch profile
  try {
    await profile.fetchProfile(auth);
    debugPrint('✅ [MOBILE DEBUG] Profile fetch completed');
    debugPrint('🔍 [MOBILE DEBUG] Has profile: ${profile.hasProfile}');
  } catch (e, stackTrace) {
    debugPrint('❌ [MOBILE DEBUG] Profile fetch error: $e');
    debugPrint('❌ [MOBILE DEBUG] Stack trace: $stackTrace');
  }
}
```

**In `profile_provider.dart` (fetchProfile)**:
```dart
Future<void> fetchProfile(AuthProvider authProvider) async {
  debugPrint('🔍 [PROFILE] Starting fetchProfile...');
  
  final token = await authProvider.getIdToken();
  debugPrint('✅ [PROFILE] Got token: ${token.substring(0, 20)}...');
  
  final url = '${AppConstants.apiBaseUrl}/profile/me';
  debugPrint('🔍 [PROFILE] Fetching from: $url');
  
  final response = await http.get(...).timeout(
    const Duration(seconds: 15),
    onTimeout: () {
      debugPrint('❌ [PROFILE] Request timed out after 15 seconds');
      throw Exception('Request timed out');
    },
  );
  
  debugPrint('🔍 [PROFILE] Response status: ${response.statusCode}');
  debugPrint('🔍 [PROFILE] Response body: ${response.body}');
}
```

### **2. Timeline Filter Fix** ✅

Fixed separate bug where timeline disappears when all filters unchecked:

**Before**:
- User could uncheck all filters
- Timeline would show empty state
- Confusing UX

**After**:
- At least 1 filter must remain selected
- Attempting to uncheck last filter is blocked
- Timeline always shows at least one category

---

## 🧪 **Testing Plan**

### **Step 1: Deploy Debug Build** (Next)
```bash
cd flutter_app && flutter build web --release
cd .. && firebase deploy --only hosting
```

### **Step 2: Test on Mobile Safari**
1. Open app on mobile Safari: `https://productivityai-mvp.web.app`
2. Login with existing user credentials
3. Watch for debug logs in browser console
4. Check backend logs for API errors

### **Step 3: Analyze Logs**

**Expected Log Flow** (Success):
```
🔍 [MOBILE DEBUG] Starting profile check...
✅ [MOBILE DEBUG] User authenticated: user@example.com
✅ [MOBILE DEBUG] Got ID token: eyJhbGciOiJSUzI1NiIs...
🔍 [PROFILE] Starting fetchProfile...
✅ [PROFILE] Got token: eyJhbGciOiJSUzI1NiIs...
🔍 [PROFILE] Fetching from: https://aiproductivity-backend-rhwrraai2a-uc.a.run.app/profile/me
🔍 [PROFILE] Response status: 200
✅ [PROFILE] Profile loaded successfully
✅ [MOBILE DEBUG] Profile found - showing home screen
```

**Expected Log Flow** (Failure):
```
🔍 [MOBILE DEBUG] Starting profile check...
✅ [MOBILE DEBUG] User authenticated: user@example.com
❌ [MOBILE DEBUG] Failed to get ID token: [error]
OR
✅ [MOBILE DEBUG] Got ID token: eyJhbGciOiJSUzI1NiIs...
❌ [PROFILE] Request timed out after 15 seconds
OR
❌ [PROFILE] Response status: 401/403/500
```

### **Step 4: Check Backend Logs**
```bash
# Check Cloud Run logs for /profile/me endpoint
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=aiproductivity-backend \
  AND textPayload=~'/profile/me'" \
  --limit=50 --project=productivityai-mvp
```

---

## 🔧 **Potential Fixes** (Based on Log Analysis)

### **If Token Retrieval Fails**:
```dart
// Add token refresh logic
final token = await auth.currentUser?.getIdToken(true); // Force refresh
```

### **If CORS Issue**:
```python
# In backend main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://productivityai-mvp.web.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Add this
)
```

### **If Timeout Issue**:
```dart
// Increase timeout
final response = await http.get(...).timeout(
  const Duration(seconds: 30), // Increase from 15s
);
```

### **If 404 (Profile Not Found)**:
```python
# Check backend /profile/me endpoint
# Verify user_id extraction from token
# Check Firestore query
```

---

## 📊 **Current Status**

### **Completed** ✅:
1. ✅ Added comprehensive debug logging (frontend)
2. ✅ Added timeout handling (15s)
3. ✅ Fixed timeline filter bug
4. ✅ Built production bundle
5. ✅ Committed changes to git

### **Pending** ⏳:
1. ⏳ Deploy to production
2. ⏳ Test on mobile Safari
3. ⏳ Analyze debug logs
4. ⏳ Check backend logs
5. ⏳ Implement fix based on findings
6. ⏳ Verify fix works on multiple devices

---

## 🎯 **Next Steps**

### **Immediate** (User to do):
1. Deploy the debug build to production
2. Test on mobile Safari
3. Share debug logs from browser console
4. Check backend Cloud Run logs

### **After Log Analysis** (AI to do):
1. Identify exact failure point
2. Implement targeted fix
3. Test fix locally
4. Deploy to production
5. Verify with user on multiple devices

---

## 📝 **Notes**

- This is a **P0 CRITICAL** issue blocking mobile users
- Desktop works fine, only mobile Safari affected
- Multiple devices confirmed, not isolated incident
- User has tested multiple times, consistent behavior
- Timeline filter bug was separate issue (now fixed)

---

## 🔗 **Related Files**

- `flutter_app/lib/main.dart` - _HomeOrOnboarding widget
- `flutter_app/lib/providers/profile_provider.dart` - fetchProfile method
- `flutter_app/lib/providers/auth_provider.dart` - Authentication state
- `flutter_app/lib/services/auth_service.dart` - Firebase Auth wrapper
- `app/routers/profile.py` - Backend /profile/me endpoint

---

## 📞 **Communication**

**User Feedback**:
> "very strange issue- I logged into my account in mobile app safari browser. instead Shivangi, it's say Hi, there, No Plan, No profile, timeline : Error:API :error. i beleive this might be more of authenticating issue or something else. but i can confirm browser login worls we;; om ;aptop.. very interesting i logged in again and first page came as Get Started and it navigated to me to onboarding workflow. pretty strange if user is exisitng why workflow is triggering"

> "i have tried multiple times in multiple mobile. it is redirecting to onboarding flow and if i skip it treat as that user doesn't existi. it is very critical issue. however on laptop web browser it is working"

**Status**: Awaiting deployment and log analysis

---

*Last Updated*: November 3, 2025, 7:15 PM PST  
*Next Review*: After production deployment and mobile testing

