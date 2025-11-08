/// User Profile Model for Flutter
/// Matches backend UserProfile model
library;

enum Gender { male, female, other }

enum ActivityLevel {
  sedentary,
  lightlyActive,
  moderatelyActive,
  veryActive,
  extremelyActive
}

enum FitnessGoal { loseWeight, maintain, gainMuscle, improveFitness }

enum DietPreference {
  none,
  vegetarian,
  vegan,
  pescatarian,
  keto,
  paleo,
  lowCarb,
  highProtein
}

class DailyGoals {
  final int calories;
  final int proteinG;
  final int carbsG;
  final int fatG;
  final int fiberG;
  final int waterMl;
  final int steps;
  final int workoutsPerWeek;

  DailyGoals({
    required this.calories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    this.fiberG = 25,
    this.waterMl = 2000,
    this.steps = 10000,
    this.workoutsPerWeek = 3,
  });

  factory DailyGoals.fromJson(Map<String, dynamic> json) {
    return DailyGoals(
      calories: json['calories'] as int,
      proteinG: json['protein_g'] as int,
      carbsG: json['carbs_g'] as int,
      fatG: json['fat_g'] as int,
      fiberG: (json['fiber_g'] as int?) ?? 25,
      waterMl: (json['water_ml'] as int?) ?? 2000,
      steps: (json['steps'] as int?) ?? 10000,
      workoutsPerWeek: (json['workouts_per_week'] as int?) ?? 3,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'calories': calories,
      'protein_g': proteinG,
      'carbs_g': carbsG,
      'fat_g': fatG,
      'fiber_g': fiberG,
      'water_ml': waterMl,
      'steps': steps,
      'workouts_per_week': workoutsPerWeek,
    };
  }
}

class UserProfileModel {
  final String userId;
  final String name;
  final Gender gender;
  final int age;
  final int heightCm;
  final double weightKg;
  final ActivityLevel activityLevel;
  final FitnessGoal fitnessGoal;
  final double? targetWeightKg;
  final DailyGoals dailyGoals;
  final DietPreference dietPreference;
  final List<String> allergies;
  final List<String> dislikedFoods;
  final bool onboardingCompleted;
  final int currentStreak;
  final int totalDaysLogged;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String timezone;
  final String units;
  final String subscriptionTier;

  UserProfileModel({
    required this.userId,
    required this.name,
    required this.gender,
    required this.age,
    required this.heightCm,
    required this.weightKg,
    required this.activityLevel,
    required this.fitnessGoal,
    this.targetWeightKg,
    required this.dailyGoals,
    this.dietPreference = DietPreference.none,
    this.allergies = const [],
    this.dislikedFoods = const [],
    this.onboardingCompleted = false,
    this.currentStreak = 0,
    this.totalDaysLogged = 0,
    required this.createdAt,
    required this.updatedAt,
    this.timezone = 'UTC',
    this.units = 'metric',
    this.subscriptionTier = 'free',
  });

  factory UserProfileModel.fromJson(Map<String, dynamic> json) {
    return UserProfileModel(
      userId: json['user_id'] as String,
      name: json['name'] as String,
      gender: _genderFromString(json['gender'] as String),
      age: json['age'] as int,
      heightCm: json['height_cm'] as int,
      weightKg: (json['weight_kg'] as num).toDouble(),
      activityLevel: _activityLevelFromString(json['activity_level'] as String),
      fitnessGoal: _fitnessGoalFromString(json['fitness_goal'] as String),
      targetWeightKg: json['target_weight_kg'] != null
          ? (json['target_weight_kg'] as num).toDouble()
          : null,
      dailyGoals: DailyGoals.fromJson(json['daily_goals'] as Map<String, dynamic>),
      dietPreference: _dietPreferenceFromString(json['diet_preference'] as String? ?? 'none'),
      allergies: (json['allergies'] as List<dynamic>?)?.cast<String>() ?? [],
      dislikedFoods: (json['disliked_foods'] as List<dynamic>?)?.cast<String>() ?? [],
      onboardingCompleted: json['onboarding_completed'] as bool? ?? false,
      currentStreak: json['current_streak'] as int? ?? 0,
      totalDaysLogged: json['total_days_logged'] as int? ?? 0,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      timezone: json['timezone'] as String? ?? 'UTC',
      units: json['units'] as String? ?? 'metric',
      subscriptionTier: json['subscription_tier'] as String? ?? 'free',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'name': name,
      'gender': _genderToString(gender),
      'age': age,
      'height_cm': heightCm,
      'weight_kg': weightKg,
      'activity_level': _activityLevelToString(activityLevel),
      'fitness_goal': _fitnessGoalToString(fitnessGoal),
      'target_weight_kg': targetWeightKg,
      'daily_goals': dailyGoals.toJson(),
      'diet_preference': _dietPreferenceToString(dietPreference),
      'allergies': allergies,
      'disliked_foods': dislikedFoods,
      'onboarding_completed': onboardingCompleted,
      'current_streak': currentStreak,
      'total_days_logged': totalDaysLogged,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'timezone': timezone,
      'units': units,
      'subscription_tier': subscriptionTier,
    };
  }

  static Gender _genderFromString(String value) {
    switch (value.toLowerCase()) {
      case 'male':
        return Gender.male;
      case 'female':
        return Gender.female;
      default:
        return Gender.other;
    }
  }

  static String _genderToString(Gender gender) {
    return gender.name;
  }

  static ActivityLevel _activityLevelFromString(String value) {
    switch (value) {
      case 'sedentary':
        return ActivityLevel.sedentary;
      case 'lightly_active':
        return ActivityLevel.lightlyActive;
      case 'moderately_active':
        return ActivityLevel.moderatelyActive;
      case 'very_active':
        return ActivityLevel.veryActive;
      case 'extremely_active':
        return ActivityLevel.extremelyActive;
      default:
        return ActivityLevel.moderatelyActive;
    }
  }

  static String _activityLevelToString(ActivityLevel level) {
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

  static FitnessGoal _fitnessGoalFromString(String value) {
    switch (value) {
      case 'lose_weight':
        return FitnessGoal.loseWeight;
      case 'maintain':
        return FitnessGoal.maintain;
      case 'gain_muscle':
        return FitnessGoal.gainMuscle;
      case 'improve_fitness':
        return FitnessGoal.improveFitness;
      default:
        return FitnessGoal.maintain;
    }
  }

  static String _fitnessGoalToString(FitnessGoal goal) {
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

  static DietPreference _dietPreferenceFromString(String value) {
    switch (value) {
      case 'vegetarian':
        return DietPreference.vegetarian;
      case 'vegan':
        return DietPreference.vegan;
      case 'pescatarian':
        return DietPreference.pescatarian;
      case 'keto':
        return DietPreference.keto;
      case 'paleo':
        return DietPreference.paleo;
      case 'low_carb':
        return DietPreference.lowCarb;
      case 'high_protein':
        return DietPreference.highProtein;
      default:
        return DietPreference.none;
    }
  }

  static String _dietPreferenceToString(DietPreference pref) {
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

// Helper extensions for UI display
extension GenderExtension on Gender {
  String get displayName {
    switch (this) {
      case Gender.male:
        return 'Male';
      case Gender.female:
        return 'Female';
      case Gender.other:
        return 'Other';
    }
  }

  String get emoji {
    switch (this) {
      case Gender.male:
        return '👨';
      case Gender.female:
        return '👩';
      case Gender.other:
        return '🧑';
    }
  }
}

extension ActivityLevelExtension on ActivityLevel {
  String get displayName {
    switch (this) {
      case ActivityLevel.sedentary:
        return 'Sedentary';
      case ActivityLevel.lightlyActive:
        return 'Lightly Active';
      case ActivityLevel.moderatelyActive:
        return 'Moderately Active';
      case ActivityLevel.veryActive:
        return 'Very Active';
      case ActivityLevel.extremelyActive:
        return 'Extremely Active';
    }
  }

  String get description {
    switch (this) {
      case ActivityLevel.sedentary:
        return 'Little to no exercise';
      case ActivityLevel.lightlyActive:
        return '1-3 days/week';
      case ActivityLevel.moderatelyActive:
        return '3-5 days/week';
      case ActivityLevel.veryActive:
        return '6-7 days/week';
      case ActivityLevel.extremelyActive:
        return 'Athlete level';
    }
  }

  String get emoji {
    switch (this) {
      case ActivityLevel.sedentary:
        return '🪑';
      case ActivityLevel.lightlyActive:
        return '🚶';
      case ActivityLevel.moderatelyActive:
        return '🏃';
      case ActivityLevel.veryActive:
        return '💪';
      case ActivityLevel.extremelyActive:
        return '🏋️';
    }
  }
}

extension FitnessGoalExtension on FitnessGoal {
  String get displayName {
    switch (this) {
      case FitnessGoal.loseWeight:
        return 'Lose Weight';
      case FitnessGoal.maintain:
        return 'Maintain Weight';
      case FitnessGoal.gainMuscle:
        return 'Gain Muscle';
      case FitnessGoal.improveFitness:
        return 'Improve Fitness';
    }
  }

  String get description {
    switch (this) {
      case FitnessGoal.loseWeight:
        return 'Lose fat while preserving muscle';
      case FitnessGoal.maintain:
        return 'Stay at current weight';
      case FitnessGoal.gainMuscle:
        return 'Build muscle mass';
      case FitnessGoal.improveFitness:
        return 'Get healthier and stronger';
    }
  }

  String get emoji {
    switch (this) {
      case FitnessGoal.loseWeight:
        return '📉';
      case FitnessGoal.maintain:
        return '⚖️';
      case FitnessGoal.gainMuscle:
        return '💪';
      case FitnessGoal.improveFitness:
        return '🎯';
    }
  }
}

extension DietPreferenceExtension on DietPreference {
  String get displayName {
    switch (this) {
      case DietPreference.none:
        return 'No Preference';
      case DietPreference.vegetarian:
        return 'Vegetarian';
      case DietPreference.vegan:
        return 'Vegan';
      case DietPreference.pescatarian:
        return 'Pescatarian';
      case DietPreference.keto:
        return 'Keto';
      case DietPreference.paleo:
        return 'Paleo';
      case DietPreference.lowCarb:
        return 'Low Carb';
      case DietPreference.highProtein:
        return 'High Protein';
    }
  }
}






