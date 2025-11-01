import 'package:flutter/material.dart';

/// Global constants for the Flutter app.
class AppConstants {
  /// Backend API base URL. Override via runtime config if needed.
  static const String apiBaseUrl = ApiEnv.apiBaseUrl;

  /// Color palette aligning with admin design system.
  static const Color primary = Color(0xFF20B2AA);
  static const Color bgLight = Color(0xFFFDFCF9);
  static const Color bgDark = Color(0xFF1F2937);
}

/// Compile-time API environment configuration.
class ApiEnv {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );
}

/// Common string constants.
class Strings {
  static const String appName = 'AI Productivity';
  static const String loginTitle = 'Welcome back';
  static const String signupTitle = 'Create your account';
}






