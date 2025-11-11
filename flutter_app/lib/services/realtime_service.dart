import 'dart:async';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart';
import '../models/timeline_activity.dart';
import '../models/fitness_log.dart';

/// Real-Time Firestore Snapshot Service
/// 
/// Provides real-time updates for Timeline and Dashboard using Firestore onSnapshot.
/// This replaces polling with push-based updates for instant synchronization.
/// 
/// Features:
/// - Real-time timeline updates
/// - Connection state management
/// - Automatic reconnection
/// - Graceful degradation (falls back to polling if disabled)
/// - Feature flag controlled (REALTIME_ENABLED)
class RealtimeService {
  static final RealtimeService _instance = RealtimeService._internal();
  factory RealtimeService() => _instance;
  RealtimeService._internal();

  // Feature flag (can be controlled via remote config)
  static bool _enabled = false;
  static bool get isEnabled => _enabled;
  static set enabled(bool value) => _enabled = value;

  // Firestore instance
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  // Active listeners
  final Map<String, StreamSubscription> _listeners = {};

  // Connection state
  ConnectionState _connectionState = ConnectionState.disconnected;
  ConnectionState get connectionState => _connectionState;

  // Stream controllers for broadcasting updates
  final _timelineController = StreamController<List<TimelineActivity>>.broadcast();
  final _connectionStateController = StreamController<ConnectionState>.broadcast();

  /// Stream of timeline updates
  Stream<List<TimelineActivity>> get timelineStream => _timelineController.stream;

  /// Stream of connection state changes
  Stream<ConnectionState> get connectionStateStream => _connectionStateController.stream;

  /// Initialize real-time service
  void initialize({bool enabled = false}) {
    _enabled = enabled;
    
    if (_enabled) {
      print('🔴 Real-time service ENABLED');
      _updateConnectionState(ConnectionState.connecting);
    } else {
      print('⚪ Real-time service DISABLED (using polling)');
    }
  }

  /// Listen to timeline updates for a user
  /// 
  /// This creates a Firestore onSnapshot listener that pushes updates
  /// whenever fitness logs or tasks change.
  void listenToTimeline({
    required String userId,
    required Function(List<TimelineActivity>) onUpdate,
    Function(String)? onError,
  }) {
    if (!_enabled) {
      print('⚪ Real-time disabled, skipping timeline listener');
      return;
    }

    // Cancel existing listener if any
    _listeners['timeline_$userId']?.cancel();

    print('🔴 Starting real-time timeline listener for user: $userId');

    // Listen to fitness_logs collection
    final fitnessLogsQuery = _firestore
        .collection('users')
        .doc(userId)
        .collection('fitness_logs')
        .orderBy('timestamp', descending: true)
        .limit(100); // Limit to recent 100 activities

    _listeners['timeline_$userId'] = fitnessLogsQuery.snapshots().listen(
      (snapshot) {
        try {
          _updateConnectionState(ConnectionState.connected);

          // Convert Firestore documents to TimelineActivity
          final activities = <TimelineActivity>[];

          for (var doc in snapshot.docs) {
            try {
              final data = doc.data();
              final activity = _fitnessLogToActivity(doc.id, data);
              if (activity != null) {
                activities.add(activity);
              }
            } catch (e) {
              print('⚠️  Error parsing fitness log: $e');
            }
          }

          print('🔴 Real-time update: ${activities.length} activities');

          // Broadcast update
          _timelineController.add(activities);
          onUpdate(activities);
        } catch (e) {
          print('❌ Error processing timeline snapshot: $e');
          if (onError != null) {
            onError(e.toString());
          }
        }
      },
      onError: (error) {
        print('❌ Timeline listener error: $error');
        _updateConnectionState(ConnectionState.error);
        if (onError != null) {
          onError(error.toString());
        }
      },
      cancelOnError: false, // Keep listening even after errors
    );
  }

  /// Stop listening to timeline updates
  void stopListeningToTimeline(String userId) {
    _listeners['timeline_$userId']?.cancel();
    _listeners.remove('timeline_$userId');
    print('🔴 Stopped timeline listener for user: $userId');
  }

  /// Listen to dashboard updates for a user
  /// 
  /// This creates a Firestore onSnapshot listener for today's fitness logs
  /// to update dashboard stats in real-time.
  void listenToDashboard({
    required String userId,
    required Function(Map<String, dynamic>) onUpdate,
    Function(String)? onError,
  }) {
    if (!_enabled) {
      print('⚪ Real-time disabled, skipping dashboard listener');
      return;
    }

    // Cancel existing listener if any
    _listeners['dashboard_$userId']?.cancel();

    print('🔴 Starting real-time dashboard listener for user: $userId');

    // Get today's date range (local time)
    final now = DateTime.now();
    final startOfDay = DateTime(now.year, now.month, now.day);
    final endOfDay = startOfDay.add(const Duration(days: 1));

    // Listen to today's fitness logs
    final dashboardQuery = _firestore
        .collection('users')
        .doc(userId)
        .collection('fitness_logs')
        .where('timestamp', isGreaterThanOrEqualTo: Timestamp.fromDate(startOfDay.toUtc()))
        .where('timestamp', isLessThan: Timestamp.fromDate(endOfDay.toUtc()));

    _listeners['dashboard_$userId'] = dashboardQuery.snapshots().listen(
      (snapshot) {
        try {
          _updateConnectionState(ConnectionState.connected);

          // Calculate dashboard stats
          int totalCalories = 0;
          double totalProtein = 0;
          double totalCarbs = 0;
          double totalFat = 0;
          int waterMl = 0;
          int workouts = 0;

          for (var doc in snapshot.docs) {
            try {
              final data = doc.data();
              final logType = data['log_type'] as String?;
              final calories = data['calories'] as int? ?? 0;
              final parsedData = data['ai_parsed_data'] as Map<String, dynamic>?;

              if (logType == 'meal') {
                totalCalories += calories;
                totalProtein += (parsedData?['protein_g'] as num?)?.toDouble() ?? 0;
                totalCarbs += (parsedData?['carbs_g'] as num?)?.toDouble() ?? 0;
                totalFat += (parsedData?['fat_g'] as num?)?.toDouble() ?? 0;
              } else if (logType == 'water') {
                waterMl += (parsedData?['quantity_ml'] as int?) ?? 0;
              } else if (logType == 'workout') {
                workouts++;
              }
            } catch (e) {
              print('⚠️  Error parsing fitness log for dashboard: $e');
            }
          }

          final stats = {
            'calories': totalCalories,
            'protein_g': totalProtein,
            'carbs_g': totalCarbs,
            'fat_g': totalFat,
            'water_ml': waterMl,
            'workouts': workouts,
            'updated_at': DateTime.now().toIso8601String(),
          };

          print('🔴 Real-time dashboard update: $totalCalories cal, ${totalProtein.toStringAsFixed(1)}g protein');

          onUpdate(stats);
        } catch (e) {
          print('❌ Error processing dashboard snapshot: $e');
          if (onError != null) {
            onError(e.toString());
          }
        }
      },
      onError: (error) {
        print('❌ Dashboard listener error: $error');
        _updateConnectionState(ConnectionState.error);
        if (onError != null) {
          onError(error.toString());
        }
      },
      cancelOnError: false,
    );
  }

  /// Stop listening to dashboard updates
  void stopListeningToDashboard(String userId) {
    _listeners['dashboard_$userId']?.cancel();
    _listeners.remove('dashboard_$userId');
    print('🔴 Stopped dashboard listener for user: $userId');
  }

  /// Stop all listeners
  void stopAll() {
    for (var listener in _listeners.values) {
      listener.cancel();
    }
    _listeners.clear();
    print('🔴 Stopped all real-time listeners');
  }

  /// Update connection state and broadcast
  void _updateConnectionState(ConnectionState newState) {
    if (_connectionState != newState) {
      _connectionState = newState;
      _connectionStateController.add(newState);
      print('🔴 Connection state: ${newState.name}');
    }
  }

  /// Convert Firestore fitness log to TimelineActivity
  TimelineActivity? _fitnessLogToActivity(String id, Map<String, dynamic> data) {
    try {
      final logType = data['log_type'] as String?;
      final content = data['content'] as String? ?? '';
      final timestamp = (data['timestamp'] as Timestamp?)?.toDate() ?? DateTime.now();
      final calories = data['calories'] as int? ?? 0;
      final parsedData = data['ai_parsed_data'] as Map<String, dynamic>? ?? {};

      // Determine icon and color based on log type
      String icon = '📝';
      String color = '#6366F1';
      String status = 'completed';

      switch (logType) {
        case 'meal':
          icon = '🍽️';
          color = '#34C759';
          status = '$calories kcal';
          break;
        case 'workout':
          icon = '💪';
          color = '#FF6B6B';
          status = '$calories kcal burned';
          break;
        case 'water':
          icon = '💧';
          color = '#00B4D8';
          final ml = parsedData['quantity_ml'] as int? ?? 0;
          status = '${ml}ml';
          break;
        case 'supplement':
          icon = '💊';
          color = '#9C27B0';
          status = parsedData['dosage'] as String? ?? 'taken';
          break;
        default:
          return null;
      }

      return TimelineActivity(
        id: id,
        type: logType ?? 'other',
        title: content,
        timestamp: timestamp,
        icon: icon,
        color: color,
        status: status,
        details: parsedData,
      );
    } catch (e) {
      print('⚠️  Error converting fitness log to activity: $e');
      return null;
    }
  }

  /// Dispose and clean up
  void dispose() {
    stopAll();
    _timelineController.close();
    _connectionStateController.close();
  }
}

/// Connection state enum
enum ConnectionState {
  disconnected,
  connecting,
  connected,
  error,
}

