import 'dart:developer' as dev;
import 'package:flutter/foundation.dart';

import 'package:dio/dio.dart';

import '../models/fitness_log.dart';
import '../models/task.dart';
import '../models/user.dart';
import '../models/timeline_activity.dart';
import '../providers/auth_provider.dart';
import '../utils/constants.dart';

class ApiException implements Exception { 
  final String message; 
  ApiException(this.message); 
  @override
  String toString() => message;
}
class NetworkException implements Exception { 
  final String message; 
  NetworkException(this.message); 
  @override
  String toString() => message;
}
class AuthException implements Exception { 
  final String message; 
  AuthException(this.message); 
  @override
  String toString() => message;
}
class ValidationException implements Exception { 
  final String message; 
  ValidationException(this.message); 
  @override
  String toString() => message;
}

class ApiService {
  final Dio _dio;
  final AuthProvider _authProvider;
  final VoidCallback? onUnauthorized;
  ApiService(this._authProvider, { this.onUnauthorized })
      : _dio = Dio(BaseOptions(
          baseUrl: AppConstants.apiBaseUrl,
          connectTimeout: const Duration(seconds: 12),
          receiveTimeout: const Duration(seconds: 120), // Increased for meal plan generation (takes 15-90s)
          headers: {'Content-Type': 'application/json'},
        )) {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        try {
          final token = await _authProvider.getIdToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
        } catch (_) {}
        return handler.next(options);
      },
      onError: (e, handler) async {
        if (e.type == DioExceptionType.connectionTimeout || e.type == DioExceptionType.receiveTimeout) {
          return handler.reject(DioException(requestOptions: e.requestOptions, error: NetworkException('Request timed out')));
        }
        if (e.response?.statusCode == 401) {
          // Attempt refresh (Firebase auto-refreshes tokens via SDK when valid)
          try {
            final token = await _authProvider.getIdToken();
            if (token != null) {
              e.requestOptions.headers['Authorization'] = 'Bearer $token';
              final clone = await _dio.fetch(e.requestOptions);
              return handler.resolve(clone);
            }
          } catch (_) {}
          onUnauthorized?.call();
          return handler.reject(DioException(requestOptions: e.requestOptions, error: AuthException('Unauthorized')));
        }
        return handler.next(e);
      },
      onResponse: (resp, handler) {
        assert(() {
          dev.log('API ${resp.requestOptions.method} ${resp.requestOptions.uri} → ${resp.statusCode}');
          return true;
        }());
        return handler.next(resp);
      },
    ));
  }

  // Chat & AI
  Future<Map<String, dynamic>> sendChatMessage(String message, String type) async {
    try {
      final resp = await _dio.post(
        '/chat',
        data: {
          'user_input': message,
          'type': type,
        },
      );
      return (resp.data as Map).cast<String, dynamic>();
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  // Tasks
  Future<TaskModel> createTask(Map<String, dynamic> taskData) async {
    try {
      final resp = await _dio.post('/tasks', data: taskData);
      return TaskModel.fromJson((resp.data as Map).cast<String, dynamic>());
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  Future<List<TaskModel>> getTasks({String? status, DateTime? date}) async {
    try {
      final resp = await _dio.get('/tasks', queryParameters: {
        if (status != null) 'status': status,
        if (date != null) 'start_due': date.toIso8601String(),
      });
      final list = (resp.data as List).cast<Map>();
      return list.map((e) => TaskModel.fromJson(e.cast<String, dynamic>())).toList();
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  Future<TaskModel> updateTask(String taskId, Map<String, dynamic> updates) async {
    try {
      final resp = await _dio.patch('/tasks/$taskId', data: updates);
      return TaskModel.fromJson((resp.data as Map).cast<String, dynamic>());
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  Future<void> deleteTask(String taskId) async {
    try {
      await _dio.delete('/tasks/$taskId');
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  // Fitness
  Future<FitnessLogModel> logFitness(Map<String, dynamic> logData) async {
    try {
      final resp = await _dio.post('/fitness/log', data: logData);
      return FitnessLogModel.fromJson((resp.data as Map).cast<String, dynamic>());
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  Future<List<FitnessLogModel>> getFitnessLogs({DateTime? startDate, DateTime? endDate}) async {
    try {
      final resp = await _dio.get('/fitness/logs', queryParameters: {
        if (startDate != null) 'start': startDate.toIso8601String(),
        if (endDate != null) 'end': endDate.toIso8601String(),
      });
      final list = (resp.data as List).cast<Map>();
      return list.map((e) => FitnessLogModel.fromJson(e.cast<String, dynamic>())).toList();
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  Future<Map<String, dynamic>> getFitnessStats({String period = 'daily'}) async {
    try {
      final resp = await _dio.get('/fitness/stats', queryParameters: {'period': period});
      return (resp.data as Map).cast<String, dynamic>();
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  // User
  Future<AppUser> getUserProfile() async {
    try {
      final resp = await _dio.get('/auth/me');
      return AppUser.fromJson((resp.data as Map).cast<String, dynamic>());
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  // Fitness edits/deletes (optional helpers for SummaryCard actions)
  Future<void> deleteFitnessLog(String logId) async {
    try {
      await _dio.delete('/fitness/$logId');
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  Future<FitnessLogModel> updateFitnessLog(String logId, Map<String, dynamic> updates) async {
    try {
      final resp = await _dio.patch('/fitness/$logId', data: updates);
      return FitnessLogModel.fromJson((resp.data as Map).cast<String, dynamic>());
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  Future<AppUser> updateUserProfile(Map<String, dynamic> updates) async {
    try {
      final resp = await _dio.patch('/users/${_authProvider.currentUser?.uid}', data: updates);
      return AppUser.fromJson((resp.data as Map).cast<String, dynamic>());
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  // Generic GET method for custom endpoints
  Future<dynamic> get(String path) async {
    try {
      final resp = await _dio.get(path);
      if (resp.data == null) return {};
      // Return data as-is (can be Map, List, or other types)
      return resp.data;
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  // Generic DELETE method for custom endpoints
  Future<Map<String, dynamic>> delete(String path) async {
    print('🔴 [API SERVICE] DELETE $path');
    try {
      print('🔴 [API SERVICE] Calling _dio.delete...');
      final resp = await _dio.delete(path);
      print('✅ [API SERVICE] DELETE Response status: ${resp.statusCode}');
      print('✅ [API SERVICE] DELETE Response data: ${resp.data}');
      
      if (resp.data is Map) {
        return (resp.data as Map).cast<String, dynamic>();
      } else {
        print('❌ [API SERVICE] Invalid response format: ${resp.data}');
        throw ApiException('Invalid response format');
      }
    } on DioException catch (e) {
      print('❌ [API SERVICE] DELETE DioException: ${e.type}');
      print('❌ [API SERVICE] DELETE Message: ${e.message}');
      print('❌ [API SERVICE] DELETE Response: ${e.response?.data}');
      print('❌ [API SERVICE] DELETE Status: ${e.response?.statusCode}');
      _handleDioError(e); 
      rethrow; 
    } catch (e, stackTrace) {
      print('❌ [API SERVICE] DELETE Exception: $e');
      print('❌ [API SERVICE] DELETE Stack trace: $stackTrace');
      throw ApiException('Failed to parse response: $e');
    }
  }

  // Generic POST method for custom endpoints
  Future<Map<String, dynamic>> post(String path, Map<String, dynamic> data) async {
    print('🔵 [API SERVICE] POST $path');
    print('🔵 [API SERVICE] Data: $data');
    
    try {
      print('🔵 [API SERVICE] Calling _dio.post...');
      final resp = await _dio.post(path, data: data);
      print('✅ [API SERVICE] Response status: ${resp.statusCode}');
      print('✅ [API SERVICE] Response data type: ${resp.data.runtimeType}');
      
      if (resp.data is Map) {
        return (resp.data as Map).cast<String, dynamic>();
      } else {
        print('❌ [API SERVICE] Invalid response format: ${resp.data}');
        throw ApiException('Invalid response format');
      }
    } on DioException catch (e) {
      print('❌ [API SERVICE] DioException: ${e.type}');
      print('❌ [API SERVICE] Message: ${e.message}');
      print('❌ [API SERVICE] Response: ${e.response?.data}');
      _handleDioError(e); 
      rethrow; 
    } catch (e, stackTrace) {
      print('❌ [API SERVICE] Exception: $e');
      print('❌ [API SERVICE] Stack trace: $stackTrace');
      throw ApiException('Failed to parse response: $e');
    }
  }

  // Generic PUT method for custom endpoints
  Future<Map<String, dynamic>> put(String path, Map<String, dynamic> data) async {
    try {
      final resp = await _dio.put(path, data: data);
      if (resp.data is Map) {
        return (resp.data as Map).cast<String, dynamic>();
      } else {
        throw ApiException('Invalid response format');
      }
    } on DioException catch (e) { 
      _handleDioError(e); 
      rethrow; 
    } catch (e) {
      throw ApiException('Failed to parse response: $e');
    }
  }

  // Timeline - Unified activity feed
  Future<TimelineResponse> getTimeline({
    String? types,
    String? startDate,
    String? endDate,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final resp = await _dio.get('/timeline', queryParameters: {
        if (types != null && types.isNotEmpty) 'types': types,
        if (startDate != null) 'start_date': startDate,
        if (endDate != null) 'end_date': endDate,
        'limit': limit,
        'offset': offset,
      });
      return TimelineResponse.fromJson((resp.data as Map).cast<String, dynamic>());
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  Future<Map<String, dynamic>> getTimelineStats({
    String? startDate,
    String? endDate,
  }) async {
    try {
      final resp = await _dio.get('/timeline/stats', queryParameters: {
        if (startDate != null) 'start_date': startDate,
        if (endDate != null) 'end_date': endDate,
      });
      return (resp.data as Map).cast<String, dynamic>();
    } on DioException catch (e) { _handleDioError(e); rethrow; }
  }

  /// Get feedback analytics summary for current user
  /// Phase 1: Analytics Dashboard
  Future<Map<String, dynamic>> getFeedbackSummary() async {
    debugPrint('🔵 [API SERVICE] GET /analytics/feedback-summary');
    
    try {
      final response = await _dio.get('/analytics/feedback-summary');
      
      debugPrint('✅ [API SERVICE] Response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      } else if (response.statusCode == 404) {
        // Feature not enabled
        debugPrint('⚠️ [API SERVICE] Analytics feature not enabled');
        throw Exception('Analytics feature not available');
      } else {
        throw Exception('Failed to fetch feedback summary');
      }
    } catch (e) {
      debugPrint('❌ [API SERVICE] Error: $e');
      rethrow;
    }
  }

  Never _handleDioError(DioException e) {
    final status = e.response?.statusCode;
    final data = e.response?.data;
    if (status == 400) throw ValidationException(data is Map ? (data['detail']?.toString() ?? 'Validation error') : 'Validation error');
    if (status == 401) throw AuthException('Unauthorized');
    if (e.type == DioExceptionType.connectionTimeout || e.type == DioExceptionType.receiveTimeout) {
      throw NetworkException('Network timeout');
    }
    throw ApiException(data is Map ? (data['detail']?.toString() ?? 'API error') : 'API error');
  }
}


