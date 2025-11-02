import 'package:flutter/material.dart';

class NotificationProvider extends ChangeNotifier {
  bool enabled = true;
  TimeOfDay? dndStart;
  TimeOfDay? dndEnd;

  void toggle(bool value) { enabled = value; notifyListeners(); }
  void setDnd({TimeOfDay? start, TimeOfDay? end}) { dndStart = start; dndEnd = end; notifyListeners(); }
}







