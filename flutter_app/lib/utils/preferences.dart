import 'package:shared_preferences/shared_preferences.dart';

/// User preferences manager for app settings
class AppPreferences {
  static const String _keyHomeScreenVariant = 'home_screen_variant';

  /// Get the selected home screen variant
  /// Returns 'v1', 'v2', or 'v3' (defaults to 'v2')
  static Future<String> getHomeScreenVariant() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyHomeScreenVariant) ?? 'v2';
  }

  /// Set the selected home screen variant
  static Future<void> setHomeScreenVariant(String variant) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyHomeScreenVariant, variant);
  }
}


