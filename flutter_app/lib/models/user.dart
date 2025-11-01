class AppUser {
  final String id;
  final String email;
  final DateTime createdAt;

  AppUser({required this.id, required this.email, required this.createdAt});

  factory AppUser.fromJson(Map<String, dynamic> json) => AppUser(
        id: (json['user_id'] ?? json['id']) as String,
        email: json['email'] as String,
        createdAt: DateTime.parse((json['created_at'] ?? json['createdAt']) as String),
      );

  Map<String, dynamic> toJson() => {
        'user_id': id,
        'email': email,
        'created_at': createdAt.toIso8601String(),
      };
}


