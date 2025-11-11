# 🔔 Agentic Notification Framework & Device Integration Plan
**Date**: November 11, 2025  
**Version**: 1.0 - Enterprise-Grade Architecture  
**Status**: Planning Phase

---

## 📋 Executive Summary

This document outlines an **enterprise-grade agentic notification framework** and **comprehensive device integration strategy** for iPhone (HealthKit), Apple Watch, Fitbit, and major health/wearable ecosystems. This framework is designed to be:

- **Modular & Event-Driven**: Agent-based architecture for intelligent notifications
- **Privacy-First**: User consent, granular controls, GDPR compliance
- **Multi-Channel**: Local push, in-app, device/watch, email
- **Extensible**: Easy to add new devices (Garmin, Whoop, Samsung Health)
- **Production-Ready**: Follows best practices from existing codebase

---

## 1️⃣ AGENTIC NOTIFICATION FRAMEWORK

### 1.1 Core Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENTIC NOTIFICATION FRAMEWORK                   │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  Event Sources   │
├──────────────────┤
│ • User Actions   │──┐
│ • Device Sync    │  │
│ • AI/Coach       │  │
│ • Backend Cron   │  │
│ • 3rd Party Push │  │
└──────────────────┘  │
                      ▼
            ┌─────────────────┐
            │ Decision Engine │
            │   (AI Agent)    │
            ├─────────────────┤
            │ • Priority      │
            │ • Timing        │
            │ • Frequency     │
            │ • User Prefs    │
            └─────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Local Push   │ │  In-App      │ │ Device/Watch │
│  Provider    │ │  Provider    │ │  Provider    │
└──────────────┘ └──────────────┘ └──────────────┘
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   iOS/       │ │  Banners/    │ │ Apple Watch/ │
│  Android     │ │  Toasts      │ │   Fitbit     │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

### 1.2 Notification Types

| Type | Description | Priority | Example |
|------|-------------|----------|---------|
| **Scheduled Reminders** | Time-based nudges | Medium | "Time to log lunch! 🍽️" |
| **Habit Nudges** | Behavior-driven | Medium | "Don't forget to log water!" |
| **Goal Updates** | Progress milestones | High | "2,000 steps left to goal!" |
| **Achievements** | Unlocks, badges | High | "🎉 7-day streak unlocked!" |
| **AI-Driven** | Contextual insights | Medium | "You just met your protein target!" |
| **Critical Alerts** | Urgent issues | Critical | "Sync failed - action required" |
| **Social/Coach** | Engagement | Low | "Coach replied to your question" |

---

### 1.3 Event Sources & Triggers

```dart
// Event-driven notification triggers
enum NotificationTrigger {
  // User Actions
  userLoggedMeal,
  userCompletedWorkout,
  userMissedLog,
  userAchievedGoal,
  
  // Device Sync
  deviceSyncCompleted,
  newHealthDataReceived,
  deviceDisconnected,
  
  // AI/Coach
  patternDetected,
  goalMissed,
  insightGenerated,
  
  // Backend Scheduled
  mealTimeReminder,
  waterReminder,
  workoutReminder,
  streakAtRisk,
  
  // Third-Party
  fitbitPushReceived,
  appleHealthUpdated,
  wearOSEventReceived,
}
```

---

### 1.4 Notification Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                      NOTIFICATION LIFECYCLE                         │
└─────────────────────────────────────────────────────────────────────┘

1. EVENT TRIGGERED
   ├─ User logs meal
   ├─ Device syncs new workout
   ├─ AI detects pattern
   └─ Cron job fires reminder

2. DECISION ENGINE (AI Agent)
   ├─ Check user preferences (enabled/disabled)
   ├─ Check DND windows (quiet hours)
   ├─ Check frequency limits (max 5/day)
   ├─ Calculate priority score
   └─ Determine optimal timing

3. PROVIDER DISPATCH
   ├─ Select channels (push, in-app, watch)
   ├─ Format payload per channel
   ├─ Queue for delivery
   └─ Track delivery status

4. USER INTERACTION
   ├─ View notification
   ├─ Take action (log, dismiss, snooze)
   ├─ Update preferences
   └─ Feedback to AI agent

5. ANALYTICS & LEARNING
   ├─ Track open rate
   ├─ Track action rate
   ├─ Adjust frequency
   └─ Improve AI model
```

---

## 2️⃣ DEVICE INTEGRATION STRATEGY

### 2.1 iPhone Health Data (Apple HealthKit)

#### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLE HEALTHKIT INTEGRATION                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   Your App       │
│  (Flutter)       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ health Package   │  (pub.dev/packages/health)
│  or Swift Bridge │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   HealthKit      │
│   (iOS Native)   │
├──────────────────┤
│ • Steps          │
│ • Workouts       │
│ • Calories       │
│ • Sleep          │
│ • Nutrition      │
│ • Heart Rate     │
│ • Mindfulness    │
└──────────────────┘
```

#### Data Flow

**READ (from HealthKit):**
- Steps (daily, hourly)
- Workouts (type, duration, calories)
- Active energy burned
- Sleep analysis (duration, quality)
- Heart rate (resting, active)
- Nutrition (if logged in Apple Health)
- Mindfulness minutes

**WRITE (to HealthKit):**
- Logged meals (nutrition data)
- Workouts (if logged in your app)
- Water intake
- Mindfulness sessions

#### Sync Strategy

```dart
class AppleHealthKitProvider {
  final Health health = Health();
  
  // Permissions
  static const types = [
    HealthDataType.STEPS,
    HealthDataType.WORKOUT,
    HealthDataType.ACTIVE_ENERGY_BURNED,
    HealthDataType.SLEEP_ASLEEP,
    HealthDataType.HEART_RATE,
    HealthDataType.NUTRITION,
    HealthDataType.WATER,
  ];
  
  Future<bool> requestPermissions() async {
    return await health.requestAuthorization(types);
  }
  
  Future<List<HealthDataPoint>> fetchTodayData() async {
    final now = DateTime.now();
    final startOfDay = DateTime(now.year, now.month, now.day);
    
    return await health.getHealthDataFromTypes(
      startOfDay,
      now,
      types,
    );
  }
  
  Future<void> syncToBackend(List<HealthDataPoint> data) async {
    // Convert HealthKit data to your app's format
    // Send to backend API
    // Update local cache
    // Trigger notifications if needed
  }
  
  // Background sync (iOS Background Fetch)
  Future<void> backgroundSync() async {
    final data = await fetchTodayData();
    await syncToBackend(data);
  }
}
```

#### Conflict Resolution

```dart
class HealthKitSyncAgent {
  Future<void> mergeData(
    List<HealthDataPoint> healthKitData,
    List<FitnessLog> appData,
  ) async {
    // 1. Detect conflicts (same timestamp, different values)
    final conflicts = detectConflicts(healthKitData, appData);
    
    // 2. Resolution strategy
    for (var conflict in conflicts) {
      if (conflict.healthKitValue > conflict.appValue) {
        // HealthKit is authoritative for device data
        await updateAppData(conflict.healthKitValue);
      } else if (conflict.requiresUserInput) {
        // Show user prompt to resolve
        await promptUserResolution(conflict);
      }
    }
    
    // 3. Merge non-conflicting data
    await mergeNonConflictingData(healthKitData, appData);
  }
}
```

---

### 2.2 Apple Watch Integration

#### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLE WATCH INTEGRATION                          │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐          ┌──────────────────┐
│   iPhone App     │◀────────▶│   Apple Watch    │
│   (Flutter)      │  Watch   │   (watchOS)      │
│                  │Connectivity│                  │
└──────────────────┘          └──────────────────┘
         │                             │
         ▼                             ▼
┌──────────────────┐          ┌──────────────────┐
│   HealthKit      │          │  Complications   │
│   (Shared Data)  │          │  (Glances)       │
└──────────────────┘          └──────────────────┘
```

#### Features

**Notifications:**
- Meal reminders with haptic feedback
- Workout start/end notifications
- Streak achievements
- Water intake reminders
- Goal progress updates

**Complications (Optional watchOS App):**
- Today's calorie progress ring
- Current streak count
- Water intake progress
- Next meal reminder

**Quick Actions:**
- Log water (tap complication)
- Start workout (tap to open app)
- View daily summary

#### Implementation

```dart
class AppleWatchProvider implements NotificationProvider {
  final WatchConnectivity connectivity = WatchConnectivity();
  
  @override
  Future<void> send(NotificationPayload payload) async {
    if (!await connectivity.isReachable) {
      // Queue for later delivery
      await queueForWatch(payload);
      return;
    }
    
    // Send to watch
    await connectivity.sendMessage({
      'type': payload.type,
      'title': payload.title,
      'body': payload.body,
      'action': payload.action,
      'haptic': payload.haptic, // light, medium, heavy
    });
  }
  
  Future<void> syncDailyStats(DailyStats stats) async {
    // Update watch complications
    await connectivity.updateApplicationContext({
      'calories': stats.caloriesConsumed,
      'caloriesGoal': stats.caloriesGoal,
      'streak': stats.currentStreak,
      'waterMl': stats.waterMl,
      'waterGoal': stats.waterGoal,
    });
  }
}
```

---

### 2.3 Fitbit Integration

#### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      FITBIT INTEGRATION                             │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   Your App       │
│  (Flutter)       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ fitbitter Package│  (pub.dev/packages/fitbitter)
│   OAuth 2.0      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Fitbit Web API   │
├──────────────────┤
│ • Steps          │
│ • Heart Rate     │
│ • Activity       │
│ • Sleep          │
│ • Nutrition      │
└──────────────────┘
```

#### OAuth Flow

```dart
class FitbitAuthProvider {
  final FitbitConnector connector = FitbitConnector(
    clientID: 'YOUR_CLIENT_ID',
    clientSecret: 'YOUR_CLIENT_SECRET',
    redirectUri: 'yourapp://fitbit-callback',
  );
  
  Future<void> authorize() async {
    // 1. Open Fitbit OAuth page
    final authUrl = connector.authorizeUrl;
    await launchUrl(authUrl);
    
    // 2. Handle callback
    final code = await waitForCallback();
    
    // 3. Exchange code for token
    final token = await connector.getAccessToken(code);
    
    // 4. Store token securely
    await secureStorage.write(key: 'fitbit_token', value: token);
  }
}
```

#### Data Sync

```dart
class FitbitSyncProvider {
  final FitbitDataManager dataManager = FitbitDataManager(
    clientID: 'YOUR_CLIENT_ID',
    clientSecret: 'YOUR_CLIENT_SECRET',
  );
  
  Future<void> syncTodayData() async {
    final today = DateTime.now();
    
    // Fetch steps
    final steps = await dataManager.fetch(
      FitbitActivityAPIURL.withUserIDAndDay(
        userID: 'current',
        date: today,
      ),
    );
    
    // Fetch heart rate
    final heartRate = await dataManager.fetch(
      FitbitHeartAPIURL.dayWithUserID(
        date: today,
        userID: 'current',
      ),
    );
    
    // Fetch sleep
    final sleep = await dataManager.fetch(
      FitbitSleepAPIURL.withUserIDAndDay(
        date: today,
        userID: 'current',
      ),
    );
    
    // Sync to backend
    await syncToBackend({
      'steps': steps,
      'heartRate': heartRate,
      'sleep': sleep,
    });
  }
  
  // Background sync (every 15 minutes)
  Future<void> setupBackgroundSync() async {
    Timer.periodic(Duration(minutes: 15), (timer) async {
      await syncTodayData();
    });
  }
}
```

#### Push Notifications to Fitbit

```dart
class FitbitNotificationProvider implements NotificationProvider {
  @override
  Future<void> send(NotificationPayload payload) async {
    // Fitbit API doesn't support direct push notifications
    // But we can:
    // 1. Update user's Fitbit dashboard via API
    // 2. Send email notifications (if user enabled)
    // 3. Show in-app when they open Fitbit app
    
    // For now, log and queue for next sync
    await queueForFitbitSync(payload);
  }
}
```

---

### 2.4 Other Device Integrations

#### Google Fit (Android)

```dart
class GoogleFitProvider {
  final GoogleFit fit = GoogleFit();
  
  Future<void> requestPermissions() async {
    await fit.requestAuthorization([
      HealthDataType.STEPS,
      HealthDataType.WORKOUT,
      HealthDataType.HEART_RATE,
      HealthDataType.SLEEP,
    ]);
  }
  
  Future<void> syncTodayData() async {
    final data = await fit.getHealthDataFromTypes(
      DateTime.now().subtract(Duration(days: 1)),
      DateTime.now(),
      [HealthDataType.STEPS, HealthDataType.WORKOUT],
    );
    
    await syncToBackend(data);
  }
}
```

#### Garmin Connect

```dart
class GarminProvider {
  // Use Garmin Health API
  // OAuth 1.0a flow
  // REST API for data sync
  
  Future<void> authorize() async {
    // Implement OAuth 1.0a
  }
  
  Future<void> syncActivities() async {
    // Fetch activities from Garmin
    // Parse FIT files if needed
    // Sync to backend
  }
}
```

#### Samsung Health

```dart
class SamsungHealthProvider {
  // Use Samsung Health SDK (Android only)
  // Requires Samsung Health app installed
  
  Future<void> requestPermissions() async {
    // Request read/write permissions
  }
  
  Future<void> syncData() async {
    // Fetch steps, workouts, sleep
    // Sync to backend
  }
}
```

---

## 3️⃣ NOTIFICATION PROVIDER IMPLEMENTATION

### 3.1 Abstract Provider Interface

```dart
// lib/services/notifications/notification_provider.dart

abstract class NotificationProvider {
  Future<void> send(NotificationPayload payload);
  Future<bool> isAvailable();
  Future<void> initialize();
  Future<void> dispose();
}

class NotificationPayload {
  final String id;
  final NotificationType type;
  final String title;
  final String body;
  final Map<String, dynamic> data;
  final NotificationPriority priority;
  final DateTime? scheduledTime;
  final String? action;
  final String? haptic; // For watch
  
  NotificationPayload({
    required this.id,
    required this.type,
    required this.title,
    required this.body,
    this.data = const {},
    this.priority = NotificationPriority.medium,
    this.scheduledTime,
    this.action,
    this.haptic,
  });
}

enum NotificationType {
  reminder,
  achievement,
  insight,
  alert,
  social,
}

enum NotificationPriority {
  low,
  medium,
  high,
  critical,
}
```

---

### 3.2 Local Push Provider

```dart
// lib/services/notifications/local_push_provider.dart

class LocalPushProvider implements NotificationProvider {
  final FlutterLocalNotificationsPlugin _plugin = FlutterLocalNotificationsPlugin();
  
  @override
  Future<void> initialize() async {
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    
    await _plugin.initialize(
      const InitializationSettings(
        android: androidSettings,
        iOS: iosSettings,
      ),
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );
  }
  
  @override
  Future<void> send(NotificationPayload payload) async {
    if (payload.scheduledTime != null) {
      await _scheduleNotification(payload);
    } else {
      await _sendImmediateNotification(payload);
    }
  }
  
  Future<void> _sendImmediateNotification(NotificationPayload payload) async {
    await _plugin.show(
      payload.id.hashCode,
      payload.title,
      payload.body,
      _buildNotificationDetails(payload),
      payload: jsonEncode(payload.data),
    );
  }
  
  Future<void> _scheduleNotification(NotificationPayload payload) async {
    await _plugin.zonedSchedule(
      payload.id.hashCode,
      payload.title,
      payload.body,
      tz.TZDateTime.from(payload.scheduledTime!, tz.local),
      _buildNotificationDetails(payload),
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.absoluteTime,
      payload: jsonEncode(payload.data),
    );
  }
  
  NotificationDetails _buildNotificationDetails(NotificationPayload payload) {
    return NotificationDetails(
      android: AndroidNotificationDetails(
        _getChannelId(payload.type),
        _getChannelName(payload.type),
        importance: _getImportance(payload.priority),
        priority: _getPriority(payload.priority),
        icon: _getIcon(payload.type),
      ),
      iOS: DarwinNotificationDetails(
        presentAlert: true,
        presentBadge: true,
        presentSound: true,
        interruptionLevel: _getInterruptionLevel(payload.priority),
      ),
    );
  }
  
  void _onNotificationTapped(NotificationResponse response) {
    // Handle notification tap
    // Navigate to relevant screen
    // Track analytics
  }
  
  @override
  Future<bool> isAvailable() async {
    if (Platform.isIOS) {
      return await _plugin.resolvePlatformSpecificImplementation<
          IOSFlutterLocalNotificationsPlugin>()
          ?.requestPermissions(alert: true, badge: true, sound: true) ?? false;
    }
    return true; // Android doesn't require runtime permission
  }
  
  @override
  Future<void> dispose() async {
    await _plugin.cancelAll();
  }
}
```

---

### 3.3 In-App Banner Provider

```dart
// lib/services/notifications/in_app_banner_provider.dart

class InAppBannerProvider implements NotificationProvider {
  final GlobalKey<NavigatorState> navigatorKey;
  
  InAppBannerProvider(this.navigatorKey);
  
  @override
  Future<void> send(NotificationPayload payload) async {
    final context = navigatorKey.currentContext;
    if (context == null) return;
    
    // Show banner at top of screen
    showTopSnackBar(
      Overlay.of(context),
      CustomSnackBar.success(
        message: payload.body,
        icon: _getIcon(payload.type),
        backgroundColor: _getColor(payload.type),
      ),
      displayDuration: Duration(seconds: 3),
    );
  }
  
  @override
  Future<bool> isAvailable() async => true;
  
  @override
  Future<void> initialize() async {}
  
  @override
  Future<void> dispose() async {}
}
```

---

### 3.4 Notification Agent (Decision Engine)

```dart
// lib/services/notifications/notification_agent.dart

class NotificationAgent {
  final List<NotificationProvider> providers;
  final NotificationPreferences preferences;
  final NotificationAnalytics analytics;
  
  NotificationAgent({
    required this.providers,
    required this.preferences,
    required this.analytics,
  });
  
  Future<void> notify(NotificationPayload payload) async {
    // 1. Check if user has enabled this type
    if (!preferences.isEnabled(payload.type)) {
      print('🔕 Notification disabled by user: ${payload.type}');
      return;
    }
    
    // 2. Check DND (Do Not Disturb) window
    if (preferences.isInDNDWindow(DateTime.now())) {
      print('🔕 In DND window, queuing notification');
      await _queueForLater(payload);
      return;
    }
    
    // 3. Check frequency limits
    if (await _exceedsFrequencyLimit(payload.type)) {
      print('🔕 Frequency limit exceeded for ${payload.type}');
      return;
    }
    
    // 4. Dispatch to providers
    for (var provider in providers) {
      if (await provider.isAvailable()) {
        try {
          await provider.send(payload);
          print('✅ Notification sent via ${provider.runtimeType}');
        } catch (e) {
          print('❌ Failed to send via ${provider.runtimeType}: $e');
        }
      }
    }
    
    // 5. Track analytics
    await analytics.trackNotificationSent(payload);
  }
  
  Future<bool> _exceedsFrequencyLimit(NotificationType type) async {
    final today = DateTime.now();
    final count = await analytics.getNotificationCount(
      type: type,
      since: DateTime(today.year, today.month, today.day),
    );
    
    final limit = preferences.getFrequencyLimit(type);
    return count >= limit;
  }
  
  Future<void> _queueForLater(NotificationPayload payload) async {
    // Queue in local database
    // Will be sent when DND window ends
  }
}
```

---

### 3.5 User Preferences

```dart
// lib/models/notification_preferences.dart

class NotificationPreferences {
  final Map<NotificationType, bool> enabledTypes;
  final List<DNDWindow> dndWindows;
  final Map<NotificationType, int> frequencyLimits;
  
  NotificationPreferences({
    required this.enabledTypes,
    required this.dndWindows,
    required this.frequencyLimits,
  });
  
  bool isEnabled(NotificationType type) {
    return enabledTypes[type] ?? true;
  }
  
  bool isInDNDWindow(DateTime time) {
    for (var window in dndWindows) {
      if (window.contains(time)) return true;
    }
    return false;
  }
  
  int getFrequencyLimit(NotificationType type) {
    return frequencyLimits[type] ?? 5; // Default: 5 per day
  }
  
  factory NotificationPreferences.defaults() {
    return NotificationPreferences(
      enabledTypes: {
        NotificationType.reminder: true,
        NotificationType.achievement: true,
        NotificationType.insight: true,
        NotificationType.alert: true,
        NotificationType.social: false, // Disabled by default
      },
      dndWindows: [
        DNDWindow(start: TimeOfDay(hour: 22, minute: 0), end: TimeOfDay(hour: 8, minute: 0)),
      ],
      frequencyLimits: {
        NotificationType.reminder: 5,
        NotificationType.achievement: 10,
        NotificationType.insight: 3,
        NotificationType.alert: 999,
        NotificationType.social: 5,
      },
    );
  }
}

class DNDWindow {
  final TimeOfDay start;
  final TimeOfDay end;
  
  DNDWindow({required this.start, required this.end});
  
  bool contains(DateTime time) {
    final timeOfDay = TimeOfDay.fromDateTime(time);
    
    // Handle overnight window (e.g., 22:00 - 08:00)
    if (start.hour > end.hour) {
      return timeOfDay.hour >= start.hour || timeOfDay.hour < end.hour;
    }
    
    // Handle same-day window (e.g., 12:00 - 14:00)
    return timeOfDay.hour >= start.hour && timeOfDay.hour < end.hour;
  }
}
```

---

## 4️⃣ IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 3)

```
┌─────────────────────────────────────────────────────────────────────┐
│              PHASE 1: NOTIFICATION FOUNDATION                       │
│                     Duration: 1 week                                │
└─────────────────────────────────────────────────────────────────────┘

Day 1-2: Local Push Notifications
├─ Set up flutter_local_notifications
├─ Implement LocalPushProvider
├─ Add notification channels (Android)
├─ Request permissions (iOS)
└─ Test immediate & scheduled notifications

Day 3-4: In-App Notifications
├─ Implement InAppBannerProvider
├─ Add top_snackbar_flutter package
├─ Design notification UI (banners, toasts)
└─ Test in-app notifications

Day 5: Notification Agent
├─ Implement NotificationAgent
├─ Add NotificationPreferences model
├─ Add NotificationAnalytics
└─ Test decision engine logic

Day 6-7: User Preferences UI
├─ Create notification settings screen
├─ Add enable/disable toggles per type
├─ Add DND window picker
├─ Add frequency limit sliders
└─ Test preferences persistence

Deliverables:
✅ Local push notifications working
✅ In-app banners working
✅ Notification agent with decision logic
✅ User preferences UI
```

---

### Phase 2: Scheduled Reminders (Week 4)

```
┌─────────────────────────────────────────────────────────────────────┐
│            PHASE 2: SCHEDULED REMINDERS                             │
│                     Duration: 1 week                                │
└─────────────────────────────────────────────────────────────────────┘

Day 1-2: Meal Reminders
├─ Add meal time preferences (breakfast, lunch, dinner)
├─ Schedule daily meal reminders
├─ Add snooze functionality
└─ Test meal reminders

Day 3: Water Reminders
├─ Schedule water reminders (every 2 hours)
├─ Add "I drank water" quick action
└─ Test water reminders

Day 4: Workout Reminders
├─ Add workout time preferences
├─ Schedule daily workout reminders
├─ Add "Start workout" quick action
└─ Test workout reminders

Day 5: Streak Reminders
├─ Detect streak at risk (no logs today)
├─ Send reminder at 8 PM if no logs
└─ Test streak reminders

Day 6-7: Custom Reminders
├─ Add custom reminder UI
├─ Allow user to create custom reminders
├─ Support recurring reminders
└─ Test custom reminders

Deliverables:
✅ Meal reminders (breakfast, lunch, dinner)
✅ Water reminders (every 2 hours)
✅ Workout reminders (daily)
✅ Streak reminders (if at risk)
✅ Custom user-defined reminders
```

---

### Phase 3: Apple HealthKit (Week 7)

```
┌─────────────────────────────────────────────────────────────────────┐
│            PHASE 3: APPLE HEALTHKIT INTEGRATION                     │
│                     Duration: 1 week                                │
└─────────────────────────────────────────────────────────────────────┘

Day 1-2: HealthKit Setup
├─ Add health package to pubspec.yaml
├─ Configure Info.plist permissions
├─ Implement AppleHealthKitProvider
├─ Request user authorization
└─ Test permission flow

Day 3-4: Data Sync (Read)
├─ Fetch steps, workouts, calories
├─ Fetch sleep data
├─ Fetch heart rate
├─ Sync to backend
└─ Test data sync

Day 5: Data Sync (Write)
├─ Write logged meals to HealthKit
├─ Write workouts to HealthKit
├─ Write water intake to HealthKit
└─ Test write operations

Day 6: Conflict Resolution
├─ Implement merge logic
├─ Handle duplicate data
├─ Prompt user for conflicts
└─ Test conflict resolution

Day 7: Background Sync
├─ Set up iOS Background Fetch
├─ Schedule periodic sync (every 15 min)
├─ Handle sync failures
└─ Test background sync

Deliverables:
✅ HealthKit authorization flow
✅ Read steps, workouts, sleep, heart rate
✅ Write meals, workouts, water to HealthKit
✅ Conflict resolution logic
✅ Background sync (every 15 min)
```

---

### Phase 4: Apple Watch (Week 7)

```
┌─────────────────────────────────────────────────────────────────────┐
│              PHASE 4: APPLE WATCH INTEGRATION                       │
│                     Duration: 3-4 days (parallel with HealthKit)    │
└─────────────────────────────────────────────────────────────────────┘

Day 1-2: WatchConnectivity
├─ Add watch_connectivity package
├─ Implement AppleWatchProvider
├─ Send notifications to watch
├─ Test watch notifications

Day 3: Watch Complications (Optional)
├─ Create basic watchOS app
├─ Add complications (calorie ring, streak)
├─ Update complications from iPhone
└─ Test complications

Day 4: Quick Actions
├─ Add "Log Water" action on watch
├─ Add "Start Workout" action on watch
└─ Test quick actions

Deliverables:
✅ Watch notifications with haptic feedback
✅ Watch complications (calorie ring, streak)
✅ Quick actions (log water, start workout)
```

---

### Phase 5: Fitbit Integration (Week 8)

```
┌─────────────────────────────────────────────────────────────────────┐
│               PHASE 5: FITBIT INTEGRATION                           │
│                     Duration: 1 week                                │
└─────────────────────────────────────────────────────────────────────┘

Day 1-2: Fitbit OAuth
├─ Register app on Fitbit Developer Portal
├─ Add fitbitter package
├─ Implement OAuth flow
├─ Store access token securely
└─ Test OAuth flow

Day 3-4: Data Sync
├─ Fetch steps, heart rate, activity
├─ Fetch sleep data
├─ Sync to backend
└─ Test data sync

Day 5: Background Sync
├─ Schedule periodic sync (every 15 min)
├─ Handle token refresh
├─ Handle sync failures
└─ Test background sync

Day 6-7: Conflict Resolution
├─ Implement merge logic (Fitbit + HealthKit)
├─ Handle duplicate data
├─ Prompt user for conflicts
└─ Test conflict resolution

Deliverables:
✅ Fitbit OAuth flow
✅ Read steps, heart rate, activity, sleep
✅ Background sync (every 15 min)
✅ Conflict resolution with HealthKit
```

---

## 5️⃣ USER CONTROLS & SETTINGS

### 5.1 Notification Settings Screen

```dart
// lib/screens/settings/notification_settings_screen.dart

class NotificationSettingsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Notification Settings')),
      body: ListView(
        children: [
          // Enable/Disable by Type
          _buildSection(
            title: 'Notification Types',
            children: [
              _buildToggle('Meal Reminders', NotificationType.reminder),
              _buildToggle('Achievements', NotificationType.achievement),
              _buildToggle('AI Insights', NotificationType.insight),
              _buildToggle('Critical Alerts', NotificationType.alert),
              _buildToggle('Social', NotificationType.social),
            ],
          ),
          
          // DND Windows
          _buildSection(
            title: 'Do Not Disturb',
            children: [
              _buildDNDWindow('Nighttime', TimeOfDay(hour: 22, minute: 0), TimeOfDay(hour: 8, minute: 0)),
              _buildAddDNDButton(),
            ],
          ),
          
          // Frequency Limits
          _buildSection(
            title: 'Frequency Limits',
            children: [
              _buildFrequencySlider('Reminders', NotificationType.reminder, max: 10),
              _buildFrequencySlider('Achievements', NotificationType.achievement, max: 20),
              _buildFrequencySlider('Insights', NotificationType.insight, max: 5),
            ],
          ),
          
          // Channels
          _buildSection(
            title: 'Notification Channels',
            children: [
              _buildToggle('Push Notifications', null),
              _buildToggle('In-App Banners', null),
              _buildToggle('Apple Watch', null),
              _buildToggle('Email', null),
            ],
          ),
        ],
      ),
    );
  }
}
```

---

### 5.2 Device Integration Settings

```dart
// lib/screens/settings/device_integration_screen.dart

class DeviceIntegrationScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Device Integrations')),
      body: ListView(
        children: [
          // Apple Health
          _buildIntegrationCard(
            icon: Icons.favorite,
            title: 'Apple Health',
            subtitle: 'Sync steps, workouts, sleep, heart rate',
            connected: true,
            onTap: () => _showHealthKitSettings(context),
          ),
          
          // Apple Watch
          _buildIntegrationCard(
            icon: Icons.watch,
            title: 'Apple Watch',
            subtitle: 'Receive notifications and quick actions',
            connected: true,
            onTap: () => _showWatchSettings(context),
          ),
          
          // Fitbit
          _buildIntegrationCard(
            icon: Icons.fitness_center,
            title: 'Fitbit',
            subtitle: 'Sync activity, heart rate, sleep',
            connected: false,
            onTap: () => _connectFitbit(context),
          ),
          
          // Google Fit
          _buildIntegrationCard(
            icon: Icons.directions_run,
            title: 'Google Fit',
            subtitle: 'Sync workouts and activity',
            connected: false,
            onTap: () => _connectGoogleFit(context),
          ),
          
          // Garmin
          _buildIntegrationCard(
            icon: Icons.sports_score,
            title: 'Garmin Connect',
            subtitle: 'Sync workouts and activities',
            connected: false,
            onTap: () => _connectGarmin(context),
          ),
        ],
      ),
    );
  }
}
```

---

## 6️⃣ TESTING & QA

### 6.1 Test Scenarios

#### Local Push Notifications
- [ ] Immediate notification appears
- [ ] Scheduled notification appears at correct time
- [ ] Notification tap opens correct screen
- [ ] Notification sound/vibration works
- [ ] Badge count updates correctly
- [ ] Notification can be dismissed
- [ ] Notification can be snoozed

#### In-App Notifications
- [ ] Banner appears at top of screen
- [ ] Banner auto-dismisses after 3 seconds
- [ ] Banner can be manually dismissed
- [ ] Banner tap opens correct screen
- [ ] Multiple banners queue correctly

#### Apple HealthKit
- [ ] Permission request appears
- [ ] Steps sync correctly
- [ ] Workouts sync correctly
- [ ] Sleep data syncs correctly
- [ ] Heart rate syncs correctly
- [ ] Write operations work (meals, water)
- [ ] Background sync works (every 15 min)
- [ ] Conflict resolution works

#### Apple Watch
- [ ] Notifications appear on watch
- [ ] Haptic feedback works
- [ ] Complications update correctly
- [ ] Quick actions work (log water)
- [ ] Watch app opens from complication

#### Fitbit
- [ ] OAuth flow works
- [ ] Steps sync correctly
- [ ] Heart rate syncs correctly
- [ ] Sleep data syncs correctly
- [ ] Background sync works (every 15 min)
- [ ] Token refresh works
- [ ] Conflict resolution works (Fitbit + HealthKit)

#### User Preferences
- [ ] Enable/disable toggles work
- [ ] DND windows respected
- [ ] Frequency limits enforced
- [ ] Preferences persist across app restarts

---

### 6.2 Edge Cases

- [ ] User revokes HealthKit permission mid-session
- [ ] Device offline during sync
- [ ] Fitbit token expires
- [ ] Conflicting data from multiple sources
- [ ] User logs same meal in app and HealthKit
- [ ] Background sync fails (retry logic)
- [ ] Notification queue overflow (>100 pending)
- [ ] User in DND window for 24+ hours
- [ ] Frequency limit reached (queue for tomorrow)

---

## 7️⃣ ANALYTICS & MONITORING

### 7.1 Notification Metrics

```dart
class NotificationAnalytics {
  Future<void> trackNotificationSent(NotificationPayload payload) async {
    await analytics.logEvent(
      name: 'notification_sent',
      parameters: {
        'type': payload.type.toString(),
        'priority': payload.priority.toString(),
        'channel': 'local_push', // or 'in_app', 'watch'
      },
    );
  }
  
  Future<void> trackNotificationOpened(String notificationId) async {
    await analytics.logEvent(
      name: 'notification_opened',
      parameters: {'notification_id': notificationId},
    );
  }
  
  Future<void> trackNotificationDismissed(String notificationId) async {
    await analytics.logEvent(
      name: 'notification_dismissed',
      parameters: {'notification_id': notificationId},
    );
  }
  
  Future<void> trackNotificationActionTaken(String notificationId, String action) async {
    await analytics.logEvent(
      name: 'notification_action',
      parameters: {
        'notification_id': notificationId,
        'action': action,
      },
    );
  }
}
```

---

### 7.2 Device Sync Metrics

```dart
class DeviceSyncAnalytics {
  Future<void> trackSyncStarted(String device) async {
    await analytics.logEvent(
      name: 'device_sync_started',
      parameters: {'device': device},
    );
  }
  
  Future<void> trackSyncCompleted(String device, int recordsSynced, Duration duration) async {
    await analytics.logEvent(
      name: 'device_sync_completed',
      parameters: {
        'device': device,
        'records_synced': recordsSynced,
        'duration_ms': duration.inMilliseconds,
      },
    );
  }
  
  Future<void> trackSyncFailed(String device, String error) async {
    await analytics.logEvent(
      name: 'device_sync_failed',
      parameters: {
        'device': device,
        'error': error,
      },
    );
  }
}
```

---

## 8️⃣ FUTURE ENHANCEMENTS

### 8.1 Adaptive Coaching

```dart
class AdaptiveNotificationAgent extends NotificationAgent {
  // Learn from user behavior
  // Adjust frequency based on engagement
  // Optimize timing based on open rates
  
  Future<void> optimizeFrequency(NotificationType type) async {
    final openRate = await analytics.getOpenRate(type);
    
    if (openRate < 0.2) {
      // Low engagement - reduce frequency
      await preferences.setFrequencyLimit(type, preferences.getFrequencyLimit(type) - 1);
    } else if (openRate > 0.8) {
      // High engagement - can increase frequency
      await preferences.setFrequencyLimit(type, preferences.getFrequencyLimit(type) + 1);
    }
  }
  
  Future<TimeOfDay> optimizeTiming(NotificationType type) async {
    // Analyze when user typically opens notifications
    // Adjust scheduling to match user's active hours
    final bestTime = await analytics.getBestTimeForNotification(type);
    return bestTime;
  }
}
```

---

### 8.2 Group Notifications

```dart
class GroupedNotificationProvider implements NotificationProvider {
  // Group similar notifications to prevent overload
  // Example: "You have 3 new achievements" instead of 3 separate notifications
  
  Future<void> groupAndSend(List<NotificationPayload> payloads) async {
    final grouped = _groupByType(payloads);
    
    for (var entry in grouped.entries) {
      final type = entry.key;
      final notifications = entry.value;
      
      if (notifications.length > 1) {
        // Send grouped notification
        await send(NotificationPayload(
          id: 'grouped_${type}_${DateTime.now().millisecondsSinceEpoch}',
          type: type,
          title: _getGroupedTitle(type, notifications.length),
          body: _getGroupedBody(type, notifications),
          priority: NotificationPriority.medium,
        ));
      } else {
        // Send individual notification
        await send(notifications.first);
      }
    }
  }
}
```

---

### 8.3 Social Notifications

```dart
// Future: Friend challenges, group goals, coach comments

class SocialNotificationProvider implements NotificationProvider {
  Future<void> notifyFriendChallenge(String friendName, String challengeName) async {
    await send(NotificationPayload(
      id: 'friend_challenge_${DateTime.now().millisecondsSinceEpoch}',
      type: NotificationType.social,
      title: '$friendName challenged you!',
      body: 'Join the "$challengeName" challenge',
      priority: NotificationPriority.medium,
      action: 'view_challenge',
    ));
  }
  
  Future<void> notifyCoachComment(String coachName, String comment) async {
    await send(NotificationPayload(
      id: 'coach_comment_${DateTime.now().millisecondsSinceEpoch}',
      type: NotificationType.social,
      title: '$coachName replied',
      body: comment,
      priority: NotificationPriority.low,
      action: 'view_comment',
    ));
  }
}
```

---

### 8.4 Smart Speaker / IoT Integration

```dart
// Future: Alexa, Google Home, smart displays

class SmartSpeakerProvider implements NotificationProvider {
  Future<void> sendToAlexa(NotificationPayload payload) async {
    // Use Alexa Notifications API
    // "Alexa, tell me my daily progress"
  }
  
  Future<void> sendToGoogleHome(NotificationPayload payload) async {
    // Use Google Assistant API
    // "Hey Google, what's my calorie goal today?"
  }
}
```

---

## 9️⃣ SECURITY & PRIVACY

### 9.1 Data Encryption

```dart
class SecureDeviceTokenStorage {
  final FlutterSecureStorage storage = FlutterSecureStorage();
  
  Future<void> storeToken(String device, String token) async {
    await storage.write(
      key: '${device}_token',
      value: token,
      iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
      aOptions: AndroidOptions(encryptedSharedPreferences: true),
    );
  }
  
  Future<String?> getToken(String device) async {
    return await storage.read(key: '${device}_token');
  }
  
  Future<void> deleteToken(String device) async {
    await storage.delete(key: '${device}_token');
  }
}
```

---

### 9.2 User Consent

```dart
class DeviceConsentFlow {
  Future<bool> requestHealthKitConsent(BuildContext context) async {
    // Show consent dialog
    final consent = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Connect Apple Health'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('We will read:'),
            Text('• Steps'),
            Text('• Workouts'),
            Text('• Sleep'),
            Text('• Heart Rate'),
            SizedBox(height: 16),
            Text('We will write:'),
            Text('• Logged meals'),
            Text('• Workouts'),
            Text('• Water intake'),
            SizedBox(height: 16),
            Text('Your data is encrypted and never shared.'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text('Connect'),
          ),
        ],
      ),
    );
    
    if (consent == true) {
      // Request HealthKit permissions
      return await AppleHealthKitProvider().requestPermissions();
    }
    
    return false;
  }
}
```

---

## 🎯 SUCCESS CRITERIA

### Phase 1 (Week 3) - Notifications Foundation
- ✅ Local push notifications working (immediate & scheduled)
- ✅ In-app banners working
- ✅ Notification agent with decision logic
- ✅ User preferences UI (enable/disable, DND, frequency)
- ✅ 5 notification types supported (reminder, achievement, insight, alert, social)

### Phase 2 (Week 4) - Scheduled Reminders
- ✅ Meal reminders (breakfast, lunch, dinner)
- ✅ Water reminders (every 2 hours)
- ✅ Workout reminders (daily)
- ✅ Streak reminders (if at risk)
- ✅ Custom user-defined reminders

### Phase 3 (Week 7) - Apple HealthKit
- ✅ HealthKit authorization flow
- ✅ Read steps, workouts, sleep, heart rate
- ✅ Write meals, workouts, water to HealthKit
- ✅ Conflict resolution logic
- ✅ Background sync (every 15 min)

### Phase 4 (Week 7) - Apple Watch
- ✅ Watch notifications with haptic feedback
- ✅ Watch complications (calorie ring, streak)
- ✅ Quick actions (log water, start workout)

### Phase 5 (Week 8) - Fitbit
- ✅ Fitbit OAuth flow
- ✅ Read steps, heart rate, activity, sleep
- ✅ Background sync (every 15 min)
- ✅ Conflict resolution with HealthKit

---

**End of Plan**

