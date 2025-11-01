import 'dart:developer' as dev;
import 'package:flutter/foundation.dart';

import 'package:dio/dio.dart';

import '../models/fitness_log.dart';
import '../models/task.dart';
import '../models/user.dart';
import '../providers/auth_provider.dart';
import '../utils/constants.dart';

class ApiException implements Exception { final String message; ApiException(this.message); }
class NetworkException implements Exception { final String message; NetworkException(this.message); }
class AuthException implements Exception { final String message; AuthException(this.message); }
class ValidationException implements Exception { final String message; ValidationException(this.message); }

class ApiService {
  final Dio _dio;
  final AuthProvider _authProvider;
  final VoidCallback? onUnauthorized;
  ApiService(this._authProvider, { this.onUnauthorized })
      : _dio = Dio(BaseOptions(
          baseUrl: AppConstants.apiBaseUrl,
          connectTimeout: const Duration(seconds: 12),
          receiveTimeout: const Duration(seconds: 25),
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


