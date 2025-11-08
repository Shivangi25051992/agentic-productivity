class ChatMessage {
  final String id;
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;
  
  // ✨ NEW: Expandable chat fields
  final String? summary;
  final String? suggestion;
  final Map<String, dynamic>? details;
  final bool expandable;
  
  // 🧠 PHASE 2: Explainable AI fields
  final double? confidenceScore;
  final String? confidenceLevel;
  final Map<String, dynamic>? confidenceFactors;
  final Map<String, dynamic>? explanation;
  final List<Map<String, dynamic>>? alternatives;

  ChatMessage({
    required this.id,
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.metadata,
    // ✨ NEW: Expandable fields (optional for backward compatibility)
    this.summary,
    this.suggestion,
    this.details,
    this.expandable = false,
    // 🧠 PHASE 2: Explainable AI fields (optional)
    this.confidenceScore,
    this.confidenceLevel,
    this.confidenceFactors,
    this.explanation,
    this.alternatives,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) => ChatMessage(
        id: (json['id'] ?? json['message_id']) as String,
        text: json['text'] as String,
        isUser: (json['isUser'] ?? (json['role'] == 'user')) as bool,
        timestamp: DateTime.parse((json['timestamp'] ?? json['created_at']) as String),
        metadata: (json['metadata'] as Map?)?.cast<String, dynamic>(),
        // ✨ NEW: Parse expandable fields from JSON
        summary: json['summary'] as String?,
        suggestion: json['suggestion'] as String?,
        details: (json['details'] as Map?)?.cast<String, dynamic>(),
        expandable: (json['expandable'] as bool?) ?? false,
        // 🧠 PHASE 2: Parse explainable AI fields from JSON
        confidenceScore: (json['confidence_score'] as num?)?.toDouble(),
        confidenceLevel: json['confidence_level'] as String?,
        confidenceFactors: (json['confidence_factors'] as Map?)?.cast<String, dynamic>(),
        explanation: (json['explanation'] as Map?)?.cast<String, dynamic>(),
        alternatives: (json['alternatives'] as List?)?.map((e) => (e as Map).cast<String, dynamic>()).toList(),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'text': text,
        'isUser': isUser,
        'timestamp': timestamp.toIso8601String(),
        if (metadata != null) 'metadata': metadata,
        // ✨ NEW: Include expandable fields in JSON
        if (summary != null) 'summary': summary,
        if (suggestion != null) 'suggestion': suggestion,
        if (details != null) 'details': details,
        'expandable': expandable,
        // 🧠 PHASE 2: Include explainable AI fields in JSON
        if (confidenceScore != null) 'confidence_score': confidenceScore,
        if (confidenceLevel != null) 'confidence_level': confidenceLevel,
        if (confidenceFactors != null) 'confidence_factors': confidenceFactors,
        if (explanation != null) 'explanation': explanation,
        if (alternatives != null) 'alternatives': alternatives,
      };
}


