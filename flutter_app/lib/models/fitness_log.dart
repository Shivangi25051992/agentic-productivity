enum FitnessLogType { meal, workout }

class FitnessLogModel {
  final String id;
  final String userId;
  final FitnessLogType type;
  final String content;
  final int? calories;
  final Map<String, dynamic>? parsedData;
  final DateTime timestamp;

  FitnessLogModel({
    required this.id,
    required this.userId,
    required this.type,
    required this.content,
    this.calories,
    this.parsedData,
    required this.timestamp,
  });

  factory FitnessLogModel.fromJson(Map<String, dynamic> json) => FitnessLogModel(
        id: (json['log_id'] ?? json['id']) as String,
        userId: (json['user_id'] ?? json['userId']) as String,
        type: _typeFrom(json['log_type'] as String?),
        content: json['content'] as String,
        calories: json['calories'] as int?,
        parsedData: (json['ai_parsed_data'] ?? json['parsedData']) is Map ?
            ((json['ai_parsed_data'] ?? json['parsedData']) as Map).cast<String, dynamic>() : null,
        timestamp: DateTime.parse(json['timestamp'] as String),
      );

  Map<String, dynamic> toJson() => {
        'log_id': id,
        'user_id': userId,
        'log_type': type.name,
        'content': content,
        'calories': calories,
        'ai_parsed_data': parsedData,
        'timestamp': timestamp.toIso8601String(),
      }..removeWhere((k, v) => v == null);

  static FitnessLogType _typeFrom(String? v) {
    switch ((v ?? 'meal').toLowerCase()) {
      case 'workout':
        return FitnessLogType.workout;
      default:
        return FitnessLogType.meal;
    }
  }
}


