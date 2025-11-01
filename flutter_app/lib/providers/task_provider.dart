import 'package:flutter/material.dart';

import '../models/task.dart';
import '../services/notification_service.dart';

class TaskProvider extends ChangeNotifier {
  final List<TaskModel> _tasks = [];
  List<TaskModel> get tasks => List.unmodifiable(_tasks);

  void add(TaskModel task) {
    _tasks.add(task);
    notifyListeners();
    if (task.dueDate != null) {
      NotificationService.instance.scheduleReminder(
        when: task.dueDate!,
        title: 'Task due',
        body: task.title,
      );
    }
  }

  void removeById(String id) {
    _tasks.removeWhere((t) => t.id == id);
    notifyListeners();
  }

  void toggleComplete(String id) {
    final i = _tasks.indexWhere((t) => t.id == id);
    if (i >= 0) {
      final t = _tasks[i];
      _tasks[i] = TaskModel(
        id: t.id,
        userId: t.userId,
        title: t.title,
        description: t.description,
        dueDate: t.dueDate,
        priority: t.priority,
        status: t.status == TaskStatus.completed ? TaskStatus.pending : TaskStatus.completed,
        createdAt: t.createdAt,
        updatedAt: DateTime.now(),
      );
      notifyListeners();
    }
  }
}


