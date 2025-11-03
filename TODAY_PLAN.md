# 📋 TODAY'S EXECUTION PLAN

**Date**: November 3, 2025  
**Goal**: Fix timezone issues systematically

---

## 🎯 3-STEP APPROACH

### ✅ STEP 1: LOCAL ENVIRONMENT (30 min) - **START HERE**
### 🔧 STEP 2: FIX TIMEZONE (2-3 hours)
### 🔐 STEP 3: ADMIN ACCESS (1 hour)

---

## 📍 STEP 1: GET LOCAL RUNNING (DO THIS FIRST!)

### Why Local First?
- ✅ Faster debugging (no deployment wait)
- ✅ See console logs in real-time
- ✅ Test fixes immediately
- ✅ No risk to production

### Quick Start:

```bash
# 1. Setup environment (already done!)
./start_local.sh

# 2. Start Backend (Terminal 1)
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. Update Frontend API URL (Terminal 2)
# Edit: flutter_app/lib/utils/constants.dart
# Line 6: Change to 'http://localhost:8000'

# 4. Start Frontend
cd flutter_app
flutter run -d chrome
```

### Verify Local Works:
1. Open http://localhost:XXXX (Flutter will show port)
2. Sign up with test user
3. Check console for timezone logs
4. Log "2 eggs"
5. Check if appears in Home/Timeline

**If local doesn't work**: We fix local first before touching timezone!

---

## 🔧 STEP 2: FIX TIMEZONE ISSUE

### Current Problem:
- Timezone saves as "UTC" (should be "Asia/Kolkata")
- Home/Timeline empty (timezone mismatch)
- Chat shows response but nothing displays

### Root Cause Analysis:

**Your Key Observation**: 
> "Default timezone should always be from user profile. While displaying dashboard it should cater for it."

**This is CORRECT!** The issue is:
1. **Backend**: Stores logs with UTC timestamps
2. **Frontend**: Filters by device local time
3. **Mismatch**: Frontend looking for "today IST" but logs are "today UTC"

### The Fix (2 parts):

#### Part A: Fix Timezone Detection (Frontend)
**File**: `flutter_app/lib/utils/timezone_helper.dart`

**Current Issue**: Returns "UTC" instead of "Asia/Kolkata"

**Debug Steps**:
1. Check browser console during signup
2. Look for logs:
   ```
   🔍 TimezoneHelper.getLocalTimezone() called
   🔍 UTC Offset detected: 5:30:00.000000
   🌍 Mapping offset +5:30 to timezone
   ✅ Web timezone: Asia/Kolkata
   ```
3. If missing → TimezoneHelper not called
4. If shows "UTC" → Offset detection failed

**Potential Fix**:
```dart
// Option 1: Force IST for now (temporary)
static Future<String> getLocalTimezone() async {
  final offset = DateTime.now().timeZoneOffset;
  if (offset.inHours == 5 && offset.inMinutes.remainder(60) == 30) {
    return 'Asia/Kolkata';  // Force IST
  }
  return _timezoneFromOffset(offset);
}

// Option 2: Use JavaScript directly (better)
import 'dart:js' as js;
static String getWebTimezone() {
  try {
    return js.context.callMethod('eval', [
      'Intl.DateTimeFormat().resolvedOptions().timeZone'
    ]).toString();
  } catch (e) {
    return 'Asia/Kolkata';  // Fallback
  }
}
```

#### Part B: Fix Frontend Filtering (Critical!)
**File**: `flutter_app/lib/providers/fitness_provider.dart`

**Current Issue**: Filters logs by device time, but logs stored in UTC

**The Fix**: Convert timestamps to user's timezone before filtering

```dart
// WRONG (current):
final today = DateTime.now();
final startOfDay = DateTime(today.year, today.month, today.day);
final logs = await getLogs(startDate: startOfDay, endDate: today);

// RIGHT (fixed):
Future<List<FitnessLog>> getTodayLogs() async {
  // Get user's timezone from profile
  final userTimezone = profile?.timezone ?? 'UTC';
  
  // Convert "now" to user's timezone
  final tz = getLocation(userTimezone);
  final nowInUserTz = TZDateTime.now(tz);
  
  // Get start/end of day in user's timezone
  final startOfDay = TZDateTime(tz, nowInUserTz.year, nowInUserTz.month, nowInUserTz.day);
  final endOfDay = startOfDay.add(Duration(days: 1));
  
  // Query logs
  final logs = await getLogs(
    startDate: startOfDay.toUtc(),  // Convert back to UTC for query
    endDate: endOfDay.toUtc(),
  );
  
  return logs;
}
```

---

## 🔐 STEP 3: ADMIN/DEVOPS ACCESS

### Goal: Direct database access for debugging

### What You Need:

1. **Firebase Admin SDK** (already have via backend)
2. **Direct Firestore Query Script**
3. **Automated Testing Script**

### Create Admin Tools:

```bash
# Create admin_tools directory
mkdir -p admin_tools

# 1. Direct DB Query Script
cat > admin_tools/query_user.py << 'EOF'
#!/usr/bin/env python3
import os
from google.cloud import firestore

os.environ['GOOGLE_CLOUD_PROJECT'] = 'productivityai-mvp'
db = firestore.Client()

def get_user_by_email(email):
    """Get user and profile by email"""
    users = db.collection('users').where('email', '==', email).limit(1).stream()
    for user in users:
        user_id = user.id
        user_data = user.to_dict()
        
        # Get profile
        profile = db.collection('user_profiles').document(user_id).get()
        profile_data = profile.to_dict() if profile.exists else None
        
        # Get recent logs
        logs = db.collection('users').document(user_id)\
                 .collection('fitness_logs')\
                 .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                 .limit(10).stream()
        
        return {
            'user': user_data,
            'profile': profile_data,
            'recent_logs': [log.to_dict() for log in logs]
        }
    return None

if __name__ == '__main__':
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else 'test@test.com'
    data = get_user_by_email(email)
    
    if data:
        print(f"\n✅ Found user: {email}")
        print(f"\nTimezone: {data['profile'].get('timezone')}")
        print(f"Recent logs: {len(data['recent_logs'])}")
        for log in data['recent_logs'][:3]:
            print(f"  - {log.get('item')}: {log.get('timestamp')}")
    else:
        print(f"❌ User not found: {email}")
EOF

chmod +x admin_tools/query_user.py

# 2. Automated Test Script
cat > admin_tools/test_timezone.py << 'EOF'
#!/usr/bin/env python3
"""Automated timezone testing"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"  # Change to production URL

def test_signup_timezone():
    """Test if timezone is saved correctly"""
    email = f"test_{datetime.now().timestamp()}@test.com"
    
    # 1. Sign up
    response = requests.post(f"{BASE_URL}/auth/signup", json={
        "email": email,
        "password": "Test123!"
    })
    
    # 2. Onboard
    token = response.json()['token']
    response = requests.post(
        f"{BASE_URL}/profile/onboard",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test User",
            "gender": "male",
            "age": 30,
            "height_cm": 175,
            "weight_kg": 75,
            "activity_level": "moderate",
            "fitness_goal": "lose_weight",
            "timezone": "Asia/Kolkata"  # Explicitly set
        }
    )
    
    # 3. Verify
    response = requests.get(
        f"{BASE_URL}/profile/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    profile = response.json()
    timezone = profile.get('timezone')
    
    print(f"\n✅ Test Result:")
    print(f"  Email: {email}")
    print(f"  Timezone: {timezone}")
    print(f"  Expected: Asia/Kolkata")
    print(f"  Status: {'✅ PASS' if timezone == 'Asia/Kolkata' else '❌ FAIL'}")
    
    return timezone == 'Asia/Kolkata'

if __name__ == '__main__':
    test_signup_timezone()
EOF

chmod +x admin_tools/test_timezone.py
```

---

## ✅ SUCCESS CRITERIA

After all fixes:
- [ ] Local environment running
- [ ] Can debug with console logs
- [ ] Timezone saves as "Asia/Kolkata"
- [ ] Home shows logged meals
- [ ] Timeline shows correct time
- [ ] AI classifies correctly
- [ ] Admin tools work for direct DB access

---

## 📊 EXECUTION ORDER

### Morning (Now):
1. ✅ Run `./start_local.sh` (DONE)
2. ⏳ Start backend locally
3. ⏳ Start frontend locally
4. ⏳ Verify local works

### After Local Works:
5. ⏳ Debug timezone detection (console logs)
6. ⏳ Fix timezone helper
7. ⏳ Fix frontend filtering
8. ⏳ Test locally
9. ⏳ Deploy to production

### After Timezone Fixed:
10. ⏳ Create admin tools
11. ⏳ Test automated scripts
12. ⏳ Document for future use

---

## 🚨 IMPORTANT NOTES

1. **Don't skip local testing**: Always test locally before deploying
2. **Check console logs**: They tell you exactly what's happening
3. **Fix one thing at a time**: Don't change multiple things together
4. **Verify after each fix**: Test immediately after each change

---

## 📞 NEXT STEPS FOR YOU:

**Right now**:
1. Open Terminal 1 → Start backend
2. Open Terminal 2 → Start frontend
3. Tell me if you see any errors
4. Once running, we'll debug timezone together

**Commands**:
```bash
# Terminal 1 (Backend)
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/app
source ../venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 (Frontend)
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app
# First, edit lib/utils/constants.dart line 6 to 'http://localhost:8000'
flutter run -d chrome
```

---

**Let me know when local is running and we'll debug timezone together!** 🚀

