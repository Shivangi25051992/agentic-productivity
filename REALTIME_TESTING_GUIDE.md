# 🔴 Real-Time Firestore Snapshots - Testing Guide

## Overview

Real-time Firestore snapshots have been implemented to replace polling with push-based updates. This provides:
- **Instant updates** across devices (no refresh needed)
- **Better UX** (live synchronization)
- **Reduced latency** (push vs poll)
- **Lower battery usage** (no constant polling)

---

## 🚩 **Feature Flag Control**

Real-time updates are **DISABLED by default** and controlled by a feature flag.

### **Enable Real-Time Updates**

Edit `flutter_app/lib/utils/feature_flags.dart`:

```dart
/// Enable real-time Firestore snapshots (frontend-side)
/// Status: IMPLEMENTED (Task 9)
/// Default: false (needs testing)
static const bool realtimeUpdatesEnabled = true;  // ← Change to true
```

Then rebuild the app:

```bash
cd flutter_app
flutter run
```

---

## 📋 **What's Implemented**

### **1. RealtimeService** (`flutter_app/lib/services/realtime_service.dart`)

A singleton service that manages Firestore onSnapshot listeners:

- **Timeline Listener**: Listens to `users/{userId}/fitness_logs` collection
- **Dashboard Listener**: Listens to today's fitness logs for real-time stats
- **Connection State Management**: Tracks connection status (disconnected, connecting, connected, error)
- **Graceful Degradation**: Falls back to polling if disabled
- **Automatic Cleanup**: Cancels listeners on dispose

### **2. Feature Flags** (`flutter_app/lib/utils/feature_flags.dart`)

Centralized feature flag management for all features:

- **Real-time updates**: `realtimeUpdatesEnabled` (default: false)
- **Redis cache**: `redisCacheEnabled` (default: true)
- **Optimistic UI**: `optimisticUIEnabled` (default: true)
- **Client cache**: `clientCacheEnabled` (default: true)
- And many more...

---

## 🧪 **Testing Scenarios**

### **Test 1: Timeline Real-Time Updates**

**Goal**: Verify timeline updates instantly when new activities are logged.

**Steps**:
1. Enable real-time updates (see above)
2. Open app on Device A (iPhone/Simulator)
3. Navigate to Timeline
4. Open app on Device B (another device or web)
5. Log a meal on Device B: "I ate 2 eggs"
6. **Expected**: Timeline on Device A updates **instantly** (no refresh needed)
7. **Verify**: Check logs for `🔴 Real-time update: X activities`

**Success Criteria**:
- ✅ Timeline updates within 1-2 seconds
- ✅ No manual refresh needed
- ✅ Connection state shows "connected"

---

### **Test 2: Dashboard Real-Time Stats**

**Goal**: Verify dashboard stats update instantly when new meals are logged.

**Steps**:
1. Enable real-time updates
2. Open app on Device A
3. Navigate to Home (Dashboard)
4. Note current calorie count
5. Log a meal on Device B: "I ate 3 bananas"
6. **Expected**: Dashboard on Device A updates **instantly**
7. **Verify**: Calorie rings and stats reflect new meal

**Success Criteria**:
- ✅ Dashboard updates within 1-2 seconds
- ✅ Calorie rings animate to new values
- ✅ Stats are accurate

---

### **Test 3: Connection State Management**

**Goal**: Verify connection state is tracked correctly.

**Steps**:
1. Enable real-time updates
2. Open app
3. Check initial connection state: `connecting` → `connected`
4. Turn off WiFi/cellular
5. **Expected**: Connection state changes to `error` or `disconnected`
6. Turn on WiFi/cellular
7. **Expected**: Connection state changes back to `connected`
8. **Verify**: Timeline still works (reconnects automatically)

**Success Criteria**:
- ✅ Connection state transitions correctly
- ✅ Automatic reconnection works
- ✅ No crashes or errors

---

### **Test 4: Graceful Degradation (Disabled)**

**Goal**: Verify app works normally when real-time is disabled.

**Steps**:
1. **Disable** real-time updates (set `realtimeUpdatesEnabled = false`)
2. Rebuild app
3. Open app
4. Navigate to Timeline
5. Log a meal: "I ate 2 eggs"
6. **Expected**: Timeline updates using **polling** (client-side cache + background refresh)
7. **Verify**: Check logs for `⚪ Real-time disabled, using polling`

**Success Criteria**:
- ✅ App works normally (no crashes)
- ✅ Timeline updates (via polling)
- ✅ No real-time listeners are created

---

### **Test 5: Multiple Listeners**

**Goal**: Verify multiple listeners don't conflict.

**Steps**:
1. Enable real-time updates
2. Open app
3. Navigate to Timeline (creates timeline listener)
4. Navigate to Home (creates dashboard listener)
5. Navigate back to Timeline
6. **Expected**: Old listener is cancelled, new one is created
7. **Verify**: Check logs for `🔴 Stopped timeline listener` and `🔴 Starting real-time timeline listener`

**Success Criteria**:
- ✅ Only one listener per user per type
- ✅ Old listeners are cancelled
- ✅ No memory leaks

---

### **Test 6: Offline/Online Transitions**

**Goal**: Verify app handles offline/online transitions gracefully.

**Steps**:
1. Enable real-time updates
2. Open app (online)
3. Navigate to Timeline
4. Turn off WiFi/cellular (go offline)
5. Wait 10 seconds
6. Turn on WiFi/cellular (go online)
7. **Expected**: Timeline reconnects and updates
8. **Verify**: Check logs for reconnection messages

**Success Criteria**:
- ✅ No crashes when going offline
- ✅ Automatic reconnection when online
- ✅ Timeline updates after reconnection

---

### **Test 7: Performance Impact**

**Goal**: Measure performance impact of real-time listeners.

**Steps**:
1. Enable real-time updates
2. Open app
3. Navigate to Timeline
4. Monitor memory usage (Xcode Instruments)
5. Monitor battery usage (Settings → Battery)
6. Compare with real-time disabled

**Success Criteria**:
- ✅ Memory usage increase < 10MB
- ✅ Battery usage similar to polling
- ✅ No significant performance degradation

---

## 📊 **Expected Logs**

### **When Real-Time is Enabled**

```
🔴 Real-time service ENABLED
🔴 Starting real-time timeline listener for user: abc123
🔴 Connection state: connecting
🔴 Connection state: connected
🔴 Real-time update: 15 activities
🔴 Real-time dashboard update: 2000 cal, 150.0g protein
```

### **When Real-Time is Disabled**

```
⚪ Real-time service DISABLED (using polling)
⚪ Real-time disabled, skipping timeline listener
⚪ Real-time disabled, skipping dashboard listener
⚡ Cache hit! Loaded 15 activities instantly
```

### **When Connection Fails**

```
❌ Timeline listener error: [firebase_firestore/unavailable] The service is currently unavailable
🔴 Connection state: error
```

---

## 🔧 **Troubleshooting**

### **Issue: Real-Time Updates Not Working**

**Symptoms**:
- Timeline doesn't update automatically
- No `🔴` logs in console

**Solutions**:
1. Check feature flag: `realtimeUpdatesEnabled = true`
2. Rebuild app: `flutter run`
3. Check Firebase rules allow read access
4. Check internet connection
5. Check Firestore indexes are deployed

---

### **Issue: Connection State Always "Error"**

**Symptoms**:
- Connection state shows "error"
- Logs show Firestore errors

**Solutions**:
1. Check Firebase project is configured correctly
2. Check `google-services.json` (Android) or `GoogleService-Info.plist` (iOS)
3. Check Firebase rules:
   ```javascript
   match /users/{userId}/fitness_logs/{logId} {
     allow read: if request.auth != null && request.auth.uid == userId;
   }
   ```
4. Check internet connection

---

### **Issue: Multiple Listeners Created**

**Symptoms**:
- Logs show multiple `Starting real-time listener` messages
- Memory usage increases

**Solutions**:
1. Check `stopListeningToTimeline()` is called before creating new listener
2. Check `dispose()` is called when screen is disposed
3. Add debug logs to track listener lifecycle

---

### **Issue: App Crashes on Offline**

**Symptoms**:
- App crashes when WiFi is turned off
- Error logs show Firestore exceptions

**Solutions**:
1. Check `cancelOnError: false` in listener setup
2. Check error handlers are implemented
3. Add try-catch blocks around Firestore operations

---

## 🚀 **Production Deployment**

### **Gradual Rollout**

1. **Phase 1: Internal Testing** (1 week)
   - Enable for internal team only
   - Monitor logs and performance
   - Fix any issues

2. **Phase 2: Beta Testing** (1 week)
   - Enable for 10% of users (A/B test)
   - Monitor crash rate, performance, battery usage
   - Collect user feedback

3. **Phase 3: Full Rollout** (1 week)
   - Enable for 50% of users
   - Monitor metrics
   - If stable, enable for 100%

### **Rollback Plan**

If issues occur:

1. **Immediate Rollback** (< 1 minute):
   ```dart
   // In feature_flags.dart
   static const bool realtimeUpdatesEnabled = false;
   ```
   Push update via Firebase Remote Config (instant rollback)

2. **Verify Rollback**:
   - Check logs for `⚪ Real-time disabled`
   - Verify polling is working
   - Monitor error rate drops

---

## 📈 **Monitoring**

### **Key Metrics to Track**

1. **Connection State**:
   - % of users in "connected" state
   - Average time to connect
   - Reconnection success rate

2. **Update Latency**:
   - Time from log creation to timeline update
   - Target: < 2 seconds

3. **Error Rate**:
   - Firestore listener errors
   - Connection errors
   - Target: < 1%

4. **Performance**:
   - Memory usage increase
   - Battery usage impact
   - Target: < 10% increase

5. **User Engagement**:
   - Time spent in app
   - Refresh rate (should decrease)
   - User satisfaction (surveys)

---

## ✅ **Next Steps**

After testing:

1. ✅ Enable real-time for internal team
2. ✅ Monitor for 1 week
3. ✅ Fix any issues
4. ✅ Enable for 10% of users (A/B test)
5. ✅ Monitor metrics
6. ✅ Gradual rollout to 100%

---

## 📚 **Additional Resources**

- [Firestore Real-Time Updates](https://firebase.google.com/docs/firestore/query-data/listen)
- [Flutter Firestore Snapshots](https://firebase.flutter.dev/docs/firestore/usage#realtime-changes)
- [Feature Flags Best Practices](https://martinfowler.com/articles/feature-toggles.html)

---

**Questions?** Check logs for detailed real-time behavior or contact the team.

