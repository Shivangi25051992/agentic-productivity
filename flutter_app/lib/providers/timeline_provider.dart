import 'dart:async';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/timeline_activity.dart';
import '../services/api_service.dart';

class TimelineProvider extends ChangeNotifier {
  final ApiService _apiService;

  TimelineProvider(this._apiService);

  // State
  List<TimelineActivity> _activities = [];
  Set<String> _selectedTypes = {'meal', 'workout', 'task', 'event', 'water', 'supplement'};
  DateTime? _startDate;
  DateTime? _endDate;
  bool _isLoading = false;
  bool _hasMore = true;
  int _offset = 0;
  Map<String, bool> _expandedStates = {};
  Map<String, bool> _sectionExpandedStates = {}; // NEW: Section collapse state
  String? _error;
  
  // Debouncing
  Timer? _debounceTimer;

  // Getters
  List<TimelineActivity> get activities => _activities;
  Set<String> get selectedTypes => _selectedTypes;
  DateTime? get startDate => _startDate;
  DateTime? get endDate => _endDate;
  bool get isLoading => _isLoading;
  bool get hasMore => _hasMore;
  String? get error => _error;

  /// Get activities grouped by date sections
  Map<String, List<TimelineActivity>> get groupedActivities {
    return _groupByDate();
  }

  /// Check if an activity is expanded
  bool isExpanded(String activityId) {
    return _expandedStates[activityId] ?? false;
  }
  
  /// Check if a section is expanded (default: true)
  bool isSectionExpanded(String sectionKey) {
    return _sectionExpandedStates[sectionKey] ?? true;
  }

  /// Get count of activities by type
  Map<String, int> get activityCounts {
    final counts = <String, int>{};
    for (var activity in _activities) {
      counts[activity.type] = (counts[activity.type] ?? 0) + 1;
    }
    return counts;
  }

  /// Fetch timeline data
  Future<void> fetchTimeline({bool loadMore = false}) async {
    if (_isLoading) return;

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // If not loading more, reset offset and activities
      if (!loadMore) {
        _offset = 0;
        _activities = [];
      }

      // Build query parameters
      final types = _selectedTypes.join(',');
      final startDateStr = _startDate?.toIso8601String().split('T')[0];
      final endDateStr = _endDate?.toIso8601String().split('T')[0];

      // Call API
      final response = await _apiService.getTimeline(
        types: types,
        startDate: startDateStr,
        endDate: endDateStr,
        limit: 50,
        offset: _offset,
      );

      // Update state
      if (loadMore) {
        _activities.addAll(response.activities);
      } else {
        _activities = response.activities;
      }

      _hasMore = response.hasMore;
      _offset = response.nextOffset;

      print('✅ Fetched ${response.activities.length} timeline activities');
    } catch (e) {
      _error = e.toString();
      print('❌ Error fetching timeline: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Toggle filter type (with debouncing)
  void toggleFilter(String type) {
    if (_selectedTypes.contains(type)) {
      // Don't allow unchecking if it's the last selected filter
      if (_selectedTypes.length > 1) {
        _selectedTypes.remove(type);
      } else {
        // Show a message or just prevent the action
        print('⚠️  Cannot uncheck last filter - at least one must be selected');
        return; // Don't proceed if trying to uncheck the last filter
      }
    } else {
      _selectedTypes.add(type);
    }
    
    // Notify immediately for UI update
    notifyListeners();

    // Debounce the API call (300ms)
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 300), () {
      fetchTimeline();
    });
  }

  /// Set date range filter
  void setDateRange(DateTime? start, DateTime? end) {
    _startDate = start;
    _endDate = end;

    // Refresh timeline with new date range
    fetchTimeline();
  }

  /// Clear date range filter
  void clearDateRange() {
    _startDate = null;
    _endDate = null;
    fetchTimeline();
  }

  /// Toggle expanded state for an activity
  void toggleExpanded(String activityId) {
    _expandedStates[activityId] = !(_expandedStates[activityId] ?? false);
    notifyListeners();
  }
  
  /// Toggle section expanded/collapsed state
  void toggleSection(String sectionKey) {
    _sectionExpandedStates[sectionKey] = !isSectionExpanded(sectionKey);
    notifyListeners();
  }

  /// Refresh timeline (pull to refresh)
  Future<void> refresh() async {
    await fetchTimeline(loadMore: false);
  }

  /// Load more activities (pagination)
  Future<void> loadMore() async {
    if (!_hasMore || _isLoading) return;
    await fetchTimeline(loadMore: true);
  }

  /// Group activities by date sections
  Map<String, List<TimelineActivity>> _groupByDate() {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));

    Map<String, List<TimelineActivity>> grouped = {
      'Upcoming & Overdue': [],
      'Today': [],
      'Yesterday': [],
    };

    for (var activity in _activities) {
      // Convert UTC timestamp to local time for date comparison
      final localTimestamp = activity.timestamp.toLocal();
      final activityDate = DateTime(
        localTimestamp.year,
        localTimestamp.month,
        localTimestamp.day,
      );

      // Overdue tasks
      if (activity.isOverdue) {
        grouped['Upcoming & Overdue']!.add(activity);
      }
      // Upcoming tasks/events (future)
      else if (activity.isUpcoming && activityDate.isAfter(today)) {
        grouped['Upcoming & Overdue']!.add(activity);
      }
      // Today
      else if (activityDate == today) {
        grouped['Today']!.add(activity);
      }
      // Yesterday
      else if (activityDate == yesterday) {
        grouped['Yesterday']!.add(activity);
      }
      // Other dates
      else {
        final key = DateFormat('MMMM d, yyyy').format(activityDate);
        grouped.putIfAbsent(key, () => []);
        grouped[key]!.add(activity);
      }
    }

    // Remove empty sections
    grouped.removeWhere((key, value) => value.isEmpty);

    // Sort activities within each section by timestamp
    for (var section in grouped.values) {
      section.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    }

    return grouped;
  }

  /// Clear all data
  void clear() {
    _activities = [];
    _offset = 0;
    _hasMore = true;
    _expandedStates = {};
    _sectionExpandedStates = {};
    _error = null;
    _debounceTimer?.cancel();
    notifyListeners();
  }
  
  @override
  void dispose() {
    _debounceTimer?.cancel();
    super.dispose();
  }
}

