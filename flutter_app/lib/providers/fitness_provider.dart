import 'package:flutter/material.dart';

import '../models/fitness_log.dart';

class FitnessProvider extends ChangeNotifier {
  final List<FitnessLogModel> _logs = [];
  List<FitnessLogModel> get logs => List.unmodifiable(_logs);

  void add(FitnessLogModel log) {
    _logs.add(log);
    notifyListeners();
  }

  void removeById(String id) {
    _logs.removeWhere((l) => l.id == id);
    notifyListeners();
  }
}


