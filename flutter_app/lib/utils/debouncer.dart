import 'dart:async';
import 'package:flutter/material.dart';

/// Debouncer - Delays function execution until after wait time
/// Useful for search inputs, API calls, etc.
/// 
/// Example:
/// ```dart
/// final debouncer = Debouncer(milliseconds: 300);
/// debouncer.run(() => searchAPI(query));
/// ```
class Debouncer {
  final int milliseconds;
  Timer? _timer;
  
  Debouncer({required this.milliseconds});
  
  /// Run action after debounce delay
  void run(VoidCallback action) {
    _timer?.cancel();
    _timer = Timer(Duration(milliseconds: milliseconds), action);
  }
  
  /// Cancel pending action
  void cancel() {
    _timer?.cancel();
  }
  
  /// Dispose and cancel timer
  void dispose() {
    _timer?.cancel();
  }
  
  /// Check if timer is active
  bool get isActive => _timer?.isActive ?? false;
}

/// Throttler - Ensures function executes at most once per time period
/// Useful for scroll events, resize events, etc.
/// 
/// Example:
/// ```dart
/// final throttler = Throttler(milliseconds: 1000);
/// throttler.run(() => updateUI());
/// ```
class Throttler {
  final int milliseconds;
  Timer? _timer;
  DateTime? _lastExecuted;
  
  Throttler({required this.milliseconds});
  
  /// Run action if enough time has passed
  void run(VoidCallback action) {
    final now = DateTime.now();
    
    if (_lastExecuted == null || 
        now.difference(_lastExecuted!) > Duration(milliseconds: milliseconds)) {
      _lastExecuted = now;
      action();
    }
  }
  
  /// Dispose and cancel timer
  void dispose() {
    _timer?.cancel();
  }
}


