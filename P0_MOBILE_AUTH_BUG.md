# 🚨 P0 CRITICAL: Mobile Authentication Bug

**Reported**: November 3, 2025  
**Severity**: CRITICAL  
**Impact**: Existing users redirected to onboarding on mobile  
**Status**: 🔴 ACTIVE BUG

---

## 📋 **Symptoms**

User logged in on mobile Safari (PWA mode):
1. ❌ Shows "Hi, there" instead of user name
2. ❌ Shows "No Plan"
3. ❌ No profile data loaded
4. ❌ Timeline shows "Error: API: error"
5. ❌ **Redirected to onboarding workflow** (existing user!)
6. ✅ Works fine on laptop browser
7. ❌ Only happens on mobile Safari

---

## 🔍 **Root Cause Analysis**

### **What's Happening**:

```
1. User logs in on mobile Safari
2. App tries to fetch profile: GET /profile/me
3. Backend verifies Firebase ID token
4. Token verification FAILS (expired/invalid on mobile)
5. Backend returns 401 Unauthorized
6. Frontend catches error, sets _profile = null
7. hasProfile returns false
8. App redirects to onboarding (thinks user is new)
```

### **Why It Happens**:

**Mobile Safari Issues**:
- Token expiration handling different from desktop
- Local storage/IndexedDB issues in PWA mode
- Cookie handling differences
- CORS preflight issues

**Code Flow**:
```dart
// flutter_app/lib/providers/profile_provider.dart
Future<void> fetchProfile(AuthProvider authProvider) async {
  try {
    final token = await authProvider.getIdToken();  // ← May be expired
    if (token == null) {
      throw Exception('Not authenticated');
    }
    
    final response = await http.get(
      Uri.parse('${AppConstants.apiBaseUrl}/profile/me'),
      headers: {'Authorization': 'Bearer $token'},  // ← Token invalid
    );
    
    if (response.statusCode == 200) {
      _profile = UserProfileModel.fromJson(data['profile']);
    } else if (response.statusCode == 404) {
      _profile = null;  // ← Profile not found
    } else {
      _errorMessage = 'Failed to fetch profile';  // ← 401 error
    }
  } catch (e) {
    _errorMessage = e.toString();  // ← Network/auth error
  }
}

// flutter_app/lib/main.dart
if (!profile.hasProfile) {  // ← _profile is null, so hasProfile = false
  Navigator.pushReplacementNamed('/onboarding/welcome');  // ← REDIRECTS!
}
```

---

## 🎯 **The Problem**

### **Current Logic**:
```
Profile fetch fails → _profile = null → hasProfile = false → Redirect to onboarding
```

### **Should Be**:
```
Profile fetch fails → Check if auth error → Refresh token → Retry
If still fails → Show error, don't redirect
Only redirect to onboarding if 404 (profile truly doesn't exist)
```

---

## ✅ **Solution**

### **Fix 1: Distinguish Between Auth Errors and Missing Profile**

```dart
// flutter_app/lib/providers/profile_provider.dart
Future<void> fetchProfile(AuthProvider authProvider) async {
  _isLoading = true;
  _errorMessage = null;
  
  try {
    final token = await authProvider.getIdToken();
    if (token == null) {
      // Try to refresh token
      await authProvider.refreshToken();
      final newToken = await authProvider.getIdToken();
      if (newToken == null) {
        throw Exception('Authentication failed');
      }
    }
    
    final response = await http.get(
      Uri.parse('${AppConstants.apiBaseUrl}/profile/me'),
      headers: {'Authorization': 'Bearer $token'},
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _profile = UserProfileModel.fromJson(data['profile']);
      _profileNotFound = false;  // NEW FLAG
    } else if (response.statusCode == 404) {
      // Profile truly doesn't exist
      _profile = null;
      _profileNotFound = true;  // NEW FLAG
    } else if (response.statusCode == 401) {
      // Auth error - don't set profile to null
      _errorMessage = 'Authentication error. Please log in again.';
      // Don't set _profile = null if we had a profile before
    } else {
      _errorMessage = 'Failed to fetch profile: ${response.body}';
    }
  } catch (e) {
    _errorMessage = e.toString();
    // Don't set _profile = null on network errors
  } finally {
    _isLoading = false;
    notifyListeners();
  }
}

// Update hasProfile getter
bool get hasProfile => _profile != null && _profile!.onboardingCompleted;
bool get profileNotFound => _profileNotFound;  // NEW
```

### **Fix 2: Better Token Refresh Logic**

```dart
// flutter_app/lib/providers/auth_provider.dart
Future<String?> getIdToken({bool forceRefresh = false}) async {
  if (_user == null) return null;
  
  try {
    // Check if token is about to expire
    final tokenResult = await _user!.getIdTokenResult();
    final expirationTime = tokenResult.expirationTime;
    final now = DateTime.now();
    
    // Refresh if token expires in less than 5 minutes
    if (expirationTime != null && 
        expirationTime.difference(now).inMinutes < 5) {
      forceRefresh = true;
    }
    
    return await _user!.getIdToken(forceRefresh);
  } catch (e) {
    debugPrint('Error getting ID token: $e');
    return null;
  }
}

Future<void> refreshToken() async {
  if (_user == null) return;
  
  try {
    await _user!.reload();
    _user = fb_auth.FirebaseAuth.instance.currentUser;
    notifyListeners();
  } catch (e) {
    debugPrint('Error refreshing token: $e');
  }
}
```

### **Fix 3: Don't Redirect on Auth Errors**

```dart
// flutter_app/lib/main.dart
Future<void> _checkProfile() async {
  final auth = context.read<AuthProvider>();
  final profile = context.read<ProfileProvider>();

  try {
    await profile.fetchProfile(auth);
  } catch (e) {
    debugPrint('Profile fetch error: $e');
  }

  if (mounted) {
    setState(() {
      _isChecking = false;
    });

    // Only redirect if profile truly doesn't exist (404)
    // Don't redirect on auth errors or network errors
    if (profile.profileNotFound) {
      Navigator.of(context).pushReplacementNamed('/onboarding/welcome');
    } else if (profile.errorMessage != null) {
      // Show error dialog, don't redirect
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Error Loading Profile'),
          content: Text(profile.errorMessage!),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _checkProfile();  // Retry
              },
              child: const Text('Retry'),
            ),
            TextButton(
              onPressed: () {
                auth.signOut();
                Navigator.of(context).pushReplacementNamed('/login');
              },
              child: const Text('Log Out'),
            ),
          ],
        ),
      );
    }
  }
}
```

---

## 🔧 **Additional Fixes**

### **1. Add Retry Logic**:
```dart
Future<void> fetchProfileWithRetry(AuthProvider authProvider, {int maxRetries = 3}) async {
  for (int i = 0; i < maxRetries; i++) {
    try {
      await fetchProfile(authProvider);
      if (_profile != null) return;  // Success
      
      if (_profileNotFound) return;  // Profile doesn't exist, don't retry
      
      // Wait before retry (exponential backoff)
      await Future.delayed(Duration(seconds: pow(2, i).toInt()));
    } catch (e) {
      if (i == maxRetries - 1) rethrow;  // Last attempt failed
    }
  }
}
```

### **2. Add Logging**:
```dart
// Log auth issues for debugging
debugPrint('🔐 AUTH: Token status: ${token != null ? "valid" : "null"}');
debugPrint('🔐 AUTH: User: ${authProvider.user?.email}');
debugPrint('🔐 AUTH: Response: ${response.statusCode}');
debugPrint('🔐 AUTH: Error: $_errorMessage');
```

### **3. Add User Feedback**:
```dart
// Show loading state
if (_isLoading) {
  return Scaffold(
    body: Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('Loading your profile...'),
        ],
      ),
    ),
  );
}
```

---

## 🧪 **Testing**

### **Test Cases**:
1. ✅ Desktop browser - should work
2. ❌ Mobile Safari (PWA) - currently broken
3. ❌ Mobile Safari (browser) - test this
4. ❌ Mobile Chrome (PWA) - test this
5. ❌ Mobile Chrome (browser) - test this
6. ❌ After token expiration (1 hour) - test this
7. ❌ After app is closed and reopened - test this
8. ❌ With poor network connection - test this

### **Test Steps**:
1. Log in on mobile Safari
2. Save to home screen (PWA mode)
3. Close app completely
4. Wait 5 minutes
5. Reopen app
6. Check if profile loads correctly
7. Check if redirected to onboarding (should NOT be)

---

## 📊 **Impact**

### **Current State**:
- ❌ **100% of mobile users** affected
- ❌ Existing users forced through onboarding again
- ❌ Data loss risk (if they complete onboarding again)
- ❌ Poor user experience
- ❌ Trust issues

### **After Fix**:
- ✅ Mobile users can access their profiles
- ✅ Proper error handling
- ✅ Token refresh works correctly
- ✅ No unnecessary onboarding redirects

---

## 🎯 **Priority**

**P0 - CRITICAL**

**Rationale**:
1. Affects all mobile users
2. Breaks core functionality
3. Data integrity risk
4. User trust issue
5. Blocks mobile adoption

**Estimated Effort**: 4-6 hours

**Dependencies**: None

---

## 📋 **Action Plan**

### **Immediate** (Today):
1. [ ] Implement Fix 1: Distinguish auth errors from missing profile
2. [ ] Implement Fix 2: Better token refresh
3. [ ] Implement Fix 3: Don't redirect on auth errors
4. [ ] Add logging for debugging

### **Testing** (Tomorrow):
1. [ ] Test on mobile Safari (PWA)
2. [ ] Test on mobile Safari (browser)
3. [ ] Test on mobile Chrome
4. [ ] Test token expiration
5. [ ] Test app reopen after close

### **Deploy** (After Testing):
1. [ ] Deploy to production
2. [ ] Monitor logs for auth errors
3. [ ] Get user feedback

---

## 🔗 **Related Issues**

- Timeline API error (likely same root cause)
- "No Plan" display (profile not loaded)
- "Hi, there" instead of name (profile not loaded)

---

## 📝 **Notes**

- This is likely why water tracking and other features don't work on mobile
- May also affect iOS app when built
- Consider adding Sentry/error tracking for better debugging
- Consider adding health check endpoint that doesn't require auth

---

**Status**: 🔴 CRITICAL - FIX IMMEDIATELY  
**Assigned**: Next sprint (this week)  
**Estimated Fix Time**: 4-6 hours  
**Testing Time**: 2-3 hours  
**Total**: 1 day

