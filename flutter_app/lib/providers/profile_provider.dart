import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

import '../models/user_profile.dart';
import '../utils/constants.dart';
import 'auth_provider.dart';

class ProfileProvider extends ChangeNotifier {
  UserProfileModel? _profile;
  bool _isLoading = false;
  String? _errorMessage;

  UserProfileModel? get profile => _profile;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get hasProfile => _profile != null && _profile!.onboardingCompleted;

  /// Complete onboarding and create profile
  Future<bool> completeOnboarding({
    required String name,
    required Gender gender,
    required int age,
    required int heightCm,
    required double weightKg,
    required ActivityLevel activityLevel,
    required FitnessGoal fitnessGoal,
    double? targetWeightKg,
    DietPreference dietPreference = DietPreference.none,
    List<String> allergies = const [],
    List<String> dislikedFoods = const [],
    required AuthProvider authProvider,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final token = await authProvider.getIdToken();
      if (token == null) {
        throw Exception('Not authenticated');
      }

      // Detect user's timezone
      final timezone = DateTime.now().timeZoneName;
      
      final response = await http.post(
        Uri.parse('${AppConstants.apiBaseUrl}/profile/onboard'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'name': name,
          'gender': _genderToApi(gender),
          'age': age,
          'height_cm': heightCm,
          'weight_kg': weightKg,
          'activity_level': _activityLevelToApi(activityLevel),
          'fitness_goal': _fitnessGoalToApi(fitnessGoal),
          if (targetWeightKg != null) 'target_weight_kg': targetWeightKg,
          'diet_preference': _dietPreferenceToApi(dietPreference),
          'allergies': allergies,
          'disliked_foods': dislikedFoods,
          'timezone': timezone,  // Auto-detect timezone
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _profile = UserProfileModel.fromJson(data['profile']);
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _errorMessage = 'Failed to create profile: ${response.body}';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Fetch user profile
  Future<void> fetchProfile(AuthProvider authProvider) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final token = await authProvider.getIdToken();
      if (token == null) {
        throw Exception('Not authenticated');
      }

      final response = await http.get(
        Uri.parse('${AppConstants.apiBaseUrl}/profile/me'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _profile = UserProfileModel.fromJson(data['profile']);
      } else if (response.statusCode == 404) {
        // Profile not found - user needs to complete onboarding
        _profile = null;
      } else {
        _errorMessage = 'Failed to fetch profile: ${response.body}';
      }
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Update profile
  Future<bool> updateProfile({
    String? name,
    double? weightKg,
    ActivityLevel? activityLevel,
    FitnessGoal? fitnessGoal,
    double? targetWeightKg,
    DietPreference? dietPreference,
    List<String>? allergies,
    List<String>? dislikedFoods,
    required AuthProvider authProvider,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final token = await authProvider.getIdToken();
      if (token == null) {
        throw Exception('Not authenticated');
      }

      final body = <String, dynamic>{};
      if (name != null) body['name'] = name;
      if (weightKg != null) body['weight_kg'] = weightKg;
      if (activityLevel != null) body['activity_level'] = _activityLevelToApi(activityLevel);
      if (fitnessGoal != null) body['fitness_goal'] = _fitnessGoalToApi(fitnessGoal);
      if (targetWeightKg != null) body['target_weight_kg'] = targetWeightKg;
      if (dietPreference != null) body['diet_preference'] = _dietPreferenceToApi(dietPreference);
      if (allergies != null) body['allergies'] = allergies;
      if (dislikedFoods != null) body['disliked_foods'] = dislikedFoods;

      final response = await http.put(
        Uri.parse('${AppConstants.apiBaseUrl}/profile/me'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _profile = UserProfileModel.fromJson(data['profile']);
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _errorMessage = 'Failed to update profile: ${response.body}';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Calculate recommended goals (without saving)
  Future<Map<String, dynamic>?> calculateGoals({
    required Gender gender,
    required int age,
    required int heightCm,
    required double weightKg,
    required ActivityLevel activityLevel,
    required FitnessGoal fitnessGoal,
    double? targetWeightKg,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('${AppConstants.apiBaseUrl}/profile/calculate-goals'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'gender': _genderToApi(gender),
          'age': age,
          'height_cm': heightCm,
          'weight_kg': weightKg,
          'activity_level': _activityLevelToApi(activityLevel),
          'fitness_goal': _fitnessGoalToApi(fitnessGoal),
          if (targetWeightKg != null) 'target_weight_kg': targetWeightKg,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  // Helper methods to convert enums to API format
  String _genderToApi(Gender gender) {
    return gender.name;
  }

  String _activityLevelToApi(ActivityLevel level) {
    switch (level) {
      case ActivityLevel.sedentary:
        return 'sedentary';
      case ActivityLevel.lightlyActive:
        return 'lightly_active';
      case ActivityLevel.moderatelyActive:
        return 'moderately_active';
      case ActivityLevel.veryActive:
        return 'very_active';
      case ActivityLevel.extremelyActive:
        return 'extremely_active';
    }
  }

  String _fitnessGoalToApi(FitnessGoal goal) {
    switch (goal) {
      case FitnessGoal.loseWeight:
        return 'lose_weight';
      case FitnessGoal.maintain:
        return 'maintain';
      case FitnessGoal.gainMuscle:
        return 'gain_muscle';
      case FitnessGoal.improveFitness:
        return 'improve_fitness';
    }
  }

  String _dietPreferenceToApi(DietPreference pref) {
    switch (pref) {
      case DietPreference.none:
        return 'none';
      case DietPreference.vegetarian:
        return 'vegetarian';
      case DietPreference.vegan:
        return 'vegan';
      case DietPreference.pescatarian:
        return 'pescatarian';
      case DietPreference.keto:
        return 'keto';
      case DietPreference.paleo:
        return 'paleo';
      case DietPreference.lowCarb:
        return 'low_carb';
      case DietPreference.highProtein:
        return 'high_protein';
    }
  }
}


