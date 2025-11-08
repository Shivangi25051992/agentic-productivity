import 'package:flutter/material.dart';
import '../config/environment_config.dart';

/// Global constants for the Flutter app.
class AppConstants {
  /// App version for cache busting
  static const String appVersion = '1.1.0'; // Update this on each deployment
  static const String buildNumber = '20251108'; // YYYYMMDD format
  
  /// Backend API base URL - uses EnvironmentConfig
  static String get apiBaseUrl => EnvironmentConfig.apiBaseUrl;

  /// Color palette aligning with admin design system.
  static const Color primary = Color(0xFF20B2AA);
  static const Color bgLight = Color(0xFFFDFCF9);
  static const Color bgDark = Color(0xFF1F2937);
  
  // ============================================================================
  // AI ASSISTANT PERSONALITY
  // ============================================================================
  
  /// AI Assistant Name (short, friendly)
  static const String aiName = 'Yuvi';
  
  /// AI Assistant Full Name
  static const String aiFullName = 'Yuviki';
  
  /// AI Assistant Emoji
  static const String aiEmoji = '🤖';
  
  // ============================================================================
  // AI ASSISTANT MESSAGES
  // ============================================================================
  
  /// Chat
  static const String aiChatTitle = 'Chat with $aiName';
  static const String aiTyping = '$aiName is typing...';
  static const String aiThinking = '$aiName is thinking...';
  static const String aiWelcome = "Hi! I'm $aiName, your personal AI health companion 👋";
  static const String aiAskAnything = 'Ask $aiName anything about your fitness journey';
  
  /// Insights
  static const String aiInsightsTitle = "$aiName's Insights";
  static const String aiAnalyzed = '$aiName analyzed your';
  static const String aiNoticed = '$aiName noticed';
  static const String aiSuggests = '$aiName suggests';
  static const String aiRecommends = '$aiName recommends';
  
  /// Meal Planning
  static const String aiMealPlanTitle = 'Let $aiName plan your meals';
  static const String aiGeneratingPlan = '$aiName is creating your personalized plan...';
  static const String aiPlanReady = '$aiName generated your plan! 🎉';
  
  /// Encouragement
  static const String aiProud = '$aiName is proud of your progress!';
  static const String aiGreatJob = 'Great job! $aiName noticed your consistency 🌟';
  static const String aiKeepGoing = 'Keep it up! $aiName believes in you 💪';
  
  /// Errors
  static const String aiError = "Oops! $aiName couldn't process that. Let's try again?";
  static const String aiNoData = "$aiName needs more data to provide insights. Keep logging!";
}

/// Compile-time API environment configuration.
class ApiEnv {
  /// Backend API base URL - automatically switches based on environment
  static String get apiBaseUrl => AppConstants.apiBaseUrl;
}

/// Common string constants.
class Strings {
  static const String appName = 'AI Productivity';
  static const String loginTitle = 'Welcome back';
  static const String signupTitle = 'Create your account';
}







