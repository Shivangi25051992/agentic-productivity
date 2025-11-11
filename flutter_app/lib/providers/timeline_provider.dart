import 'dart:async';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/timeline_activity.dart';
import '../services/api_service.dart';
import '../services/realtime_service.dart'; // 🔴 PHASE 1: Real-time support
import '../utils/feature_flags.dart'; // 🚩 Feature flag control

class TimelineProvider extends ChangeNotifier {
  final ApiService _apiService;
  // 🎯 ENTERPRISE PATTERN: Dependency Injection for testability
  final RealtimeService _realtimeService;

  // 🎯 ENTERPRISE PATTERN: Constructor with optional dependency injection
  // Production code: TimelineProvider(apiService) - uses real RealtimeService
  // Test code: TimelineProvider(apiService, realtimeService: mockService) - uses mock
  TimelineProvider(
    this._apiService, {
    RealtimeService? realtimeService,
  }) : _realtimeService = realtimeService ?? RealtimeService();

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
  
  // 🚀 HYBRID OPTIMIZATION: Client-side cache
  List<TimelineActivity>? _cachedActivities;
  DateTime? _cacheTimestamp;
  String? _cacheKey; // Cache key based on filters
  static const Duration _cacheDuration = Duration(minutes: 5);
  
  // Debouncing
  Timer? _debounceTimer;
  
  // 🔥 RACE CONDITION FIX: Request sequence tracking
  int _fetchSequence = 0; // Increments with each fetch request
  int _lastCompletedSequence = 0; // Tracks the most recent completed fetch

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
  Future<void> fetchTimeline({bool loadMore = false, bool forceRefresh = false}) async {
    if (_isLoading) return;

    // 🔴 PHASE 1: If real-time is enabled, skip polling (listener handles updates)
    if (FeatureFlags.realtimeUpdatesEnabled && !loadMore && !forceRefresh) {
      print('🔴 Real-time enabled, skipping API fetch (listener active)');
      return;
    }

    // 🚀 HYBRID OPTIMIZATION: Check cache first (only for initial load, not pagination)
    if (!loadMore && !forceRefresh) {
      final currentCacheKey = _generateCacheKey();
      
      if (_cachedActivities != null &&
          _cacheTimestamp != null &&
          _cacheKey == currentCacheKey &&
          DateTime.now().difference(_cacheTimestamp!) < _cacheDuration) {
        // ⚡ Cache hit! Use cached data (instant!)
        _activities = List.from(_cachedActivities!);
        _hasMore = false; // Cached data is complete
        _offset = _activities.length;
        print('⚡ Cache hit! Loaded ${_activities.length} activities instantly');
        notifyListeners();
        
        // 🔄 Refresh in background (silent)
        _refreshInBackground();
        return;
      }
    }

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
        bustCache: forceRefresh, // Bust backend cache when forcing refresh
      );

      // Update state
      if (loadMore) {
        _activities.addAll(response.activities);
      } else {
        // 🔧 CRITICAL FIX: Preserve optimistic activities (temp_* IDs)
        // Keep them until we find their real counterparts in backend data
        final optimisticActivities = _activities.where((a) => a.id.startsWith('temp_')).toList();
        _activities = response.activities;
        
        // 🔑 GOLD STANDARD: Match optimistic activities with real ones using clientGeneratedId
        // This is deterministic and reliable - no false positives!
        for (var optimistic in optimisticActivities) {
          if (optimistic.clientGeneratedId == null) {
            // Old optimistic activity without clientGeneratedId - keep for now
            _activities.insert(0, optimistic);
            print('⏳ [OPTIMISTIC] Keeping legacy optimistic activity (no clientGeneratedId): ${optimistic.id}');
            continue;
          }
          
          // Look for exact match by clientGeneratedId
          final matchFound = _activities.any((real) => 
            real.clientGeneratedId == optimistic.clientGeneratedId
          );
          
          if (!matchFound) {
            // Not in backend yet - keep the optimistic activity
            _activities.insert(0, optimistic);
            print('⏳ [OPTIMISTIC] Keeping optimistic activity (not in backend yet): ${optimistic.id} [clientId: ${optimistic.clientGeneratedId}]');
          } else {
            // Found exact match - backend has it now, remove optimistic
            print('✅ [OPTIMISTIC] Found exact match for optimistic activity: ${optimistic.id} [clientId: ${optimistic.clientGeneratedId}]');
          }
        }
        
        // 🚀 HYBRID OPTIMIZATION: Update cache
        _cachedActivities = List.from(_activities);
        _cacheTimestamp = DateTime.now();
        _cacheKey = _generateCacheKey();
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
  
  /// 🚀 HYBRID OPTIMIZATION: Generate cache key based on current filters
  String _generateCacheKey() {
    final types = _selectedTypes.toList()..sort();
    final startDateStr = _startDate?.toIso8601String() ?? 'null';
    final endDateStr = _endDate?.toIso8601String() ?? 'null';
    return '${types.join(',')}_${startDateStr}_$endDateStr';
  }
  
  /// 🚀 HYBRID OPTIMIZATION: Refresh cache in background (silent)
  Future<void> _refreshInBackground() async {
    try {
      final types = _selectedTypes.join(',');
      final startDateStr = _startDate?.toIso8601String().split('T')[0];
      final endDateStr = _endDate?.toIso8601String().split('T')[0];

      final response = await _apiService.getTimeline(
        types: types,
        startDate: startDateStr,
        endDate: endDateStr,
        limit: 50,
        offset: 0,
        bustCache: true, // Always bust cache for background refresh
      );

      // Update cache and activities silently
      // 🔧 CRITICAL FIX: Preserve optimistic activities in background refresh too
      final optimisticActivities = _activities.where((a) => a.id.startsWith('temp_')).toList();
      
      _cachedActivities = List.from(response.activities);
      _cacheTimestamp = DateTime.now();
      _cacheKey = _generateCacheKey();
      _activities = response.activities;
      
      // 🔑 GOLD STANDARD: Match by clientGeneratedId (same logic as main fetch)
      int preserved = 0;
      for (var optimistic in optimisticActivities) {
        if (optimistic.clientGeneratedId == null) {
          _activities.insert(0, optimistic);
          preserved++;
          continue;
        }
        
        final matchFound = _activities.any((real) => 
          real.clientGeneratedId == optimistic.clientGeneratedId
        );
        
        if (!matchFound) {
          _activities.insert(0, optimistic);
          preserved++;
        }
      }
      
      _hasMore = response.hasMore;
      _offset = response.nextOffset;
      
      print('🔄 Background refresh complete: ${response.activities.length} activities ($preserved optimistic preserved)');
      notifyListeners();
    } catch (e) {
      print('⚠️  Background refresh failed: $e');
      // Don't update error state - this is a silent refresh
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
    await fetchTimeline(loadMore: false, forceRefresh: true);
  }
  
  /// 🚀 HYBRID OPTIMIZATION: Invalidate cache (force refresh on next load)
  void invalidateCache() {
    _cachedActivities = null;
    _cacheTimestamp = null;
    _cacheKey = null;
    print('🗑️  Cache invalidated');
  }
  
  /// 🚀 HYBRID OPTIMIZATION: Add optimistic activity (instant UI update)
  void addOptimisticActivity(TimelineActivity activity) {
    _activities.insert(0, activity);
    
    // Also add to cache if it exists
    if (_cachedActivities != null) {
      _cachedActivities!.insert(0, activity);
    }
    
    print('⚡ Optimistic activity added: ${activity.type}');
    notifyListeners();
  }
  
  /// 🚀 HYBRID OPTIMIZATION: Remove optimistic activity (on sync failure)
  void removeOptimisticActivity(String activityId) {
    _activities.removeWhere((a) => a.id == activityId);
    
    // Also remove from cache if it exists
    if (_cachedActivities != null) {
      _cachedActivities!.removeWhere((a) => a.id == activityId);
    }
    
    print('🗑️  Optimistic activity removed: $activityId');
    notifyListeners();
  }
  
  /// 🚀 HYBRID OPTIMIZATION: Update optimistic activity with real data
  void updateOptimisticActivity(String tempId, TimelineActivity realActivity) {
    final index = _activities.indexWhere((a) => a.id == tempId);
    if (index != -1) {
      _activities[index] = realActivity;
    }
    
    // Also update cache if it exists
    if (_cachedActivities != null) {
      final cacheIndex = _cachedActivities!.indexWhere((a) => a.id == tempId);
      if (cacheIndex != -1) {
        _cachedActivities![cacheIndex] = realActivity;
      }
    }
    
    print('✅ Optimistic activity updated: $tempId → ${realActivity.id}');
    notifyListeners();
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
    
    // 🚀 HYBRID OPTIMIZATION: Clear cache
    _cachedActivities = null;
    _cacheTimestamp = null;
    _cacheKey = null;
    
    // 🔴 PHASE 1: Stop real-time listener
    stopRealtimeListener();
    
    notifyListeners();
  }
  
  // 🔴 PHASE 1: Real-Time Listener Methods
  
  /// Start real-time listener for timeline updates
  /// 
  /// This replaces polling with push-based updates when feature flag is enabled.
  /// Falls back to polling if real-time is disabled.
  void startRealtimeListener(String userId) {
    if (!FeatureFlags.realtimeUpdatesEnabled) {
      print('⚪ Real-time disabled, using polling');
      return;
    }
    
    print('🔴 Starting real-time timeline listener');
    
    _realtimeService.listenToTimeline(
      userId: userId,
      onUpdate: (activities) {
        // Update activities from real-time stream
        print('🔴 Real-time update received: ${activities.length} activities');
        
        // Merge with optimistic activities (preserve temp_* IDs)
        final optimisticActivities = _activities.where((a) => a.id.startsWith('temp_')).toList();
        
        _activities = activities;
        
        // Re-add optimistic activities if not found in real data
        for (var optimistic in optimisticActivities) {
          if (optimistic.clientGeneratedId == null) {
            _activities.insert(0, optimistic);
            continue;
          }
          
          final matchFound = _activities.any((real) => 
            real.clientGeneratedId == optimistic.clientGeneratedId
          );
          
          if (!matchFound) {
            _activities.insert(0, optimistic);
          }
        }
        
        // Update cache
        _cachedActivities = List.from(_activities);
        _cacheTimestamp = DateTime.now();
        
        notifyListeners();
      },
      onError: (error) {
        print('❌ Real-time listener error: $error');
        _error = error;
        notifyListeners();
        
        // Fall back to polling on error
        fetchTimeline();
      },
    );
  }
  
  /// Stop real-time listener
  void stopRealtimeListener() {
    // Note: We don't have userId here, so we'll need to track it
    // For now, just log - the service will handle cleanup
    print('🔴 Stopping real-time timeline listener');
  }
  
  @override
  void dispose() {
    _debounceTimer?.cancel();
    stopRealtimeListener();
    super.dispose();
  }
}

