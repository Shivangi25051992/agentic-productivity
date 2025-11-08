import 'dart:convert';
import 'api_service.dart';

/// Fasting API Service
/// Handles all fasting-related API calls
class FastingApiService {
  final ApiService _api;

  FastingApiService(this._api);

  // ========================================================================
  // SESSION MANAGEMENT
  // ========================================================================

  /// Start a new fasting session
  Future<Map<String, dynamic>> startFasting({
    required int targetDurationHours,
    required String protocol,
    String? notes,
  }) async {
    try {
      final response = await _api.post('/fasting/start', {
        'target_duration_hours': targetDurationHours,
        'protocol': protocol,
        'notes': notes,
      });
      print('✅ Started fasting session: ${response['id']}');
      return response;
    } catch (e) {
      print('❌ Error starting fasting: $e');
      rethrow;
    }
  }

  /// End an active fasting session
  Future<Map<String, dynamic>> endFasting({
    required String sessionId,
    required String breakReason,
    required int energyLevel,
    required int hungerLevel,
    String? notes,
  }) async {
    try {
      final response = await _api.post('/fasting/end/$sessionId', {
        'break_reason': breakReason,
        'energy_level': energyLevel,
        'hunger_level': hungerLevel,
        'notes': notes,
      });
      print('✅ Ended fasting session: $sessionId');
      return response;
    } catch (e) {
      print('❌ Error ending fasting: $e');
      rethrow;
    }
  }

  /// Get current active fasting session
  Future<Map<String, dynamic>?> getCurrentSession() async {
    try {
      final response = await _api.get('/fasting/current');
      if (response.isEmpty) return null;
      return response;
    } catch (e) {
      print('❌ Error getting current session: $e');
      return null;
    }
  }

  /// Get fasting session by ID
  Future<Map<String, dynamic>> getSession(String sessionId) async {
    try {
      return await _api.get('/fasting/sessions/$sessionId');
    } catch (e) {
      print('❌ Error getting session: $e');
      rethrow;
    }
  }

  /// Get fasting history
  Future<List<Map<String, dynamic>>> getHistory({int limit = 30}) async {
    try {
      final response = await _api.get('/fasting/history?limit=$limit');
      // Response is a Map with a 'data' or direct list
      if (response is Map && response.containsKey('data')) {
        final data = response['data'];
        if (data is List) {
          return List<Map<String, dynamic>>.from(data.map((e) => e as Map<String, dynamic>));
        }
      }
      // If response is directly a list (shouldn't happen with our API but handle it)
      return [];
    } catch (e) {
      print('❌ Error getting history: $e');
      return [];
    }
  }

  // ========================================================================
  // ANALYTICS
  // ========================================================================

  /// Get fasting analytics
  Future<Map<String, dynamic>> getAnalytics({int periodDays = 30}) async {
    try {
      return await _api.get('/fasting/analytics?period_days=$periodDays');
    } catch (e) {
      print('❌ Error getting analytics: $e');
      rethrow;
    }
  }

  // ========================================================================
  // PROFILE
  // ========================================================================

  /// Get fasting profile
  Future<Map<String, dynamic>?> getProfile() async {
    try {
      final response = await _api.get('/fasting/profile');
      if (response.isEmpty) return null;
      return response;
    } catch (e) {
      print('❌ Error getting profile: $e');
      return null;
    }
  }

  /// Update fasting profile
  Future<Map<String, dynamic>> updateProfile({
    required String defaultProtocol,
    required String eatingWindowStart,
    required String eatingWindowEnd,
    String? experienceLevel,
    List<String>? goals,
  }) async {
    try {
      return await _api.put('/fasting/profile', {
        'default_protocol': defaultProtocol,
        'eating_window_start': eatingWindowStart,
        'eating_window_end': eatingWindowEnd,
        'experience_level': experienceLevel,
        'goals': goals,
      });
    } catch (e) {
      print('❌ Error updating profile: $e');
      rethrow;
    }
  }

  // ========================================================================
  // AI COACHING
  // ========================================================================

  /// Get coaching context for AI
  Future<Map<String, dynamic>> getCoachingContext() async {
    try {
      return await _api.get('/fasting/coaching/context');
    } catch (e) {
      print('❌ Error getting coaching context: $e');
      rethrow;
    }
  }

  /// Get fasting window recommendation
  Future<Map<String, dynamic>> getWindowRecommendation({
    required Map<String, dynamic> userSchedule,
  }) async {
    try {
      return await _api.post('/fasting/coaching/recommend-window', userSchedule);
    } catch (e) {
      print('❌ Error getting recommendation: $e');
      rethrow;
    }
  }
}

