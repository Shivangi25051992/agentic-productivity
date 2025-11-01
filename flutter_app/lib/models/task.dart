enum TaskPriority { low, medium, high }
enum TaskStatus { pending, inProgress, completed, cancelled }

class TaskModel {
  final String id;
  final String userId;
  final String title;
  final String? description;
  final DateTime? dueDate;
  final TaskPriority priority;
  final TaskStatus status;
  final DateTime createdAt;
  final DateTime updatedAt;

  TaskModel({
    required this.id,
    required this.userId,
    required this.title,
    this.description,
    this.dueDate,
    this.priority = TaskPriority.medium,
    this.status = TaskStatus.pending,
    required this.createdAt,
    required this.updatedAt,
  });

  factory TaskModel.fromJson(Map<String, dynamic> json) => TaskModel(
        id: (json['task_id'] ?? json['id']) as String,
        userId: (json['user_id'] ?? json['userId']) as String,
        title: json['title'] as String,
        description: json['description'] as String?,
        dueDate: json['due_date'] != null ? DateTime.parse(json['due_date'] as String) : null,
        priority: _priorityFrom(json['priority'] as String?),
        status: _statusFrom(json['status'] as String?),
        createdAt: DateTime.parse((json['created_at'] ?? json['createdAt']) as String),
        updatedAt: DateTime.parse((json['updated_at'] ?? json['updatedAt']) as String),
      );

  Map<String, dynamic> toJson() => {
        'task_id': id,
        'user_id': userId,
        'title': title,
        'description': description,
        'due_date': dueDate?.toIso8601String(),
        'priority': priority.name,
        'status': _statusToApi(status),
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
      }..removeWhere((k, v) => v == null);

  static TaskPriority _priorityFrom(String? v) {
    switch ((v ?? 'medium').toLowerCase()) {
      case 'low':
        return TaskPriority.low;
      case 'high':
        return TaskPriority.high;
      default:
        return TaskPriority.medium;
    }
  }

  static TaskStatus _statusFrom(String? v) {
    switch ((v ?? 'pending').toLowerCase()) {
      case 'in_progress':
      case 'inprogress':
        return TaskStatus.inProgress;
      case 'completed':
        return TaskStatus.completed;
      case 'cancelled':
      case 'canceled':
        return TaskStatus.cancelled;
      default:
        return TaskStatus.pending;
    }
  }

  static String _statusToApi(TaskStatus s) {
    switch (s) {
      case TaskStatus.inProgress:
        return 'in_progress';
      case TaskStatus.completed:
        return 'completed';
      case TaskStatus.cancelled:
        return 'cancelled';
      case TaskStatus.pending:
      default:
        return 'pending';
    }
  }
}


