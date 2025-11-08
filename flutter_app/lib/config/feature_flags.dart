/// Feature Flags - Control feature availability
/// 
/// Benefits:
/// - Enable/disable features without code changes
/// - A/B testing capability
/// - Gradual rollout
/// - Quick rollback if issues found
/// 
/// Future: Integrate with Firebase Remote Config for dynamic flags
class FeatureFlags {
  // Tier 1: Super Quick Wins
  static const bool enableProfileEdit = true;
  static const bool enableCalorieInfo = true;
  static const bool enableEmptyStateCTAs = true;
  static const bool enableWorkoutCalories = true;
  
  // Tier 2: Quick Wins
  static const bool enableWaterGoalCustomization = true;
  static const bool enableMacroRings = true;
  static const bool enableFoodSearch = true;
  static const bool enableFavorites = true;
  static const bool enableWorkoutDisplay = true;
  static const bool enableDateToggle = true;
  
  // Tier 3: Medium Wins
  static const bool enableChatUpdates = true;
  static const bool enableGoalTimeline = true;
  static const bool enableDarkMode = true;
  static const bool enableMealReminders = true;
  
  // Water & Supplement (Already deployed)
  static const bool enableWaterTracking = true;
  static const bool enableSupplementTracking = true;
  
  // Future features (disabled by default)
  static const bool enableSleepTracking = false;
  static const bool enableMealPlanning = false;
  static const bool enableIntermittentFasting = false;
  static const bool enablePhotoLogging = false;
  static const bool enableBarcodeScanner = false;
  static const bool enableSocialFeatures = false;
  
  // Performance features
  static const bool enableCaching = true;
  static const bool enableOfflineMode = false;
  static const bool enableAnalytics = true;
  
  // Debug features (only in development)
  static const bool enableDebugMode = false;
  static const bool enablePerformanceMonitoring = true;
  
  /// Check if a feature is enabled
  static bool isEnabled(String featureName) {
    switch (featureName) {
      // Tier 1
      case 'profile_edit':
        return enableProfileEdit;
      case 'calorie_info':
        return enableCalorieInfo;
      case 'empty_state_ctas':
        return enableEmptyStateCTAs;
      case 'workout_calories':
        return enableWorkoutCalories;
      
      // Tier 2
      case 'water_goal_customization':
        return enableWaterGoalCustomization;
      case 'macro_rings':
        return enableMacroRings;
      case 'food_search':
        return enableFoodSearch;
      case 'favorites':
        return enableFavorites;
      case 'workout_display':
        return enableWorkoutDisplay;
      case 'date_toggle':
        return enableDateToggle;
      
      // Tier 3
      case 'chat_updates':
        return enableChatUpdates;
      case 'goal_timeline':
        return enableGoalTimeline;
      case 'dark_mode':
        return enableDarkMode;
      case 'meal_reminders':
        return enableMealReminders;
      
      // Already deployed
      case 'water_tracking':
        return enableWaterTracking;
      case 'supplement_tracking':
        return enableSupplementTracking;
      
      default:
        return false;
    }
  }
  
  /// Get all enabled features
  static List<String> getEnabledFeatures() {
    return [
      if (enableProfileEdit) 'profile_edit',
      if (enableCalorieInfo) 'calorie_info',
      if (enableEmptyStateCTAs) 'empty_state_ctas',
      if (enableWorkoutCalories) 'workout_calories',
      if (enableWaterGoalCustomization) 'water_goal_customization',
      if (enableMacroRings) 'macro_rings',
      if (enableFoodSearch) 'food_search',
      if (enableFavorites) 'favorites',
      if (enableWorkoutDisplay) 'workout_display',
      if (enableDateToggle) 'date_toggle',
      if (enableChatUpdates) 'chat_updates',
      if (enableGoalTimeline) 'goal_timeline',
      if (enableDarkMode) 'dark_mode',
      if (enableMealReminders) 'meal_reminders',
      if (enableWaterTracking) 'water_tracking',
      if (enableSupplementTracking) 'supplement_tracking',
    ];
  }
  
  /// Future: Load from Firebase Remote Config
  static Future<void> loadRemoteConfig() async {
    // TODO: Implement Firebase Remote Config integration
    // This allows changing feature flags without app update
    // 
    // Example:
    // final remoteConfig = FirebaseRemoteConfig.instance;
    // await remoteConfig.fetchAndActivate();
    // enableMacroRings = remoteConfig.getBool('enable_macro_rings');
  }
}


