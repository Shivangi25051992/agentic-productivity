import 'package:flutter/foundation.dart';
import '../utils/preferences.dart';

/// Provider to manage home screen variant selection
/// Allows instant switching without app restart
class HomeVariantProvider extends ChangeNotifier {
  String _variant = 'v2'; // Default to Hybrid

  String get variant => _variant;

  /// Load the saved variant from preferences
  Future<void> loadVariant() async {
    _variant = await AppPreferences.getHomeScreenVariant();
    notifyListeners();
  }

  /// Set a new variant and save to preferences
  Future<void> setVariant(String newVariant) async {
    if (_variant != newVariant) {
      _variant = newVariant;
      await AppPreferences.setHomeScreenVariant(newVariant);
      notifyListeners();
    }
  }
}

