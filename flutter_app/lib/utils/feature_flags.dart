/// Feature Flags Configuration
/// 
/// Centralized feature flag management for gradual rollout and A/B testing.
/// All new features should be behind a feature flag for safe deployment.
class FeatureFlags {
  // 🚀 PHASE 1: Performance & Scale Features
  
  /// Enable Redis caching (backend-side)
  /// Status: IMPLEMENTED (Task 8)
  /// Default: true (production-ready)
  static const bool redisCacheEnabled = true;
  
  /// Enable real-time Firestore snapshots (frontend-side)
  /// Status: DISABLED - Using simple pull-to-refresh instead (more reliable)
  /// Default: false (SIMPLE APPROACH)
  static const bool realtimeUpdatesEnabled = false;
  
  /// Enable optimistic UI updates
  /// Status: IMPLEMENTED
  /// Default: true (production-ready)
  static const bool optimisticUIEnabled = true;
  
  /// Enable client-side caching (5-min TTL)
  /// Status: IMPLEMENTED
  /// Default: true (production-ready)
  static const bool clientCacheEnabled = true;
  
  // 🔬 PHASE 2: Monitoring & Observability
  
  /// Enable Firebase Performance Monitoring
  /// Status: PENDING (Task 10)
  /// Default: false (needs setup)
  static const bool performanceMonitoringEnabled = false;
  
  /// Enable Sentry error tracking
  /// Status: PENDING (Task 10)
  /// Default: false (needs setup)
  static const bool sentryEnabled = false;
  
  /// Enable custom analytics events
  /// Status: PENDING
  /// Default: false
  static const bool customAnalyticsEnabled = false;
  
  // 🎨 UX Features
  
  /// Enable home screen variant selector
  /// Status: IMPLEMENTED
  /// Default: true
  static const bool homeVariantSelectorEnabled = true;
  
  /// Enable radial quick actions menu
  /// Status: IMPLEMENTED
  /// Default: true
  static const bool radialMenuEnabled = true;
  
  /// Enable prompt pills rotation
  /// Status: IMPLEMENTED
  /// Default: true
  static const bool promptPillsEnabled = true;
  
  // 🧪 Experimental Features
  
  /// Enable AI-powered meal suggestions
  /// Status: PENDING
  /// Default: false
  static const bool aiMealSuggestionsEnabled = false;
  
  /// Enable voice input for chat
  /// Status: PENDING
  /// Default: false
  static const bool voiceInputEnabled = false;
  
  /// Enable offline mode
  /// Status: PENDING
  /// Default: false
  static const bool offlineModeEnabled = false;
  
  // 🔧 Debug Features
  
  /// Enable debug logging
  /// Status: ALWAYS AVAILABLE
  /// Default: true in debug mode, false in release
  static bool get debugLoggingEnabled => const bool.fromEnvironment('dart.vm.product') == false;
  
  /// Enable performance overlay
  /// Status: ALWAYS AVAILABLE
  /// Default: false
  static const bool performanceOverlayEnabled = false;
  
  // 📊 A/B Testing
  
  /// A/B test: Fast-path vs LLM for food logging
  /// Status: IMPLEMENTED
  /// Default: 'fast_path' (80% of users)
  static const String foodLoggingStrategy = 'fast_path'; // 'fast_path' | 'llm' | 'hybrid'
  
  /// A/B test: Home screen variant
  /// Status: IMPLEMENTED
  /// Default: 'v6' (Enhanced)
  static const String defaultHomeVariant = 'v6'; // 'v1' | 'v2' | 'v3' | 'v4' | 'v5' | 'v6'
  
  // 🔐 Safety Features
  
  /// Enable rate limiting for API calls
  /// Status: PENDING
  /// Default: false
  static const bool rateLimitingEnabled = false;
  
  /// Enable request retry logic
  /// Status: IMPLEMENTED
  /// Default: true
  static const bool requestRetryEnabled = true;
  
  /// Maximum retry attempts
  static const int maxRetryAttempts = 3;
  
  // 📱 Platform-Specific Features
  
  /// Enable iOS-specific home screen variants
  /// Status: IMPLEMENTED
  /// Default: true
  static const bool iosHomeVariantsEnabled = true;
  
  /// Enable haptic feedback
  /// Status: IMPLEMENTED
  /// Default: true
  static const bool hapticFeedbackEnabled = true;
  
  // 🚀 Performance Thresholds
  
  /// Cache TTL (in minutes)
  static const int cacheTTLMinutes = 5;
  
  /// API timeout (in seconds)
  static const int apiTimeoutSeconds = 30;
  
  /// Image cache size (in MB)
  static const int imageCacheSizeMB = 100;
  
  // 📝 Feature Flag Helper Methods
  
  /// Check if a feature is enabled
  static bool isEnabled(String featureName) {
    switch (featureName) {
      case 'redis_cache':
        return redisCacheEnabled;
      case 'realtime_updates':
        return realtimeUpdatesEnabled;
      case 'optimistic_ui':
        return optimisticUIEnabled;
      case 'client_cache':
        return clientCacheEnabled;
      case 'performance_monitoring':
        return performanceMonitoringEnabled;
      case 'sentry':
        return sentryEnabled;
      case 'custom_analytics':
        return customAnalyticsEnabled;
      case 'home_variant_selector':
        return homeVariantSelectorEnabled;
      case 'radial_menu':
        return radialMenuEnabled;
      case 'prompt_pills':
        return promptPillsEnabled;
      case 'ai_meal_suggestions':
        return aiMealSuggestionsEnabled;
      case 'voice_input':
        return voiceInputEnabled;
      case 'offline_mode':
        return offlineModeEnabled;
      case 'debug_logging':
        return debugLoggingEnabled;
      case 'performance_overlay':
        return performanceOverlayEnabled;
      case 'rate_limiting':
        return rateLimitingEnabled;
      case 'request_retry':
        return requestRetryEnabled;
      case 'ios_home_variants':
        return iosHomeVariantsEnabled;
      case 'haptic_feedback':
        return hapticFeedbackEnabled;
      default:
        return false;
    }
  }
  
  /// Get all enabled features (for debugging)
  static Map<String, bool> getAllFeatures() {
    return {
      'redis_cache': redisCacheEnabled,
      'realtime_updates': realtimeUpdatesEnabled,
      'optimistic_ui': optimisticUIEnabled,
      'client_cache': clientCacheEnabled,
      'performance_monitoring': performanceMonitoringEnabled,
      'sentry': sentryEnabled,
      'custom_analytics': customAnalyticsEnabled,
      'home_variant_selector': homeVariantSelectorEnabled,
      'radial_menu': radialMenuEnabled,
      'prompt_pills': promptPillsEnabled,
      'ai_meal_suggestions': aiMealSuggestionsEnabled,
      'voice_input': voiceInputEnabled,
      'offline_mode': offlineModeEnabled,
      'debug_logging': debugLoggingEnabled,
      'performance_overlay': performanceOverlayEnabled,
      'rate_limiting': rateLimitingEnabled,
      'request_retry': requestRetryEnabled,
      'ios_home_variants': iosHomeVariantsEnabled,
      'haptic_feedback': hapticFeedbackEnabled,
    };
  }
  
  /// Print all feature flags (for debugging)
  static void printAllFeatures() {
    print('🚩 Feature Flags:');
    getAllFeatures().forEach((key, value) {
      final status = value ? '✅' : '❌';
      print('   $status $key: $value');
    });
  }
}

