import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';

import '../utils/constants.dart';
import '../services/api_service.dart';
import '../services/realtime_service.dart'; // 🔴 PHASE 1: Real-time support
import '../utils/feature_flags.dart'; // 🚩 Feature flag control
import 'auth_provider.dart';

/// Daily nutrition and fitness statistics
class DailyStats {
  final int caloriesConsumed;
  final int caloriesBurned;
  final int caloriesGoal;
  final double proteinG;
  final double proteinGoal;
  final double carbsG;
  final double carbsGoal;
  final double fatG;
  final double fatGoal;
  final double fiberG;
  final double fiberGoal;
  final int waterMl;
  final int waterGoal;
  final int workoutsCompleted;
  final int workoutsGoal;
  final List<ActivityItem> activities;

  DailyStats({
    this.caloriesConsumed = 0,
    this.caloriesBurned = 0,
    this.caloriesGoal = 2000,
    this.proteinG = 0,
    this.proteinGoal = 150,
    this.carbsG = 0,
    this.carbsGoal = 200,
    this.fatG = 0,
    this.fatGoal = 65,
    this.fiberG = 0,
    this.fiberGoal = 25,
    this.waterMl = 0,
    this.waterGoal = 2000,
    this.workoutsCompleted = 0,
    this.workoutsGoal = 1,
    this.activities = const [],
  });

  double get caloriesProgress => caloriesGoal > 0 ? (caloriesConsumed / caloriesGoal).clamp(0.0, 1.0) : 0.0;
  double get proteinProgress => proteinGoal > 0 ? (proteinG / proteinGoal).clamp(0.0, 1.0) : 0.0;
  double get carbsProgress => carbsGoal > 0 ? (carbsG / carbsGoal).clamp(0.0, 1.0) : 0.0;
  double get fatProgress => fatGoal > 0 ? (fatG / fatGoal).clamp(0.0, 1.0) : 0.0;
  double get fiberProgress => fiberGoal > 0 ? (fiberG / fiberGoal).clamp(0.0, 1.0) : 0.0;
  double get waterProgress => waterGoal > 0 ? (waterMl / waterGoal).clamp(0.0, 1.0) : 0.0;
  double get workoutsProgress => workoutsGoal > 0 ? (workoutsCompleted / workoutsGoal).clamp(0.0, 1.0) : 0.0;

  int get caloriesRemaining => caloriesGoal - caloriesConsumed;
  double get proteinRemaining => proteinGoal - proteinG;
  double get carbsRemaining => carbsGoal - carbsG;
  double get fatRemaining => fatGoal - fatG;
  
  // Net calories (consumed - burned)
  int get netCalories => caloriesConsumed - caloriesBurned;
  
  // Calorie deficit (negative = deficit, positive = surplus)
  int get calorieDeficit => netCalories - caloriesGoal;
  
  // Is user in deficit?
  bool get isInDeficit => netCalories < caloriesGoal;
}

/// Activity item for timeline
class ActivityItem {
  final String id;
  final String type; // 'meal', 'workout', 'water', 'task'
  final String title;
  final String? subtitle;
  final DateTime timestamp;
  final Map<String, dynamic>? data;

  ActivityItem({
    required this.id,
    required this.type,
    required this.title,
    this.subtitle,
    required this.timestamp,
    this.data,
  });

  String get emoji {
    switch (type) {
      case 'meal':
        return '🍽️';
      case 'workout':
        return '💪';
      case 'water':
        return '💧';
      case 'task':
        return '✅';
      default:
        return '📝';
    }
  }
}

class DashboardProvider extends ChangeNotifier {
  final RealtimeService _realtimeService = RealtimeService(); // 🔴 Real-time service
  
  DailyStats _stats = DailyStats();
  bool _isLoading = false;
  String? _errorMessage;
  DateTime _selectedDate = DateTime.now();
  
  // 🚀 HYBRID OPTIMIZATION: Client-side cache
  DailyStats? _cachedStats;
  DateTime? _cacheTimestamp;
  DateTime? _cacheDate; // Date for which stats are cached
  static const Duration _cacheDuration = Duration(minutes: 5);

  DailyStats get stats => _stats;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  DateTime get selectedDate => _selectedDate;
  String get selectedDateFormatted => DateFormat('MMM dd, yyyy').format(_selectedDate);
  bool get isToday => DateFormat('yyyy-MM-dd').format(_selectedDate) == DateFormat('yyyy-MM-dd').format(DateTime.now());

  /// Fetch daily stats from backend using ApiService (consistent with profile/chat)
  Future<void> fetchDailyStats(AuthProvider authProvider, {DateTime? date, bool forceRefresh = false}) async {
    if (date != null) _selectedDate = date;
    
    // 🔴 PHASE 1: If real-time is enabled, skip polling (listener handles updates)
    if (FeatureFlags.realtimeUpdatesEnabled && !forceRefresh) {
      print('🔴 Real-time enabled for dashboard, skipping API fetch (listener active)');
      return;
    }
    
    // 🚀 HYBRID OPTIMIZATION: Check cache first
    if (!forceRefresh) {
      final dateKey = DateFormat('yyyy-MM-dd').format(_selectedDate);
      final cachedDateKey = _cacheDate != null ? DateFormat('yyyy-MM-dd').format(_cacheDate!) : null;
      
      if (_cachedStats != null &&
          _cacheTimestamp != null &&
          cachedDateKey == dateKey &&
          DateTime.now().difference(_cacheTimestamp!) < _cacheDuration) {
        // ⚡ Cache hit! Use cached data (instant!)
        _stats = _cachedStats!;
        print('⚡ Cache hit! Loaded stats for $dateKey instantly');
        notifyListeners();
        
        // 🔄 Refresh in background (silent)
        _refreshInBackground(authProvider);
        return;
      }
    }
    
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // Create ApiService instance (same pattern as used elsewhere in the app)
      final apiService = ApiService(authProvider);
      
      // Get start and end of the selected day in LOCAL time, then convert to UTC
      // This ensures we query the correct 24-hour window in the user's timezone
      final startOfDayLocal = DateTime(_selectedDate.year, _selectedDate.month, _selectedDate.day);
      final endOfDayLocal = startOfDayLocal.add(const Duration(days: 1));
      
      // Convert to UTC for API query (backend stores all timestamps in UTC)
      final startOfDay = startOfDayLocal.toUtc();
      final endOfDay = endOfDayLocal.toUtc();

      print('🔍 Fetching data for ${DateFormat('yyyy-MM-dd').format(_selectedDate)} (local)');
      print('🔍 UTC range: ${startOfDay.toIso8601String()} to ${endOfDay.toIso8601String()}');

      // Fetch fitness logs using ApiService (handles auth, HTTPS, errors automatically)
      List<dynamic> fitnessLogs = [];
      try {
        final logs = await apiService.getFitnessLogs(
          startDate: startOfDay,
          endDate: endOfDay,
        );
        fitnessLogs = logs.map((log) => log.toJson()).toList();
        print('✅ Fetched ${fitnessLogs.length} fitness logs');
      } catch (e) {
        print('⚠️  Fitness logs fetch error: $e');
        _errorMessage = 'Failed to load meals: $e';
      }

      // Fetch tasks using ApiService (independent of fitness logs)
      // Note: Don't filter by date - we want ALL tasks (including those without due dates)
      List<dynamic> tasks = [];
      try {
        final taskModels = await apiService.getTasks();  // Removed date filter
        tasks = taskModels.map((task) => task.toJson()).toList();
        print('✅ Fetched ${tasks.length} tasks');
      } catch (e) {
        print('⚠️  Tasks fetch error: $e (continuing with meals only)');
        // Don't fail the entire request - tasks are optional
      }

      // Process data (even if one source failed)
      print('🔄 Processing ${fitnessLogs.length} logs and ${tasks.length} tasks');
      _processStats(fitnessLogs, tasks);
      
      // 🚀 HYBRID OPTIMIZATION: Update cache
      _cachedStats = _stats;
      _cacheTimestamp = DateTime.now();
      _cacheDate = _selectedDate;
      
    } catch (e) {
      _errorMessage = 'Failed to load data: $e';
      print('❌ Exception in fetchDailyStats: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// 🚀 HYBRID OPTIMIZATION: Refresh cache in background (silent)
  Future<void> _refreshInBackground(AuthProvider authProvider) async {
    try {
      final apiService = ApiService(authProvider);
      
      final startOfDayLocal = DateTime(_selectedDate.year, _selectedDate.month, _selectedDate.day);
      final endOfDayLocal = startOfDayLocal.add(const Duration(days: 1));
      final startOfDay = startOfDayLocal.toUtc();
      final endOfDay = endOfDayLocal.toUtc();

      // Fetch fitness logs
      List<dynamic> fitnessLogs = [];
      try {
        final logs = await apiService.getFitnessLogs(
          startDate: startOfDay,
          endDate: endOfDay,
        );
        fitnessLogs = logs.map((log) => log.toJson()).toList();
      } catch (e) {
        print('⚠️  Background refresh - fitness logs error: $e');
      }

      // Fetch tasks
      List<dynamic> tasks = [];
      try {
        final taskModels = await apiService.getTasks();
        tasks = taskModels.map((task) => task.toJson()).toList();
      } catch (e) {
        print('⚠️  Background refresh - tasks error: $e');
      }

      // Process and update cache silently
      _processStats(fitnessLogs, tasks);
      _cachedStats = _stats;
      _cacheTimestamp = DateTime.now();
      _cacheDate = _selectedDate;
      
      print('🔄 Background refresh complete for ${DateFormat('yyyy-MM-dd').format(_selectedDate)}');
      notifyListeners();
    } catch (e) {
      print('⚠️  Background refresh failed: $e');
      // Don't update error state - this is a silent refresh
    }
  }
  
  /// 🚀 HYBRID OPTIMIZATION: Invalidate cache (force refresh on next load)
  void invalidateCache() {
    _cachedStats = null;
    _cacheTimestamp = null;
    _cacheDate = null;
    print('🗑️  Dashboard cache invalidated');
  }
  
  /// 🚀 HYBRID OPTIMIZATION: Update stats optimistically (instant UI update)
  void updateStatsOptimistically(DailyStats newStats) {
    _stats = newStats;
    
    // Also update cache if it exists
    if (_cachedStats != null) {
      _cachedStats = newStats;
      _cacheTimestamp = DateTime.now();
    }
    
    print('⚡ Stats updated optimistically');
    notifyListeners();
  }

  /// Process raw data into stats
  void _processStats(List<dynamic> fitnessLogs, List<dynamic> tasks) {
    print('🔄 Processing ${fitnessLogs.length} fitness logs...');
    
    int totalCalories = 0;
    int totalCaloriesBurned = 0;
    double totalProtein = 0;
    double totalCarbs = 0;
    double totalFat = 0;
    double totalFiber = 0;
    int totalWater = 0;
    int workouts = 0;
    List<ActivityItem> activities = [];

    // Process fitness logs
    final logs = fitnessLogs;
    for (var log in logs) {
      try {
        final logType = log['log_type'] as String?;
        final content = log['content'] as String? ?? '';
        final calories = log['calories'] as int? ?? 0;
        final aiParsedData = log['ai_parsed_data'] as Map<String, dynamic>? ?? {};
        final timestamp = DateTime.parse(log['timestamp'] as String);

        print('  📝 Processing log: type=$logType, content=$content, calories=$calories');

        if (logType == 'meal') {
        // Extract macros from ai_parsed_data
        final protein = (aiParsedData['protein_g'] as num?)?.toDouble() ?? 0;
        final carbs = (aiParsedData['carbs_g'] as num?)?.toDouble() ?? 0;
        final fat = (aiParsedData['fat_g'] as num?)?.toDouble() ?? 0;
        final fiber = (aiParsedData['fiber_g'] as num?)?.toDouble() ?? 0;

        totalCalories += calories;
        totalProtein += protein;
        totalCarbs += carbs;
        totalFat += fat;
        totalFiber += fiber;

        activities.add(ActivityItem(
          id: log['log_id'] as String? ?? '',
          type: 'meal',
          title: content.isNotEmpty ? content : 'Meal',
          subtitle: '$calories cal • ${protein.toStringAsFixed(0)}g protein',
          timestamp: timestamp,
          data: aiParsedData,
        ));
      } else if (logType == 'workout') {
        workouts++;
        final duration = aiParsedData['duration_minutes'] as int? ?? 0;
        final caloriesBurned = calories; // Workout calories = calories burned
        totalCaloriesBurned += caloriesBurned;
        
        activities.add(ActivityItem(
          id: log['log_id'] as String? ?? '',
          type: 'workout',
          title: content.isNotEmpty ? content : 'Workout',
          subtitle: '$duration min • $caloriesBurned cal burned',
          timestamp: timestamp,
          data: aiParsedData,
        ));
      } else if (logType == 'water') {
        // ✅ FIX: Process water logs
        final quantityMl = aiParsedData['quantity_ml'] as int? ?? 0;
        totalWater += quantityMl;
        
        activities.add(ActivityItem(
          id: log['log_id'] as String? ?? '',
          type: 'water',
          title: content.isNotEmpty ? content : 'Water',
          subtitle: '$quantityMl ml',
          timestamp: timestamp,
          data: aiParsedData,
        ));
      } else if (logType == 'supplement') {
        // ✅ FIX: Process supplement logs
        activities.add(ActivityItem(
          id: log['log_id'] as String? ?? '',
          type: 'supplement',
          title: content.isNotEmpty ? content : 'Supplement',
          subtitle: aiParsedData['dosage'] as String? ?? 'taken',
          timestamp: timestamp,
          data: aiParsedData,
        ));
      }
      } catch (e) {
        print('⚠️  Error processing log: $e');
        // Continue processing other logs
      }
    }

    // Process tasks
    for (var task in tasks) {
      final status = task['status'] as String?;
      if (status == 'completed') {
        activities.add(ActivityItem(
          id: task['task_id'] as String? ?? '',
          type: 'task',
          title: task['title'] as String? ?? 'Task',
          subtitle: 'Completed',
          timestamp: DateTime.parse(task['updated_at'] as String),
        ));
      }
    }

    // Sort activities by timestamp (newest first)
    activities.sort((a, b) => b.timestamp.compareTo(a.timestamp));

    _stats = DailyStats(
      caloriesConsumed: totalCalories,
      caloriesBurned: totalCaloriesBurned,
      caloriesGoal: _stats.caloriesGoal, // Keep existing goal
      proteinG: totalProtein,
      proteinGoal: _stats.proteinGoal,
      carbsG: totalCarbs,
      carbsGoal: _stats.carbsGoal,
      fatG: totalFat,
      fatGoal: _stats.fatGoal,
      fiberG: totalFiber,
      fiberGoal: _stats.fiberGoal,
      waterMl: totalWater,
      waterGoal: _stats.waterGoal,
      workoutsCompleted: workouts,
      workoutsGoal: _stats.workoutsGoal,
      activities: activities,
    );
  }

  /// Update goals from profile
  void updateGoalsFromProfile(Map<String, dynamic> goals) {
    _stats = DailyStats(
      caloriesConsumed: _stats.caloriesConsumed,
      caloriesBurned: _stats.caloriesBurned,
      caloriesGoal: goals['calories'] as int? ?? 2000,
      proteinG: _stats.proteinG,
      proteinGoal: (goals['protein_g'] as num?)?.toDouble() ?? 150,
      carbsG: _stats.carbsG,
      carbsGoal: (goals['carbs_g'] as num?)?.toDouble() ?? 200,
      fatG: _stats.fatG,
      fatGoal: (goals['fat_g'] as num?)?.toDouble() ?? 65,
      fiberG: _stats.fiberG,
      fiberGoal: (goals['fiber_g'] as num?)?.toDouble() ?? 25,
      waterMl: _stats.waterMl,
      waterGoal: goals['water_ml'] as int? ?? 2000,
      workoutsCompleted: _stats.workoutsCompleted,
      workoutsGoal: goals['workouts_per_week'] as int? ?? 1,
      activities: _stats.activities,
    );
    notifyListeners();
  }

  /// Change selected date
  void changeDate(DateTime date) {
    _selectedDate = date;
    notifyListeners();
  }

  /// Go to previous day
  void previousDay() {
    _selectedDate = _selectedDate.subtract(const Duration(days: 1));
    notifyListeners();
  }

  /// Go to next day
  void nextDay() {
    _selectedDate = _selectedDate.add(const Duration(days: 1));
    notifyListeners();
  }

  /// Go to today
  void goToToday() {
    _selectedDate = DateTime.now();
    notifyListeners();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
  
  // 🔴 PHASE 1: Real-Time Listener Methods
  
  /// Start real-time listener for dashboard updates
  /// 
  /// This replaces polling with push-based updates when feature flag is enabled.
  /// Falls back to polling if real-time is disabled.
  void startRealtimeListener(String userId, AuthProvider authProvider) {
    if (!FeatureFlags.realtimeUpdatesEnabled) {
      print('⚪ Real-time disabled for dashboard, using polling');
      return;
    }
    
    print('🔴 Starting real-time dashboard listener');
    
    _realtimeService.listenToDashboard(
      userId: userId,
      onUpdate: (stats) {
        // Update stats from real-time stream
        print('🔴 Real-time dashboard update: ${stats['calories']} cal, ${stats['protein_g']}g protein');
        
        // Update current stats with real-time data
        _stats = DailyStats(
          caloriesConsumed: stats['calories'] as int? ?? 0,
          caloriesBurned: 0, // TODO: Add burned calories to real-time
          caloriesGoal: _stats.caloriesGoal, // Keep existing goal
          proteinG: (stats['protein_g'] as num?)?.toDouble() ?? 0,
          proteinGoal: _stats.proteinGoal,
          carbsG: (stats['carbs_g'] as num?)?.toDouble() ?? 0,
          carbsGoal: _stats.carbsGoal,
          fatG: (stats['fat_g'] as num?)?.toDouble() ?? 0,
          fatGoal: _stats.fatGoal,
          fiberG: 0, // TODO: Add fiber to real-time
          fiberGoal: _stats.fiberGoal,
          waterMl: stats['water_ml'] as int? ?? 0,
          waterGoal: _stats.waterGoal,
          workoutsCompleted: stats['workouts'] as int? ?? 0,
          workoutsGoal: _stats.workoutsGoal,
          activities: _stats.activities, // Keep existing activities (tasks)
        );
        
        // Update cache
        _cachedStats = _stats;
        _cacheTimestamp = DateTime.now();
        _cacheDate = _selectedDate;
        
        notifyListeners();
      },
      onError: (error) {
        print('❌ Real-time dashboard listener error: $error');
        _errorMessage = error;
        notifyListeners();
        
        // Fall back to polling on error
        fetchDailyStats(authProvider);
      },
    );
  }
  
  /// Stop real-time listener
  void stopRealtimeListener() {
    print('🔴 Stopping real-time dashboard listener');
    // The service will handle cleanup
  }
  
  @override
  void dispose() {
    stopRealtimeListener();
    super.dispose();
  }
}

