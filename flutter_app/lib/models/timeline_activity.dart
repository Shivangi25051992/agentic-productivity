class TimelineActivity {
  final String id;
  final String type; // meal, workout, task, event, water, supplement
  final String title;
  final DateTime timestamp;
  final String icon;
  final String color;
  final String status;
  final Map<String, dynamic> details;
  final DateTime? dueDate;
  final String? priority;

  TimelineActivity({
    required this.id,
    required this.type,
    required this.title,
    required this.timestamp,
    required this.icon,
    required this.color,
    required this.status,
    required this.details,
    this.dueDate,
    this.priority,
  });

  factory TimelineActivity.fromJson(Map<String, dynamic> json) {
    return TimelineActivity(
      id: json['id'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      icon: json['icon'] as String,
      color: json['color'] as String,
      status: json['status'] as String,
      details: Map<String, dynamic>.from(json['details'] as Map),
      dueDate: json['due_date'] != null ? DateTime.parse(json['due_date'] as String) : null,
      priority: json['priority'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'title': title,
      'timestamp': timestamp.toIso8601String(),
      'icon': icon,
      'color': color,
      'status': status,
      'details': details,
      if (dueDate != null) 'due_date': dueDate!.toIso8601String(),
      if (priority != null) 'priority': priority,
    };
  }

  /// Get icon data based on type
  String get iconName {
    switch (type) {
      case 'meal':
        return 'restaurant';
      case 'workout':
        return 'fitness_center';
      case 'task':
        return 'check_circle';
      case 'event':
        return 'event';
      case 'water':
        return 'water_drop';
      case 'supplement':
        return 'medication';
      default:
        return 'circle';
    }
  }

  /// Get display color
  String get displayColor {
    switch (type) {
      case 'meal':
        return '#4CAF50'; // Green
      case 'workout':
        return '#2196F3'; // Blue
      case 'task':
        return '#FF9800'; // Orange
      case 'event':
        return '#9C27B0'; // Purple
      case 'water':
        return '#00BCD4'; // Cyan
      case 'supplement':
        return '#E91E63'; // Pink
      default:
        return '#9E9E9E'; // Grey
    }
  }

  /// Get summary text for collapsed view
  String get summary {
    switch (type) {
      case 'meal':
        final calories = details['calories'] ?? 0;
        return '$calories cal';
      case 'workout':
        final duration = details['duration_minutes'] ?? 0;
        final calories = details['calories'] ?? 0;
        return '$duration min • $calories cal burned';
      case 'task':
        return priority ?? 'medium';
      case 'water':
        final amount = details['amount'] ?? 0;
        return '${amount}ml';
      case 'supplement':
        return details['dosage'] ?? '';
      default:
        return '';
    }
  }

  /// Check if activity is overdue (for tasks)
  bool get isOverdue {
    if (type != 'task' || status == 'completed') return false;
    if (dueDate == null) return false;
    return dueDate!.isBefore(DateTime.now());
  }

  /// Check if activity is upcoming (for tasks/events)
  bool get isUpcoming {
    if (type != 'task' && type != 'event') return false;
    if (dueDate == null) return false;
    return dueDate!.isAfter(DateTime.now());
  }
}

class TimelineResponse {
  final List<TimelineActivity> activities;
  final int totalCount;
  final bool hasMore;
  final int nextOffset;

  TimelineResponse({
    required this.activities,
    required this.totalCount,
    required this.hasMore,
    required this.nextOffset,
  });

  factory TimelineResponse.fromJson(Map<String, dynamic> json) {
    return TimelineResponse(
      activities: (json['activities'] as List)
          .map((e) => TimelineActivity.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalCount: json['total_count'] as int,
      hasMore: json['has_more'] as bool,
      nextOffset: json['next_offset'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'activities': activities.map((e) => e.toJson()).toList(),
      'total_count': totalCount,
      'has_more': hasMore,
      'next_offset': nextOffset,
    };
  }
}

