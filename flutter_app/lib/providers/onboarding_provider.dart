import 'package:flutter/material.dart';
import '../models/user_profile.dart';

/// Manages onboarding flow state and data collection
class OnboardingProvider extends ChangeNotifier {
  // Step 1: Basic Info
  String? name;
  Gender? gender;
  int? age;
  int? heightCm;
  double? weightKg;

  // Step 2: Activity Level
  ActivityLevel? activityLevel;

  // Step 3: Fitness Goal
  FitnessGoal? fitnessGoal;
  double? targetWeightKg;

  // Step 4: Calculated Goals (from API)
  Map<String, dynamic>? calculatedGoals;
  DailyGoals? customGoals; // If user edits recommendations

  // Step 5: Preferences
  DietPreference dietPreference = DietPreference.none;
  List<String> allergies = [];
  List<String> dislikedFoods = [];

  // Current step (0-6)
  int _currentStep = 0;
  int get currentStep => _currentStep;

  // Validation flags
  bool get isStep1Valid =>
      name != null &&
      name!.isNotEmpty &&
      gender != null &&
      age != null &&
      age! >= 13 &&
      age! <= 120 &&
      heightCm != null &&
      heightCm! >= 100 &&
      heightCm! <= 250 &&
      weightKg != null &&
      weightKg! >= 30 &&
      weightKg! <= 300;

  bool get isStep2Valid => activityLevel != null;
  bool get isStep3Valid => fitnessGoal != null;
  bool get isStep4Valid => calculatedGoals != null || customGoals != null;
  bool get isStep5Valid => true; // Preferences are optional

  /// Move to next step
  void nextStep() {
    if (_currentStep < 6) {
      _currentStep++;
      notifyListeners();
    }
  }

  /// Move to previous step
  void previousStep() {
    if (_currentStep > 0) {
      _currentStep--;
      notifyListeners();
    }
  }

  /// Jump to specific step
  void goToStep(int step) {
    if (step >= 0 && step <= 6) {
      _currentStep = step;
      notifyListeners();
    }
  }

  /// Update basic info
  void updateBasicInfo({
    String? name,
    Gender? gender,
    int? age,
    int? heightCm,
    double? weightKg,
  }) {
    if (name != null) this.name = name;
    if (gender != null) this.gender = gender;
    if (age != null) this.age = age;
    if (heightCm != null) this.heightCm = heightCm;
    if (weightKg != null) this.weightKg = weightKg;
    notifyListeners();
  }

  /// Update activity level
  void updateActivityLevel(ActivityLevel level) {
    activityLevel = level;
    notifyListeners();
  }

  /// Update fitness goal
  void updateFitnessGoal(FitnessGoal goal, {double? targetWeight}) {
    fitnessGoal = goal;
    targetWeightKg = targetWeight;
    notifyListeners();
  }

  /// Update target weight separately
  void updateTargetWeight(double? weight) {
    targetWeightKg = weight;
    notifyListeners();
  }

  /// Store calculated goals from API
  void setCalculatedGoals(Map<String, dynamic> goals) {
    calculatedGoals = goals;
    notifyListeners();
  }

  /// Update custom goals (if user edits)
  void updateCustomGoals(DailyGoals goals) {
    customGoals = goals;
    notifyListeners();
  }

  /// Update preferences
  void updatePreferences({
    DietPreference? diet,
    List<String>? allergies,
    List<String>? dislikedFoods,
  }) {
    if (diet != null) dietPreference = diet;
    if (allergies != null) this.allergies = allergies;
    if (dislikedFoods != null) this.dislikedFoods = dislikedFoods;
    notifyListeners();
  }

  /// Add allergy
  void addAllergy(String allergy) {
    if (!allergies.contains(allergy)) {
      allergies.add(allergy);
      notifyListeners();
    }
  }

  /// Remove allergy
  void removeAllergy(String allergy) {
    allergies.remove(allergy);
    notifyListeners();
  }

  /// Add disliked food
  void addDislikedFood(String food) {
    if (!dislikedFoods.contains(food)) {
      dislikedFoods.add(food);
      notifyListeners();
    }
  }

  /// Remove disliked food
  void removeDislikedFood(String food) {
    dislikedFoods.remove(food);
    notifyListeners();
  }

  /// Get final goals (custom or calculated)
  DailyGoals? getFinalGoals() {
    if (customGoals != null) return customGoals;
    if (calculatedGoals != null && calculatedGoals!['recommended_goals'] != null) {
      return DailyGoals.fromJson(calculatedGoals!['recommended_goals']);
    }
    return null;
  }

  /// Reset all data
  void reset() {
    name = null;
    gender = null;
    age = null;
    heightCm = null;
    weightKg = null;
    activityLevel = null;
    fitnessGoal = null;
    targetWeightKg = null;
    calculatedGoals = null;
    customGoals = null;
    dietPreference = DietPreference.none;
    allergies = [];
    dislikedFoods = [];
    _currentStep = 0;
    notifyListeners();
  }

  /// Get progress percentage (0.0 to 1.0)
  double get progress => (_currentStep + 1) / 7;

  /// Get step title
  String get stepTitle {
    switch (_currentStep) {
      case 0:
        return 'Tell us about yourself';
      case 1:
        return 'How active are you?';
      case 2:
        return 'What\'s your goal?';
      case 3:
        return 'Your personalized plan';
      case 4:
        return 'Diet preferences';
      case 5:
        return 'Review & confirm';
      case 6:
        return 'You\'re all set!';
      default:
        return '';
    }
  }

  /// Get step number display (e.g., "1/7")
  String get stepDisplay => '${_currentStep + 1}/7';
}


