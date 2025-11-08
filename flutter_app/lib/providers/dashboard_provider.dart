import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';

import '../utils/constants.dart';
import '../services/api_service.dart';
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
  DailyStats _stats = DailyStats();
  bool _isLoading = false;
  String? _errorMessage;
  DateTime _selectedDate = DateTime.now();

  DailyStats get stats => _stats;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  DateTime get selectedDate => _selectedDate;
  String get selectedDateFormatted => DateFormat('MMM dd, yyyy').format(_selectedDate);
  bool get isToday => DateFormat('yyyy-MM-dd').format(_selectedDate) == DateFormat('yyyy-MM-dd').format(DateTime.now());

  /// Fetch daily stats from backend using ApiService (consistent with profile/chat)
  Future<void> fetchDailyStats(AuthProvider authProvider, {DateTime? date}) async {
    _isLoading = true;
    _errorMessage = null;
    if (date != null) _selectedDate = date;
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
      
    } catch (e) {
      _errorMessage = 'Failed to load data: $e';
      print('❌ Exception in fetchDailyStats: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
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
}

