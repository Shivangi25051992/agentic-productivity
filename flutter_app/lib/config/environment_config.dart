/// Environment Configuration Service
/// Follows 12-factor app principles for configuration management.
/// All configuration comes from environment variables or compile-time defines.
library;

import 'package:flutter/foundation.dart';

/// Deployment environments
enum Environment {
  development,
  staging,
  production,
}

/// Centralized environment configuration
/// 
/// Usage:
/// ```dart
/// // In main.dart
/// void main() {
///   EnvironmentConfig.validate();
///   runApp(MyApp());
/// }
/// 
/// // In services
/// final apiUrl = EnvironmentConfig.apiBaseUrl;
/// ```
class EnvironmentConfig {
  // Private constructor to prevent instantiation
  EnvironmentConfig._();

  // ============================================================================
  // COMPILE-TIME CONFIGURATION
  // ============================================================================

  /// Environment name (set via --dart-define=ENVIRONMENT=production)
  static const String _envKey = 'ENVIRONMENT';

  /// API base URL override (set via --dart-define=API_BASE_URL=https://...)
  static const String _apiUrlKey = 'API_BASE_URL';

  // ============================================================================
  // ENVIRONMENT DETECTION
  // ============================================================================

  /// Get current environment from compile-time define or debug mode
  static Environment get environment {
    const envString = String.fromEnvironment(_envKey, defaultValue: '');

    if (envString.isNotEmpty) {
      switch (envString.toLowerCase()) {
        case 'production':
          return Environment.production;
        case 'staging':
          return Environment.staging;
        case 'development':
          return Environment.development;
        default:
          throw Exception(
            'Invalid ENVIRONMENT value: $envString. '
            'Must be: development, staging, or production',
          );
      }
    }

    // Default: use debug mode to determine environment
    return kDebugMode ? Environment.development : Environment.production;
  }

  /// Check if running in production
  static bool get isProduction => environment == Environment.production;

  /// Check if running in development
  static bool get isDevelopment => environment == Environment.development;

  /// Check if running in staging
  static bool get isStaging => environment == Environment.staging;

  // ============================================================================
  // API CONFIGURATION
  // ============================================================================

  /// Get API base URL based on environment
  static String get apiBaseUrl {
    // 1. Check for explicit compile-time override
    const override = String.fromEnvironment(_apiUrlKey, defaultValue: '');
    if (override.isNotEmpty) {
      return override;
    }

    // 2. Use environment-specific defaults
    switch (environment) {
      case Environment.production:
        return _productionApiUrl;
      case Environment.staging:
        return _stagingApiUrl;
      case Environment.development:
        // In development, use localhost if in debug mode, otherwise production
        return kDebugMode ? _developmentApiUrl : _productionApiUrl;
    }
  }

  // ============================================================================
  // ENVIRONMENT-SPECIFIC URLS
  // ⚠️ IMPORTANT: Update these before deployment!
  // ============================================================================

  /// Development API URL (localhost)
  static const String _developmentApiUrl = 'http://localhost:8000';

  /// Staging API URL (not yet configured)
  static const String _stagingApiUrl = 'https://aiproductivity-backend-staging.run.app';

  /// Production API URL
  /// ✅ VERIFIED: Correct Cloud Run URL (retrieved 2025-11-08)
  static const String _productionApiUrl = 'https://aiproductivity-backend-rhwrraai2a-uc.a.run.app';

  // ============================================================================
  // FEATURE FLAGS
  // ============================================================================

  /// Enable debug logging
  static bool get enableDebugLogging => isDevelopment || isStaging;

  /// Enable performance monitoring
  static bool get enablePerformanceMonitoring => isProduction || isStaging;

  /// Enable error reporting (Sentry, Firebase Crashlytics, etc.)
  static bool get enableErrorReporting => isProduction;

  // ============================================================================
  // VALIDATION
  // ============================================================================

  /// Validate configuration on app startup
  /// Throws exception if configuration is invalid
  static void validate() {
    final errors = <String>[];

    // Check for placeholder URLs
    if (apiBaseUrl.contains('YOUR-') || apiBaseUrl.contains('TODO')) {
      errors.add(
        '❌ CRITICAL: API URL not configured!\n'
        '   Update _productionApiUrl in environment_config.dart',
      );
    }

    // Check for localhost in production
    if (isProduction && apiBaseUrl.contains('localhost')) {
      errors.add(
        '❌ CRITICAL: Production build pointing to localhost!\n'
        '   Current URL: $apiBaseUrl\n'
        '   Set --dart-define=API_BASE_URL=<production-url> or update _productionApiUrl',
      );
    }

    // Check for http in production (should be https)
    if (isProduction && apiBaseUrl.startsWith('http://')) {
      errors.add(
        '⚠️  WARNING: Production using HTTP instead of HTTPS!\n'
        '   Current URL: $apiBaseUrl',
      );
    }

    // If errors found, throw exception
    if (errors.isNotEmpty) {
      throw Exception(
        'Configuration validation failed:\n\n${errors.join('\n\n')}',
      );
    }

    // Log successful validation
    _logConfiguration();
  }

  /// Log current configuration (safe, no secrets)
  static void _logConfiguration() {
    if (kDebugMode) {
      print('=' * 60);
      print('🔧 FLUTTER CONFIGURATION');
      print('=' * 60);
      print('Environment:              $environment');
      print('API Base URL:             $apiBaseUrl');
      print('Debug Logging:            ${enableDebugLogging ? '✅ ENABLED' : '❌ DISABLED'}');
      print('Performance Monitoring:   ${enablePerformanceMonitoring ? '✅ ENABLED' : '❌ DISABLED'}');
      print('Error Reporting:          ${enableErrorReporting ? '✅ ENABLED' : '❌ DISABLED'}');
      print('=' * 60);
    }
  }

  /// Get configuration summary for debugging
  static Map<String, dynamic> getConfigSummary() {
    return {
      'environment': environment.name,
      'apiBaseUrl': apiBaseUrl,
      'isProduction': isProduction,
      'isDevelopment': isDevelopment,
      'isStaging': isStaging,
      'enableDebugLogging': enableDebugLogging,
      'enablePerformanceMonitoring': enablePerformanceMonitoring,
      'enableErrorReporting': enableErrorReporting,
    };
  }
}

