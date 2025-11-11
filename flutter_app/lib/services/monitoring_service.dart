import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:firebase_performance/firebase_performance.dart';
import 'package:firebase_crashlytics/firebase_crashlytics.dart';
import 'package:sentry_flutter/sentry_flutter.dart';
import '../utils/feature_flags.dart';

/// Production Monitoring Service
/// 
/// Provides comprehensive monitoring and error tracking:
/// - Firebase Performance Monitoring (traces, metrics)
/// - Firebase Crashlytics (crash reporting)
/// - Sentry (error tracking, breadcrumbs)
/// - Custom metrics and events
/// 
/// Feature flag controlled for safe rollout.
class MonitoringService {
  static final MonitoringService _instance = MonitoringService._internal();
  factory MonitoringService() => _instance;
  MonitoringService._internal();

  // Firebase Performance
  FirebasePerformance? _performance;
  
  // Active traces
  final Map<String, Trace> _activeTraces = {};

  /// Initialize monitoring services
  Future<void> initialize() async {
    // Initialize Firebase Performance
    if (FeatureFlags.performanceMonitoringEnabled) {
      try {
        _performance = FirebasePerformance.instance;
        await _performance!.setPerformanceCollectionEnabled(true);
        print('✅ Firebase Performance Monitoring initialized');
      } catch (e) {
        print('⚠️  Firebase Performance initialization failed: $e');
      }
    } else {
      print('⚪ Firebase Performance Monitoring disabled');
    }

    // Initialize Firebase Crashlytics
    try {
      // Enable Crashlytics collection
      await FirebaseCrashlytics.instance.setCrashlyticsCollectionEnabled(true);
      
      // Pass all uncaught errors to Crashlytics
      FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterError;
      
      // Pass all uncaught asynchronous errors to Crashlytics
      PlatformDispatcher.instance.onError = (error, stack) {
        FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
        return true;
      };
      
      print('✅ Firebase Crashlytics initialized');
    } catch (e) {
      print('⚠️  Firebase Crashlytics initialization failed: $e');
    }

    // Initialize Sentry
    if (FeatureFlags.sentryEnabled) {
      // Sentry is initialized in main.dart via SentryFlutter.init()
      print('✅ Sentry initialized');
    } else {
      print('⚪ Sentry disabled');
    }
  }

  // ========== PERFORMANCE TRACES ==========

  /// Start a custom trace
  /// 
  /// Example:
  /// ```dart
  /// await monitoring.startTrace('timeline_load');
  /// // ... do work ...
  /// await monitoring.stopTrace('timeline_load');
  /// ```
  Future<void> startTrace(String traceName) async {
    if (!FeatureFlags.performanceMonitoringEnabled || _performance == null) {
      return;
    }

    try {
      if (_activeTraces.containsKey(traceName)) {
        print('⚠️  Trace "$traceName" already active, stopping old one');
        await stopTrace(traceName);
      }

      final trace = _performance!.newTrace(traceName);
      await trace.start();
      _activeTraces[traceName] = trace;
      print('📊 Started trace: $traceName');
    } catch (e) {
      print('⚠️  Error starting trace "$traceName": $e');
    }
  }

  /// Stop a custom trace
  Future<void> stopTrace(String traceName) async {
    if (!FeatureFlags.performanceMonitoringEnabled || _performance == null) {
      return;
    }

    try {
      final trace = _activeTraces.remove(traceName);
      if (trace != null) {
        await trace.stop();
        print('📊 Stopped trace: $traceName');
      } else {
        print('⚠️  Trace "$traceName" not found');
      }
    } catch (e) {
      print('⚠️  Error stopping trace "$traceName": $e');
    }
  }

  /// Add metric to active trace
  Future<void> addTraceMetric(String traceName, String metricName, int value) async {
    if (!FeatureFlags.performanceMonitoringEnabled || _performance == null) {
      return;
    }

    try {
      final trace = _activeTraces[traceName];
      if (trace != null) {
        trace.setMetric(metricName, value);
        print('📊 Added metric to trace "$traceName": $metricName = $value');
      } else {
        print('⚠️  Trace "$traceName" not found');
      }
    } catch (e) {
      print('⚠️  Error adding metric to trace "$traceName": $e');
    }
  }

  /// Add attribute to active trace
  Future<void> addTraceAttribute(String traceName, String attributeName, String value) async {
    if (!FeatureFlags.performanceMonitoringEnabled || _performance == null) {
      return;
    }

    try {
      final trace = _activeTraces[traceName];
      if (trace != null) {
        trace.putAttribute(attributeName, value);
        print('📊 Added attribute to trace "$traceName": $attributeName = $value');
      } else {
        print('⚠️  Trace "$traceName" not found');
      }
    } catch (e) {
      print('⚠️  Error adding attribute to trace "$traceName": $e');
    }
  }

  // ========== HTTP METRICS ==========

  /// Create HTTP metric for API calls
  /// 
  /// Example:
  /// ```dart
  /// final metric = monitoring.createHttpMetric('/api/timeline', HttpMethod.Get);
  /// await metric.start();
  /// // ... make API call ...
  /// metric.httpResponseCode = 200;
  /// metric.responsePayloadSize = 1024;
  /// await metric.stop();
  /// ```
  HttpMetric? createHttpMetric(String url, HttpMethod method) {
    if (!FeatureFlags.performanceMonitoringEnabled || _performance == null) {
      return null;
    }

    try {
      return _performance!.newHttpMetric(url, method);
    } catch (e) {
      print('⚠️  Error creating HTTP metric: $e');
      return null;
    }
  }

  // ========== ERROR TRACKING ==========

  /// Log error to Crashlytics and Sentry
  Future<void> logError(
    dynamic error,
    StackTrace? stackTrace, {
    String? reason,
    Map<String, dynamic>? context,
    bool fatal = false,
  }) async {
    // Log to console
    print('❌ Error: $error');
    if (stackTrace != null) {
      print('   Stack: $stackTrace');
    }
    if (reason != null) {
      print('   Reason: $reason');
    }

    // Log to Crashlytics
    try {
      await FirebaseCrashlytics.instance.recordError(
        error,
        stackTrace,
        reason: reason,
        fatal: fatal,
      );
    } catch (e) {
      print('⚠️  Failed to log error to Crashlytics: $e');
    }

    // Log to Sentry
    if (FeatureFlags.sentryEnabled) {
      try {
        await Sentry.captureException(
          error,
          stackTrace: stackTrace,
          hint: Hint.withMap({
            'reason': reason,
            ...?context,
          }),
        );
      } catch (e) {
        print('⚠️  Failed to log error to Sentry: $e');
      }
    }
  }

  /// Log message to Crashlytics
  Future<void> logMessage(String message) async {
    try {
      await FirebaseCrashlytics.instance.log(message);
      print('📝 Logged message: $message');
    } catch (e) {
      print('⚠️  Failed to log message: $e');
    }
  }

  /// Add breadcrumb to Sentry
  Future<void> addBreadcrumb(
    String message, {
    String? category,
    Map<String, dynamic>? data,
    SentryLevel level = SentryLevel.info,
  }) async {
    if (!FeatureFlags.sentryEnabled) {
      return;
    }

    try {
      await Sentry.addBreadcrumb(
        Breadcrumb(
          message: message,
          category: category,
          data: data,
          level: level,
          timestamp: DateTime.now(),
        ),
      );
      print('🍞 Added breadcrumb: $message');
    } catch (e) {
      print('⚠️  Failed to add breadcrumb: $e');
    }
  }

  // ========== USER CONTEXT ==========

  /// Set user context for error tracking
  Future<void> setUserContext({
    required String userId,
    String? email,
    String? username,
    Map<String, dynamic>? extras,
  }) async {
    // Set user for Crashlytics
    try {
      await FirebaseCrashlytics.instance.setUserIdentifier(userId);
      print('👤 Set user context: $userId');
    } catch (e) {
      print('⚠️  Failed to set user context in Crashlytics: $e');
    }

    // Set user for Sentry
    if (FeatureFlags.sentryEnabled) {
      try {
        await Sentry.configureScope((scope) {
          scope.setUser(SentryUser(
            id: userId,
            email: email,
            username: username,
            data: extras,
          ));
        });
      } catch (e) {
        print('⚠️  Failed to set user context in Sentry: $e');
      }
    }
  }

  /// Clear user context (on logout)
  Future<void> clearUserContext() async {
    try {
      await FirebaseCrashlytics.instance.setUserIdentifier('');
      print('👤 Cleared user context');
    } catch (e) {
      print('⚠️  Failed to clear user context in Crashlytics: $e');
    }

    if (FeatureFlags.sentryEnabled) {
      try {
        await Sentry.configureScope((scope) {
          scope.setUser(null);
        });
      } catch (e) {
        print('⚠️  Failed to clear user context in Sentry: $e');
      }
    }
  }

  // ========== CUSTOM EVENTS ==========

  /// Log custom event
  Future<void> logEvent(
    String eventName, {
    Map<String, dynamic>? parameters,
  }) async {
    if (!FeatureFlags.customAnalyticsEnabled) {
      return;
    }

    print('📊 Event: $eventName ${parameters ?? ''}');

    // Add as breadcrumb to Sentry
    if (FeatureFlags.sentryEnabled) {
      await addBreadcrumb(
        eventName,
        category: 'custom_event',
        data: parameters,
        level: SentryLevel.info,
      );
    }
  }

  // ========== SCREEN TRACKING ==========

  /// Track screen view
  Future<void> trackScreenView(String screenName) async {
    if (!FeatureFlags.customAnalyticsEnabled) {
      return;
    }

    print('📱 Screen: $screenName');

    // Add as breadcrumb to Sentry
    if (FeatureFlags.sentryEnabled) {
      await addBreadcrumb(
        'Screen: $screenName',
        category: 'navigation',
        level: SentryLevel.info,
      );
    }
  }

  // ========== UTILITIES ==========

  /// Test crash reporting (for testing only!)
  Future<void> testCrash() async {
    print('💥 Testing crash reporting...');
    throw Exception('Test crash from MonitoringService');
  }

  /// Get monitoring stats
  Map<String, dynamic> getStats() {
    return {
      'performance_enabled': FeatureFlags.performanceMonitoringEnabled,
      'sentry_enabled': FeatureFlags.sentryEnabled,
      'custom_analytics_enabled': FeatureFlags.customAnalyticsEnabled,
      'active_traces': _activeTraces.keys.toList(),
    };
  }
}

/// Global singleton instance
final monitoring = MonitoringService();

