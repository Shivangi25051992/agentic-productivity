# 📊 Production Monitoring Setup Guide

## Overview

Production monitoring has been implemented using:
- **Firebase Performance Monitoring**: Track app performance, API latency, screen rendering
- **Firebase Crashlytics**: Automatic crash reporting and analysis
- **Sentry**: Advanced error tracking, breadcrumbs, user context

---

## 📋 **What's Implemented**

### **1. MonitoringService** (`flutter_app/lib/services/monitoring_service.dart`)

A comprehensive monitoring service that provides:

- **Performance Traces**: Track custom operations (timeline load, API calls, etc.)
- **HTTP Metrics**: Automatic tracking of API call performance
- **Error Logging**: Send errors to Crashlytics and Sentry
- **Breadcrumbs**: Track user actions leading to errors
- **User Context**: Associate errors with specific users
- **Custom Events**: Track business metrics
- **Screen Tracking**: Monitor navigation patterns

### **2. Feature Flags** (`flutter_app/lib/utils/feature_flags.dart`)

Monitoring is controlled by feature flags:
- `performanceMonitoringEnabled` (default: false)
- `sentryEnabled` (default: false)
- `customAnalyticsEnabled` (default: false)

---

## 🚀 **Setup Instructions**

### **PART 1: Firebase Performance Monitoring** (5 minutes)

#### **Step 1: Enable in Firebase Console**

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `productivityai-mvp`
3. Navigate to **Performance** (left sidebar)
4. Click **Get Started**
5. Follow the setup wizard (should auto-detect your iOS app)

#### **Step 2: Verify Configuration**

Check that `GoogleService-Info.plist` (iOS) contains:
```xml
<key>FIREBASE_PERFORMANCE_COLLECTION_ENABLED</key>
<true/>
```

If not, add it manually.

#### **Step 3: Enable Feature Flag**

Edit `flutter_app/lib/utils/feature_flags.dart`:
```dart
/// Enable Firebase Performance Monitoring
/// Status: IMPLEMENTED (Task 10)
/// Default: false (needs setup)
static const bool performanceMonitoringEnabled = true;  // ← Change to true
```

#### **Step 4: Rebuild App**

```bash
cd flutter_app
flutter clean
flutter pub get
flutter run
```

#### **Step 5: Verify**

1. Open app
2. Navigate around (Timeline, Home, Profile)
3. Check Firebase Console → Performance (data appears within 1 hour)

---

### **PART 2: Firebase Crashlytics** (5 minutes)

#### **Step 1: Enable in Firebase Console**

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `productivityai-mvp`
3. Navigate to **Crashlytics** (left sidebar)
4. Click **Get Started**
5. Follow the setup wizard

#### **Step 2: Verify Configuration**

Crashlytics is **automatically enabled** (no feature flag needed).

#### **Step 3: Test Crash Reporting** (Optional)

Add a test button in your app:

```dart
ElevatedButton(
  onPressed: () {
    monitoring.testCrash();
  },
  child: const Text('Test Crash'),
)
```

Tap the button, app will crash, and report will appear in Firebase Console within 5 minutes.

#### **Step 4: Remove Test Button**

Remove the test button before deploying to production!

---

### **PART 3: Sentry Error Tracking** (10 minutes)

#### **Step 1: Create Sentry Account**

1. Go to [sentry.io](https://sentry.io/)
2. Sign up (free tier: 5,000 events/month)
3. Create a new project:
   - Platform: **Flutter**
   - Name: `yuvi-productivity-app`

#### **Step 2: Get DSN**

After creating the project, you'll see a **DSN** (Data Source Name):
```
https://abc123@o123456.ingest.sentry.io/789012
```

Copy this DSN.

#### **Step 3: Configure Sentry in App**

Edit `flutter_app/lib/main.dart`:

```dart
import 'package:sentry_flutter/sentry_flutter.dart';
import 'utils/feature_flags.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Sentry
  if (FeatureFlags.sentryEnabled) {
    await SentryFlutter.init(
      (options) {
        options.dsn = 'YOUR_DSN_HERE';  // ← Paste your DSN
        options.tracesSampleRate = 0.1;  // 10% of transactions
        options.environment = 'production';  // or 'development'
      },
      appRunner: () => runApp(const AppRoot()),
    );
  } else {
    runApp(const AppRoot());
  }
}
```

#### **Step 4: Enable Feature Flag**

Edit `flutter_app/lib/utils/feature_flags.dart`:
```dart
/// Enable Sentry error tracking
/// Status: IMPLEMENTED (Task 10)
/// Default: false (needs setup)
static const bool sentryEnabled = true;  // ← Change to true
```

#### **Step 5: Rebuild App**

```bash
cd flutter_app
flutter clean
flutter pub get
flutter run
```

#### **Step 6: Test Error Tracking**

Trigger an error in the app (e.g., try to access a null value), and check Sentry dashboard for the error report.

---

## 📊 **Usage Examples**

### **Example 1: Track Timeline Load Performance**

```dart
// In TimelineProvider
Future<void> fetchTimeline() async {
  // Start trace
  await monitoring.startTrace('timeline_load');
  
  try {
    // Fetch data
    final response = await _apiService.getTimeline(...);
    
    // Add metrics
    await monitoring.addTraceMetric('timeline_load', 'activity_count', response.activities.length);
    await monitoring.addTraceAttribute('timeline_load', 'types', types);
    
    // Process data
    _activities = response.activities;
    
  } catch (e) {
    // Log error
    await monitoring.logError(e, StackTrace.current, reason: 'Failed to fetch timeline');
  } finally {
    // Stop trace
    await monitoring.stopTrace('timeline_load');
  }
}
```

### **Example 2: Track API Call Performance**

```dart
// In ApiService
Future<Map<String, dynamic>> sendChatMessage(String message, String type) async {
  // Create HTTP metric
  final metric = monitoring.createHttpMetric('/chat', HttpMethod.Post);
  await metric?.start();
  
  try {
    final resp = await _dio.post('/chat', data: {...});
    
    // Set response details
    metric?.httpResponseCode = resp.statusCode;
    metric?.responsePayloadSize = resp.data.toString().length;
    
    return resp.data;
  } catch (e) {
    metric?.httpResponseCode = 500;
    await monitoring.logError(e, StackTrace.current, reason: 'Chat API failed');
    rethrow;
  } finally {
    await metric?.stop();
  }
}
```

### **Example 3: Log Error with Context**

```dart
try {
  // Some operation
  await saveData();
} catch (e, stackTrace) {
  await monitoring.logError(
    e,
    stackTrace,
    reason: 'Failed to save data',
    context: {
      'user_id': userId,
      'data_size': data.length,
      'timestamp': DateTime.now().toIso8601String(),
    },
    fatal: false,
  );
}
```

### **Example 4: Add Breadcrumbs**

```dart
// Track user actions
await monitoring.addBreadcrumb('User tapped "Log Meal" button');
await monitoring.addBreadcrumb('User entered: "2 eggs"');
await monitoring.addBreadcrumb('API call started');
// ... if error occurs, Sentry will show these breadcrumbs
```

### **Example 5: Set User Context**

```dart
// After login
await monitoring.setUserContext(
  userId: user.uid,
  email: user.email,
  username: user.displayName,
  extras: {
    'plan': 'premium',
    'signup_date': user.createdAt,
  },
);

// Before logout
await monitoring.clearUserContext();
```

### **Example 6: Track Screen Views**

```dart
// In each screen's initState
@override
void initState() {
  super.initState();
  monitoring.trackScreenView('Timeline');
}
```

---

## 📈 **Monitoring Dashboards**

### **Firebase Performance**

Go to: [Firebase Console → Performance](https://console.firebase.google.com/)

**Key Metrics to Monitor**:
- App start time
- Screen rendering time
- API call latency
- Custom traces (timeline_load, dashboard_load, etc.)

**Alerts**:
Set up alerts for:
- API latency > 3 seconds
- App start time > 5 seconds
- Screen rendering > 1 second

### **Firebase Crashlytics**

Go to: [Firebase Console → Crashlytics](https://console.firebase.google.com/)

**Key Metrics to Monitor**:
- Crash-free users (target: > 99.5%)
- Total crashes
- Most common crashes
- Crashes by OS version/device

**Alerts**:
Set up alerts for:
- New crash type detected
- Crash spike (> 10 crashes in 1 hour)

### **Sentry**

Go to: [sentry.io → Projects → yuvi-productivity-app](https://sentry.io/)

**Key Metrics to Monitor**:
- Error rate
- Affected users
- Most common errors
- Error trends (increasing/decreasing)

**Alerts**:
Set up alerts for:
- Error spike (> 50 errors in 10 minutes)
- New error type
- Error affecting > 10% of users

---

## 🔧 **Troubleshooting**

### **Issue: No Data in Firebase Performance**

**Symptoms**:
- Firebase Performance dashboard is empty
- No traces or metrics visible

**Solutions**:
1. Wait 1 hour (data takes time to appear)
2. Check feature flag: `performanceMonitoringEnabled = true`
3. Check `GoogleService-Info.plist` has Performance enabled
4. Rebuild app: `flutter clean && flutter run`
5. Check Firebase Console → Performance → Settings (collection enabled?)

---

### **Issue: Crashes Not Appearing in Crashlytics**

**Symptoms**:
- App crashes but no reports in Crashlytics
- Dashboard shows "No crashes yet"

**Solutions**:
1. Wait 5 minutes (crashes take time to upload)
2. Check internet connection (crashes upload on next app start)
3. Force crash with test button (see Part 2, Step 3)
4. Check Firebase Console → Crashlytics → Settings (enabled?)
5. Restart app after crash (uploads happen on restart)

---

### **Issue: Sentry Not Receiving Errors**

**Symptoms**:
- Errors occur but don't appear in Sentry
- Sentry dashboard is empty

**Solutions**:
1. Check feature flag: `sentryEnabled = true`
2. Check DSN is correct in `main.dart`
3. Check internet connection
4. Test with `monitoring.testCrash()`
5. Check Sentry project settings (DSN active?)

---

## 🚀 **Production Deployment**

### **Gradual Rollout**

1. **Phase 1: Internal Testing** (1 week)
   - Enable for internal team only
   - Monitor dashboards daily
   - Fix any issues

2. **Phase 2: Beta Testing** (1 week)
   - Enable for 10% of users
   - Monitor crash rate, error rate
   - Collect feedback

3. **Phase 3: Full Rollout** (1 week)
   - Enable for 50% of users
   - Monitor metrics
   - If stable, enable for 100%

### **Rollback Plan**

If monitoring causes issues:

1. **Disable Performance Monitoring**:
   ```dart
   static const bool performanceMonitoringEnabled = false;
   ```

2. **Disable Sentry**:
   ```dart
   static const bool sentryEnabled = false;
   ```

3. **Crashlytics cannot be disabled** (always on, minimal overhead)

---

## 📊 **Key Performance Indicators (KPIs)**

### **Performance**
- **App start time**: < 3 seconds (target)
- **Timeline load**: < 1 second (target)
- **API latency**: < 500ms (target)
- **Screen rendering**: < 16ms (60fps)

### **Stability**
- **Crash-free users**: > 99.5% (target)
- **Error rate**: < 1% of sessions
- **ANR rate**: < 0.1% (Android only)

### **User Experience**
- **Session duration**: > 5 minutes (engaged users)
- **Screens per session**: > 10 (active usage)
- **Retention (Day 1)**: > 40%
- **Retention (Day 7)**: > 20%

---

## ✅ **Checklist**

Before deploying to production:

- [ ] Firebase Performance enabled in Console
- [ ] Firebase Crashlytics enabled in Console
- [ ] Sentry project created and DSN configured
- [ ] Feature flags enabled
- [ ] Test crash reporting works
- [ ] Test error tracking works
- [ ] Dashboards accessible
- [ ] Alerts configured
- [ ] Team trained on dashboards
- [ ] Rollback plan documented

---

## 📚 **Additional Resources**

- [Firebase Performance Docs](https://firebase.google.com/docs/perf-mon)
- [Firebase Crashlytics Docs](https://firebase.google.com/docs/crashlytics)
- [Sentry Flutter Docs](https://docs.sentry.io/platforms/flutter/)
- [Flutter Performance Best Practices](https://flutter.dev/docs/perf)

---

**Questions?** Check monitoring dashboards or contact the team.

