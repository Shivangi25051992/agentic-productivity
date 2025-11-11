/// Enterprise-Grade Unit Tests for TaskModel
/// 
/// Testing Strategy:
/// - Test all public methods
/// - Test all enum conversions (TaskPriority, TaskStatus)
/// - Test edge cases and error conditions
/// - Test JSON serialization/deserialization
/// - Test alternative field names
/// - Achieve 100% code coverage
/// 
/// Quality Standards:
/// - Clear test names (Given-When-Then pattern)
/// - Isolated tests (no dependencies)
/// - Fast execution (< 100ms per test)
/// - Deterministic results

import 'package:flutter_test/flutter_test.dart';
import 'package:ai_productivity_app/models/task.dart';

void main() {
  group('TaskModel', () {
    // Test Fixtures (Arrange)
    final testCreatedAt = DateTime(2025, 11, 11, 10, 0, 0);
    final testUpdatedAt = DateTime(2025, 11, 11, 12, 0, 0);
    final testDueDate = DateTime(2025, 11, 15, 18, 0, 0);
    
    final validTaskJson = {
      'task_id': 'task-123',
      'user_id': 'user-456',
      'title': 'Complete project',
      'description': 'Finish the project by end of week',
      'due_date': '2025-11-15T18:00:00.000',
      'priority': 'high',
      'status': 'in_progress',
      'created_at': '2025-11-11T10:00:00.000',
      'updated_at': '2025-11-11T12:00:00.000',
    };
    
    group('Constructor', () {
      test('should create TaskModel with all required fields', () {
        // Arrange & Act
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Complete project',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        
        // Assert
        expect(task.id, equals('task-123'));
        expect(task.userId, equals('user-456'));
        expect(task.title, equals('Complete project'));
        expect(task.createdAt, equals(testCreatedAt));
        expect(task.updatedAt, equals(testUpdatedAt));
        expect(task.description, isNull);
        expect(task.dueDate, isNull);
        expect(task.priority, equals(TaskPriority.medium)); // Default
        expect(task.status, equals(TaskStatus.pending)); // Default
      });
      
      test('should create TaskModel with all optional fields', () {
        // Arrange & Act
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Complete project',
          description: 'Finish the project',
          dueDate: testDueDate,
          priority: TaskPriority.high,
          status: TaskStatus.inProgress,
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        
        // Assert
        expect(task.description, equals('Finish the project'));
        expect(task.dueDate, equals(testDueDate));
        expect(task.priority, equals(TaskPriority.high));
        expect(task.status, equals(TaskStatus.inProgress));
      });
      
      test('should create TaskModel with all priority levels', () {
        final priorities = [TaskPriority.low, TaskPriority.medium, TaskPriority.high];
        
        for (final priority in priorities) {
          final task = TaskModel(
            id: 'task-$priority',
            userId: 'user-456',
            title: 'Test task',
            priority: priority,
            createdAt: testCreatedAt,
            updatedAt: testUpdatedAt,
          );
          
          expect(task.priority, equals(priority));
        }
      });
      
      test('should create TaskModel with all status levels', () {
        final statuses = [
          TaskStatus.pending,
          TaskStatus.inProgress,
          TaskStatus.completed,
          TaskStatus.cancelled,
        ];
        
        for (final status in statuses) {
          final task = TaskModel(
            id: 'task-$status',
            userId: 'user-456',
            title: 'Test task',
            status: status,
            createdAt: testCreatedAt,
            updatedAt: testUpdatedAt,
          );
          
          expect(task.status, equals(status));
        }
      });
    });
    
    group('fromJson', () {
      test('should deserialize valid task JSON', () {
        // Act
        final task = TaskModel.fromJson(validTaskJson);
        
        // Assert
        expect(task.id, equals('task-123'));
        expect(task.userId, equals('user-456'));
        expect(task.title, equals('Complete project'));
        expect(task.description, equals('Finish the project by end of week'));
        expect(task.dueDate, equals(DateTime.parse('2025-11-15T18:00:00.000')));
        expect(task.priority, equals(TaskPriority.high));
        expect(task.status, equals(TaskStatus.inProgress));
        expect(task.createdAt, equals(DateTime.parse('2025-11-11T10:00:00.000')));
        expect(task.updatedAt, equals(DateTime.parse('2025-11-11T12:00:00.000')));
      });
      
      test('should handle alternative JSON field names (id vs task_id)', () {
        // Arrange
        final jsonWithId = {
          'id': 'task-alt-123',  // Alternative field name
          'user_id': 'user-456',
          'title': 'Test task',
          'created_at': '2025-11-11T10:00:00.000',
          'updated_at': '2025-11-11T12:00:00.000',
        };
        
        // Act
        final task = TaskModel.fromJson(jsonWithId);
        
        // Assert
        expect(task.id, equals('task-alt-123'));
      });
      
      test('should handle alternative JSON field names (userId vs user_id)', () {
        // Arrange
        final jsonWithUserId = {
          'task_id': 'task-123',
          'userId': 'user-alt-789',  // Alternative field name
          'title': 'Test task',
          'created_at': '2025-11-11T10:00:00.000',
          'updated_at': '2025-11-11T12:00:00.000',
        };
        
        // Act
        final task = TaskModel.fromJson(jsonWithUserId);
        
        // Assert
        expect(task.userId, equals('user-alt-789'));
      });
      
      test('should handle alternative JSON field names (createdAt vs created_at)', () {
        // Arrange
        final jsonWithCreatedAt = {
          'task_id': 'task-123',
          'user_id': 'user-456',
          'title': 'Test task',
          'createdAt': '2025-11-11T10:00:00.000',  // Alternative field name
          'updated_at': '2025-11-11T12:00:00.000',
        };
        
        // Act
        final task = TaskModel.fromJson(jsonWithCreatedAt);
        
        // Assert
        expect(task.createdAt, equals(DateTime.parse('2025-11-11T10:00:00.000')));
      });
      
      test('should handle alternative JSON field names (updatedAt vs updated_at)', () {
        // Arrange
        final jsonWithUpdatedAt = {
          'task_id': 'task-123',
          'user_id': 'user-456',
          'title': 'Test task',
          'created_at': '2025-11-11T10:00:00.000',
          'updatedAt': '2025-11-11T12:00:00.000',  // Alternative field name
        };
        
        // Act
        final task = TaskModel.fromJson(jsonWithUpdatedAt);
        
        // Assert
        expect(task.updatedAt, equals(DateTime.parse('2025-11-11T12:00:00.000')));
      });
      
      test('should handle null description', () {
        // Arrange
        final jsonWithoutDescription = Map<String, dynamic>.from(validTaskJson)
          ..remove('description');
        
        // Act
        final task = TaskModel.fromJson(jsonWithoutDescription);
        
        // Assert
        expect(task.description, isNull);
      });
      
      test('should handle null due_date', () {
        // Arrange
        final jsonWithoutDueDate = Map<String, dynamic>.from(validTaskJson)
          ..remove('due_date');
        
        // Act
        final task = TaskModel.fromJson(jsonWithoutDueDate);
        
        // Assert
        expect(task.dueDate, isNull);
      });
      
      test('should handle null priority (defaults to medium)', () {
        // Arrange
        final jsonWithoutPriority = Map<String, dynamic>.from(validTaskJson)
          ..remove('priority');
        
        // Act
        final task = TaskModel.fromJson(jsonWithoutPriority);
        
        // Assert
        expect(task.priority, equals(TaskPriority.medium));
      });
      
      test('should handle null status (defaults to pending)', () {
        // Arrange
        final jsonWithoutStatus = Map<String, dynamic>.from(validTaskJson)
          ..remove('status');
        
        // Act
        final task = TaskModel.fromJson(jsonWithoutStatus);
        
        // Assert
        expect(task.status, equals(TaskStatus.pending));
      });
    });
    
    group('toJson', () {
      test('should serialize TaskModel to JSON with all fields', () {
        // Arrange
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Complete project',
          description: 'Finish the project',
          dueDate: testDueDate,
          priority: TaskPriority.high,
          status: TaskStatus.inProgress,
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        
        // Act
        final json = task.toJson();
        
        // Assert
        expect(json['task_id'], equals('task-123'));
        expect(json['user_id'], equals('user-456'));
        expect(json['title'], equals('Complete project'));
        expect(json['description'], equals('Finish the project'));
        expect(json['due_date'], equals('2025-11-15T18:00:00.000'));
        expect(json['priority'], equals('high'));
        expect(json['status'], equals('in_progress'));
        expect(json['created_at'], equals('2025-11-11T10:00:00.000'));
        expect(json['updated_at'], equals('2025-11-11T12:00:00.000'));
      });
      
      test('should omit null values from JSON', () {
        // Arrange
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Complete project',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
          // description and dueDate are null
        );
        
        // Act
        final json = task.toJson();
        
        // Assert
        expect(json.containsKey('description'), isFalse);
        expect(json.containsKey('due_date'), isFalse);
      });
      
      test('should preserve timestamp precision in JSON', () {
        // Arrange
        final preciseCreatedAt = DateTime(2025, 11, 11, 10, 30, 45, 123);
        final preciseUpdatedAt = DateTime(2025, 11, 11, 12, 30, 45, 456);
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Test task',
          createdAt: preciseCreatedAt,
          updatedAt: preciseUpdatedAt,
        );
        
        // Act
        final json = task.toJson();
        
        // Assert
        expect(json['created_at'], equals('2025-11-11T10:30:45.123'));
        expect(json['updated_at'], equals('2025-11-11T12:30:45.456'));
      });
    });
    
    group('JSON Roundtrip', () {
      test('should maintain data integrity through serialize/deserialize cycle', () {
        // Arrange
        final original = TaskModel(
          id: 'task-roundtrip',
          userId: 'user-roundtrip',
          title: 'Complex task',
          description: 'Detailed description',
          dueDate: testDueDate,
          priority: TaskPriority.high,
          status: TaskStatus.inProgress,
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        
        // Act
        final json = original.toJson();
        final deserialized = TaskModel.fromJson(json);
        
        // Assert
        expect(deserialized.id, equals(original.id));
        expect(deserialized.userId, equals(original.userId));
        expect(deserialized.title, equals(original.title));
        expect(deserialized.description, equals(original.description));
        expect(deserialized.dueDate, equals(original.dueDate));
        expect(deserialized.priority, equals(original.priority));
        expect(deserialized.status, equals(original.status));
        expect(deserialized.createdAt, equals(original.createdAt));
        expect(deserialized.updatedAt, equals(original.updatedAt));
      });
    });
    
    group('Priority Conversion (_priorityFrom)', () {
      test('should convert "low" to TaskPriority.low', () {
        final json = {...validTaskJson, 'priority': 'low'};
        final task = TaskModel.fromJson(json);
        expect(task.priority, equals(TaskPriority.low));
      });
      
      test('should convert "medium" to TaskPriority.medium', () {
        final json = {...validTaskJson, 'priority': 'medium'};
        final task = TaskModel.fromJson(json);
        expect(task.priority, equals(TaskPriority.medium));
      });
      
      test('should convert "high" to TaskPriority.high', () {
        final json = {...validTaskJson, 'priority': 'high'};
        final task = TaskModel.fromJson(json);
        expect(task.priority, equals(TaskPriority.high));
      });
      
      test('should handle case-insensitive priority (LOW)', () {
        final json = {...validTaskJson, 'priority': 'LOW'};
        final task = TaskModel.fromJson(json);
        expect(task.priority, equals(TaskPriority.low));
      });
      
      test('should handle case-insensitive priority (High)', () {
        final json = {...validTaskJson, 'priority': 'High'};
        final task = TaskModel.fromJson(json);
        expect(task.priority, equals(TaskPriority.high));
      });
      
      test('should default to medium for unknown priority', () {
        final json = {...validTaskJson, 'priority': 'unknown'};
        final task = TaskModel.fromJson(json);
        expect(task.priority, equals(TaskPriority.medium));
      });
      
      test('should default to medium for null priority', () {
        final json = Map<String, dynamic>.from(validTaskJson)..remove('priority');
        final task = TaskModel.fromJson(json);
        expect(task.priority, equals(TaskPriority.medium));
      });
    });
    
    group('Status Conversion (_statusFrom)', () {
      test('should convert "pending" to TaskStatus.pending', () {
        final json = {...validTaskJson, 'status': 'pending'};
        final task = TaskModel.fromJson(json);
        expect(task.status, equals(TaskStatus.pending));
      });
      
      test('should convert "in_progress" to TaskStatus.inProgress', () {
        final json = {...validTaskJson, 'status': 'in_progress'};
        final task = TaskModel.fromJson(json);
        expect(task.status, equals(TaskStatus.inProgress));
      });
      
      test('should convert "inprogress" (no underscore) to TaskStatus.inProgress', () {
        final json = {...validTaskJson, 'status': 'inprogress'};
        final task = TaskModel.fromJson(json);
        expect(task.status, equals(TaskStatus.inProgress));
      });
      
      test('should convert "completed" to TaskStatus.completed', () {
        final json = {...validTaskJson, 'status': 'completed'};
        final task = TaskModel.fromJson(json);
        expect(task.status, equals(TaskStatus.completed));
      });
      
      test('should convert "cancelled" to TaskStatus.cancelled', () {
        final json = {...validTaskJson, 'status': 'cancelled'};
        final task = TaskModel.fromJson(json);
        expect(task.status, equals(TaskStatus.cancelled));
      });
      
      test('should convert "canceled" (US spelling) to TaskStatus.cancelled', () {
        final json = {...validTaskJson, 'status': 'canceled'};
        final task = TaskModel.fromJson(json);
        expect(task.status, equals(TaskStatus.cancelled));
      });
      
      test('should handle case-insensitive status (PENDING)', () {
        final json = {...validTaskJson, 'status': 'PENDING'};
        final task = TaskModel.fromJson(json);
        expect(task.status, equals(TaskStatus.pending));
      });
      
      test('should handle case-insensitive status (Completed)', () {
        final json = {...validTaskJson, 'status': 'Completed'};
        final task = TaskModel.fromJson(json);
        expect(task.status, equals(TaskStatus.completed));
      });
      
      test('should default to pending for unknown status', () {
        final json = {...validTaskJson, 'status': 'unknown'};
        final task = TaskModel.fromJson(json);
        expect(task.status, equals(TaskStatus.pending));
      });
      
      test('should default to pending for null status', () {
        final json = Map<String, dynamic>.from(validTaskJson)..remove('status');
        final task = TaskModel.fromJson(json);
        expect(task.status, equals(TaskStatus.pending));
      });
    });
    
    group('Status to API Conversion (_statusToApi)', () {
      test('should convert TaskStatus.pending to "pending"', () {
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Test',
          status: TaskStatus.pending,
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        final json = task.toJson();
        expect(json['status'], equals('pending'));
      });
      
      test('should convert TaskStatus.inProgress to "in_progress"', () {
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Test',
          status: TaskStatus.inProgress,
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        final json = task.toJson();
        expect(json['status'], equals('in_progress'));
      });
      
      test('should convert TaskStatus.completed to "completed"', () {
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Test',
          status: TaskStatus.completed,
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        final json = task.toJson();
        expect(json['status'], equals('completed'));
      });
      
      test('should convert TaskStatus.cancelled to "cancelled"', () {
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Test',
          status: TaskStatus.cancelled,
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        final json = task.toJson();
        expect(json['status'], equals('cancelled'));
      });
    });
    
    group('Edge Cases', () {
      test('should handle empty title', () {
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: '',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        expect(task.title, equals(''));
      });
      
      test('should handle very long title', () {
        final longTitle = 'A' * 10000;
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: longTitle,
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        expect(task.title.length, equals(10000));
      });
      
      test('should handle special characters in title', () {
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: '✅ Complete project! @#\$%^&*()',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        expect(task.title, contains('✅'));
        expect(task.title, contains('@#\$%'));
      });
      
      test('should handle empty description', () {
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Test',
          description: '',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        expect(task.description, equals(''));
      });
      
      test('should handle very long description', () {
        final longDescription = 'A' * 100000;
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Test',
          description: longDescription,
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        expect(task.description!.length, equals(100000));
      });
      
      test('should handle due date in the past', () {
        final pastDate = DateTime(2020, 1, 1);
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Test',
          dueDate: pastDate,
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        expect(task.dueDate, equals(pastDate));
      });
      
      test('should handle due date far in the future', () {
        final futureDate = DateTime(2099, 12, 31);
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Test',
          dueDate: futureDate,
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );
        expect(task.dueDate, equals(futureDate));
      });
      
      test('should handle updatedAt before createdAt (edge case)', () {
        final laterDate = DateTime(2025, 11, 12);
        final earlierDate = DateTime(2025, 11, 10);
        final task = TaskModel(
          id: 'task-123',
          userId: 'user-456',
          title: 'Test',
          createdAt: laterDate,
          updatedAt: earlierDate,
        );
        expect(task.createdAt, equals(laterDate));
        expect(task.updatedAt, equals(earlierDate));
      });
    });
  });
}

