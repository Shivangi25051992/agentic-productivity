/// Enterprise-Grade Unit Tests for TimelineActivity & TimelineResponse
/// 
/// Testing Strategy:
/// - Test all public methods and getters
/// - Test all activity types (meal, workout, task, event, water, supplement)
/// - Test edge cases and error conditions
/// - Test JSON serialization/deserialization
/// - Test computed properties (iconName, displayColor, summary, isOverdue, isUpcoming)
/// - Achieve 100% code coverage
/// 
/// Quality Standards:
/// - Clear test names (Given-When-Then pattern)
/// - Isolated tests (no dependencies)
/// - Fast execution (< 100ms per test)
/// - Deterministic results

import 'package:flutter_test/flutter_test.dart';
import 'package:ai_productivity_app/models/timeline_activity.dart';

void main() {
  group('TimelineActivity', () {
    // Test Fixtures (Arrange)
    final testTimestamp = DateTime(2025, 11, 11, 12, 0, 0);
    final testDueDate = DateTime(2025, 11, 12, 18, 0, 0);
    
    final validMealJson = {
      'id': 'meal-123',
      'type': 'meal',
      'title': '1 apple',
      'timestamp': '2025-11-11T12:00:00.000',
      'icon': '🍎',
      'color': '#4CAF50',
      'status': 'logged',
      'details': {
        'calories': 95,
        'items': ['apple'],
      },
    };
    
    final validWorkoutJson = {
      'id': 'workout-456',
      'type': 'workout',
      'title': '30 min running',
      'timestamp': '2025-11-11T12:00:00.000',
      'icon': '🏃',
      'color': '#2196F3',
      'status': 'completed',
      'details': {
        'duration_minutes': 30,
        'calories': 300,
        'type': 'running',
      },
    };
    
    final validTaskJson = {
      'id': 'task-789',
      'type': 'task',
      'title': 'Complete project',
      'timestamp': '2025-11-11T12:00:00.000',
      'icon': '✓',
      'color': '#FF9800',
      'status': 'pending',
      'details': {
        'description': 'Finish the project',
      },
      'due_date': '2025-11-12T18:00:00.000',
      'priority': 'high',
      'client_generated_id': 'client-task-123',
    };
    
    group('Constructor', () {
      test('should create TimelineActivity with all required fields', () {
        // Arrange & Act
        final activity = TimelineActivity(
          id: 'test-123',
          type: 'meal',
          title: '1 apple',
          timestamp: testTimestamp,
          icon: '🍎',
          color: '#4CAF50',
          status: 'logged',
          details: {'calories': 95},
        );
        
        // Assert
        expect(activity.id, equals('test-123'));
        expect(activity.type, equals('meal'));
        expect(activity.title, equals('1 apple'));
        expect(activity.timestamp, equals(testTimestamp));
        expect(activity.icon, equals('🍎'));
        expect(activity.color, equals('#4CAF50'));
        expect(activity.status, equals('logged'));
        expect(activity.details, equals({'calories': 95}));
        expect(activity.dueDate, isNull);
        expect(activity.priority, isNull);
        expect(activity.clientGeneratedId, isNull);
      });
      
      test('should create TimelineActivity with optional fields', () {
        // Arrange & Act
        final activity = TimelineActivity(
          id: 'test-123',
          type: 'task',
          title: 'Complete project',
          timestamp: testTimestamp,
          icon: '✓',
          color: '#FF9800',
          status: 'pending',
          details: {},
          dueDate: testDueDate,
          priority: 'high',
          clientGeneratedId: 'client-123',
        );
        
        // Assert
        expect(activity.dueDate, equals(testDueDate));
        expect(activity.priority, equals('high'));
        expect(activity.clientGeneratedId, equals('client-123'));
      });
      
      test('should create all activity types', () {
        final types = ['meal', 'workout', 'task', 'event', 'water', 'supplement'];
        
        for (final type in types) {
          final activity = TimelineActivity(
            id: 'test-$type',
            type: type,
            title: 'Test $type',
            timestamp: testTimestamp,
            icon: '🔵',
            color: '#000000',
            status: 'active',
            details: {},
          );
          
          expect(activity.type, equals(type));
        }
      });
    });
    
    group('fromJson', () {
      test('should deserialize valid meal JSON', () {
        // Act
        final activity = TimelineActivity.fromJson(validMealJson);
        
        // Assert
        expect(activity.id, equals('meal-123'));
        expect(activity.type, equals('meal'));
        expect(activity.title, equals('1 apple'));
        expect(activity.timestamp, equals(DateTime.parse('2025-11-11T12:00:00.000')));
        expect(activity.icon, equals('🍎'));
        expect(activity.color, equals('#4CAF50'));
        expect(activity.status, equals('logged'));
        expect(activity.details['calories'], equals(95));
        expect(activity.dueDate, isNull);
        expect(activity.priority, isNull);
        expect(activity.clientGeneratedId, isNull);
      });
      
      test('should deserialize valid workout JSON', () {
        // Act
        final activity = TimelineActivity.fromJson(validWorkoutJson);
        
        // Assert
        expect(activity.id, equals('workout-456'));
        expect(activity.type, equals('workout'));
        expect(activity.title, equals('30 min running'));
        expect(activity.details['duration_minutes'], equals(30));
        expect(activity.details['calories'], equals(300));
      });
      
      test('should deserialize valid task JSON with all optional fields', () {
        // Act
        final activity = TimelineActivity.fromJson(validTaskJson);
        
        // Assert
        expect(activity.id, equals('task-789'));
        expect(activity.type, equals('task'));
        expect(activity.dueDate, equals(DateTime.parse('2025-11-12T18:00:00.000')));
        expect(activity.priority, equals('high'));
        expect(activity.clientGeneratedId, equals('client-task-123'));
      });
      
      test('should handle null due_date', () {
        // Arrange
        final jsonWithoutDueDate = Map<String, dynamic>.from(validTaskJson)
          ..remove('due_date');
        
        // Act
        final activity = TimelineActivity.fromJson(jsonWithoutDueDate);
        
        // Assert
        expect(activity.dueDate, isNull);
      });
      
      test('should handle null priority', () {
        // Arrange
        final jsonWithoutPriority = Map<String, dynamic>.from(validTaskJson)
          ..remove('priority');
        
        // Act
        final activity = TimelineActivity.fromJson(jsonWithoutPriority);
        
        // Assert
        expect(activity.priority, isNull);
      });
      
      test('should handle null client_generated_id', () {
        // Arrange
        final jsonWithoutClientId = Map<String, dynamic>.from(validTaskJson)
          ..remove('client_generated_id');
        
        // Act
        final activity = TimelineActivity.fromJson(jsonWithoutClientId);
        
        // Assert
        expect(activity.clientGeneratedId, isNull);
      });
      
      test('should handle empty details map', () {
        // Arrange
        final jsonWithEmptyDetails = {
          ...validMealJson,
          'details': {},
        };
        
        // Act
        final activity = TimelineActivity.fromJson(jsonWithEmptyDetails);
        
        // Assert
        expect(activity.details, isEmpty);
      });
      
      test('should handle complex nested details', () {
        // Arrange
        final jsonWithComplexDetails = {
          ...validMealJson,
          'details': {
            'calories': 450,
            'items': [
              {'name': 'chicken', 'quantity': 200},
              {'name': 'rice', 'quantity': 150},
            ],
            'nutrition': {
              'protein': 45.5,
              'carbs': 60.2,
            },
          },
        };
        
        // Act
        final activity = TimelineActivity.fromJson(jsonWithComplexDetails);
        
        // Assert
        expect(activity.details['calories'], equals(450));
        expect(activity.details['items'], isA<List>());
        expect(activity.details['nutrition'], isA<Map>());
      });
    });
    
    group('toJson', () {
      test('should serialize TimelineActivity to JSON with all fields', () {
        // Arrange
        final activity = TimelineActivity(
          id: 'test-123',
          type: 'task',
          title: 'Complete project',
          timestamp: testTimestamp,
          icon: '✓',
          color: '#FF9800',
          status: 'pending',
          details: {'description': 'Test'},
          dueDate: testDueDate,
          priority: 'high',
          clientGeneratedId: 'client-123',
        );
        
        // Act
        final json = activity.toJson();
        
        // Assert
        expect(json['id'], equals('test-123'));
        expect(json['type'], equals('task'));
        expect(json['title'], equals('Complete project'));
        expect(json['timestamp'], equals('2025-11-11T12:00:00.000'));
        expect(json['icon'], equals('✓'));
        expect(json['color'], equals('#FF9800'));
        expect(json['status'], equals('pending'));
        expect(json['details'], equals({'description': 'Test'}));
        expect(json['due_date'], equals('2025-11-12T18:00:00.000'));
        expect(json['priority'], equals('high'));
        expect(json['client_generated_id'], equals('client-123'));
      });
      
      test('should omit null optional fields from JSON', () {
        // Arrange
        final activity = TimelineActivity(
          id: 'test-123',
          type: 'meal',
          title: '1 apple',
          timestamp: testTimestamp,
          icon: '🍎',
          color: '#4CAF50',
          status: 'logged',
          details: {'calories': 95},
          // dueDate, priority, clientGeneratedId are null
        );
        
        // Act
        final json = activity.toJson();
        
        // Assert
        expect(json.containsKey('due_date'), isFalse);
        expect(json.containsKey('priority'), isFalse);
        expect(json.containsKey('client_generated_id'), isFalse);
      });
      
      test('should preserve timestamp precision in JSON', () {
        // Arrange
        final preciseTimestamp = DateTime(2025, 11, 11, 12, 30, 45, 123);
        final activity = TimelineActivity(
          id: 'test-123',
          type: 'meal',
          title: 'Test',
          timestamp: preciseTimestamp,
          icon: '🍎',
          color: '#4CAF50',
          status: 'logged',
          details: {},
        );
        
        // Act
        final json = activity.toJson();
        
        // Assert
        expect(json['timestamp'], equals('2025-11-11T12:30:45.123'));
      });
    });
    
    group('JSON Roundtrip', () {
      test('should maintain data integrity through serialize/deserialize cycle', () {
        // Arrange
        final original = TimelineActivity(
          id: 'roundtrip-123',
          type: 'task',
          title: 'Complex task',
          timestamp: testTimestamp,
          icon: '✓',
          color: '#FF9800',
          status: 'pending',
          details: {
            'description': 'Test description',
            'tags': ['urgent', 'important'],
          },
          dueDate: testDueDate,
          priority: 'high',
          clientGeneratedId: 'client-roundtrip',
        );
        
        // Act
        final json = original.toJson();
        final deserialized = TimelineActivity.fromJson(json);
        
        // Assert
        expect(deserialized.id, equals(original.id));
        expect(deserialized.type, equals(original.type));
        expect(deserialized.title, equals(original.title));
        expect(deserialized.timestamp, equals(original.timestamp));
        expect(deserialized.icon, equals(original.icon));
        expect(deserialized.color, equals(original.color));
        expect(deserialized.status, equals(original.status));
        expect(deserialized.details, equals(original.details));
        expect(deserialized.dueDate, equals(original.dueDate));
        expect(deserialized.priority, equals(original.priority));
        expect(deserialized.clientGeneratedId, equals(original.clientGeneratedId));
      });
    });
    
    group('iconName getter', () {
      test('should return correct icon for meal', () {
        final activity = TimelineActivity(
          id: 'test', type: 'meal', title: 'Test', timestamp: testTimestamp,
          icon: '🍎', color: '#000', status: 'active', details: {},
        );
        expect(activity.iconName, equals('restaurant'));
      });
      
      test('should return correct icon for workout', () {
        final activity = TimelineActivity(
          id: 'test', type: 'workout', title: 'Test', timestamp: testTimestamp,
          icon: '🏃', color: '#000', status: 'active', details: {},
        );
        expect(activity.iconName, equals('fitness_center'));
      });
      
      test('should return correct icon for task', () {
        final activity = TimelineActivity(
          id: 'test', type: 'task', title: 'Test', timestamp: testTimestamp,
          icon: '✓', color: '#000', status: 'active', details: {},
        );
        expect(activity.iconName, equals('check_circle'));
      });
      
      test('should return correct icon for event', () {
        final activity = TimelineActivity(
          id: 'test', type: 'event', title: 'Test', timestamp: testTimestamp,
          icon: '📅', color: '#000', status: 'active', details: {},
        );
        expect(activity.iconName, equals('event'));
      });
      
      test('should return correct icon for water', () {
        final activity = TimelineActivity(
          id: 'test', type: 'water', title: 'Test', timestamp: testTimestamp,
          icon: '💧', color: '#000', status: 'active', details: {},
        );
        expect(activity.iconName, equals('water_drop'));
      });
      
      test('should return correct icon for supplement', () {
        final activity = TimelineActivity(
          id: 'test', type: 'supplement', title: 'Test', timestamp: testTimestamp,
          icon: '💊', color: '#000', status: 'active', details: {},
        );
        expect(activity.iconName, equals('medication'));
      });
      
      test('should return default icon for unknown type', () {
        final activity = TimelineActivity(
          id: 'test', type: 'unknown', title: 'Test', timestamp: testTimestamp,
          icon: '❓', color: '#000', status: 'active', details: {},
        );
        expect(activity.iconName, equals('circle'));
      });
    });
    
    group('displayColor getter', () {
      test('should return correct color for meal', () {
        final activity = TimelineActivity(
          id: 'test', type: 'meal', title: 'Test', timestamp: testTimestamp,
          icon: '🍎', color: '#000', status: 'active', details: {},
        );
        expect(activity.displayColor, equals('#4CAF50'));
      });
      
      test('should return correct color for workout', () {
        final activity = TimelineActivity(
          id: 'test', type: 'workout', title: 'Test', timestamp: testTimestamp,
          icon: '🏃', color: '#000', status: 'active', details: {},
        );
        expect(activity.displayColor, equals('#2196F3'));
      });
      
      test('should return correct color for task', () {
        final activity = TimelineActivity(
          id: 'test', type: 'task', title: 'Test', timestamp: testTimestamp,
          icon: '✓', color: '#000', status: 'active', details: {},
        );
        expect(activity.displayColor, equals('#FF9800'));
      });
      
      test('should return correct color for event', () {
        final activity = TimelineActivity(
          id: 'test', type: 'event', title: 'Test', timestamp: testTimestamp,
          icon: '📅', color: '#000', status: 'active', details: {},
        );
        expect(activity.displayColor, equals('#9C27B0'));
      });
      
      test('should return correct color for water', () {
        final activity = TimelineActivity(
          id: 'test', type: 'water', title: 'Test', timestamp: testTimestamp,
          icon: '💧', color: '#000', status: 'active', details: {},
        );
        expect(activity.displayColor, equals('#00BCD4'));
      });
      
      test('should return correct color for supplement', () {
        final activity = TimelineActivity(
          id: 'test', type: 'supplement', title: 'Test', timestamp: testTimestamp,
          icon: '💊', color: '#000', status: 'active', details: {},
        );
        expect(activity.displayColor, equals('#E91E63'));
      });
      
      test('should return default color for unknown type', () {
        final activity = TimelineActivity(
          id: 'test', type: 'unknown', title: 'Test', timestamp: testTimestamp,
          icon: '❓', color: '#000', status: 'active', details: {},
        );
        expect(activity.displayColor, equals('#9E9E9E'));
      });
    });
    
    group('summary getter', () {
      test('should return correct summary for meal', () {
        final activity = TimelineActivity(
          id: 'test', type: 'meal', title: 'Test', timestamp: testTimestamp,
          icon: '🍎', color: '#000', status: 'active',
          details: {'calories': 450},
        );
        expect(activity.summary, equals('450 cal'));
      });
      
      test('should return 0 cal for meal with missing calories', () {
        final activity = TimelineActivity(
          id: 'test', type: 'meal', title: 'Test', timestamp: testTimestamp,
          icon: '🍎', color: '#000', status: 'active',
          details: {},
        );
        expect(activity.summary, equals('0 cal'));
      });
      
      test('should return correct summary for workout', () {
        final activity = TimelineActivity(
          id: 'test', type: 'workout', title: 'Test', timestamp: testTimestamp,
          icon: '🏃', color: '#000', status: 'active',
          details: {'duration_minutes': 45, 'calories': 500},
        );
        expect(activity.summary, equals('45 min • 500 cal burned'));
      });
      
      test('should return 0 values for workout with missing data', () {
        final activity = TimelineActivity(
          id: 'test', type: 'workout', title: 'Test', timestamp: testTimestamp,
          icon: '🏃', color: '#000', status: 'active',
          details: {},
        );
        expect(activity.summary, equals('0 min • 0 cal burned'));
      });
      
      test('should return priority for task', () {
        final activity = TimelineActivity(
          id: 'test', type: 'task', title: 'Test', timestamp: testTimestamp,
          icon: '✓', color: '#000', status: 'active', details: {},
          priority: 'high',
        );
        expect(activity.summary, equals('high'));
      });
      
      test('should return medium for task with no priority', () {
        final activity = TimelineActivity(
          id: 'test', type: 'task', title: 'Test', timestamp: testTimestamp,
          icon: '✓', color: '#000', status: 'active', details: {},
        );
        expect(activity.summary, equals('medium'));
      });
      
      test('should return correct summary for water', () {
        final activity = TimelineActivity(
          id: 'test', type: 'water', title: 'Test', timestamp: testTimestamp,
          icon: '💧', color: '#000', status: 'active',
          details: {'amount': 500},
        );
        expect(activity.summary, equals('500ml'));
      });
      
      test('should return 0ml for water with missing amount', () {
        final activity = TimelineActivity(
          id: 'test', type: 'water', title: 'Test', timestamp: testTimestamp,
          icon: '💧', color: '#000', status: 'active',
          details: {},
        );
        expect(activity.summary, equals('0ml'));
      });
      
      test('should return correct summary for supplement', () {
        final activity = TimelineActivity(
          id: 'test', type: 'supplement', title: 'Test', timestamp: testTimestamp,
          icon: '💊', color: '#000', status: 'active',
          details: {'dosage': '500mg'},
        );
        expect(activity.summary, equals('500mg'));
      });
      
      test('should return empty string for supplement with missing dosage', () {
        final activity = TimelineActivity(
          id: 'test', type: 'supplement', title: 'Test', timestamp: testTimestamp,
          icon: '💊', color: '#000', status: 'active',
          details: {},
        );
        expect(activity.summary, equals(''));
      });
      
      test('should return empty string for unknown type', () {
        final activity = TimelineActivity(
          id: 'test', type: 'unknown', title: 'Test', timestamp: testTimestamp,
          icon: '❓', color: '#000', status: 'active', details: {},
        );
        expect(activity.summary, equals(''));
      });
    });
    
    group('isOverdue getter', () {
      test('should return false for non-task activity', () {
        final activity = TimelineActivity(
          id: 'test', type: 'meal', title: 'Test', timestamp: testTimestamp,
          icon: '🍎', color: '#000', status: 'active', details: {},
          dueDate: DateTime.now().subtract(const Duration(days: 1)),
        );
        expect(activity.isOverdue, isFalse);
      });
      
      test('should return false for completed task', () {
        final activity = TimelineActivity(
          id: 'test', type: 'task', title: 'Test', timestamp: testTimestamp,
          icon: '✓', color: '#000', status: 'completed', details: {},
          dueDate: DateTime.now().subtract(const Duration(days: 1)),
        );
        expect(activity.isOverdue, isFalse);
      });
      
      test('should return false for task with no due date', () {
        final activity = TimelineActivity(
          id: 'test', type: 'task', title: 'Test', timestamp: testTimestamp,
          icon: '✓', color: '#000', status: 'pending', details: {},
        );
        expect(activity.isOverdue, isFalse);
      });
      
      test('should return true for overdue task', () {
        final activity = TimelineActivity(
          id: 'test', type: 'task', title: 'Test', timestamp: testTimestamp,
          icon: '✓', color: '#000', status: 'pending', details: {},
          dueDate: DateTime.now().subtract(const Duration(days: 1)),
        );
        expect(activity.isOverdue, isTrue);
      });
      
      test('should return false for task due in future', () {
        final activity = TimelineActivity(
          id: 'test', type: 'task', title: 'Test', timestamp: testTimestamp,
          icon: '✓', color: '#000', status: 'pending', details: {},
          dueDate: DateTime.now().add(const Duration(days: 1)),
        );
        expect(activity.isOverdue, isFalse);
      });
    });
    
    group('isUpcoming getter', () {
      test('should return false for non-task/event activity', () {
        final activity = TimelineActivity(
          id: 'test', type: 'meal', title: 'Test', timestamp: testTimestamp,
          icon: '🍎', color: '#000', status: 'active', details: {},
          dueDate: DateTime.now().add(const Duration(days: 1)),
        );
        expect(activity.isUpcoming, isFalse);
      });
      
      test('should return false for task with no due date', () {
        final activity = TimelineActivity(
          id: 'test', type: 'task', title: 'Test', timestamp: testTimestamp,
          icon: '✓', color: '#000', status: 'pending', details: {},
        );
        expect(activity.isUpcoming, isFalse);
      });
      
      test('should return true for upcoming task', () {
        final activity = TimelineActivity(
          id: 'test', type: 'task', title: 'Test', timestamp: testTimestamp,
          icon: '✓', color: '#000', status: 'pending', details: {},
          dueDate: DateTime.now().add(const Duration(days: 1)),
        );
        expect(activity.isUpcoming, isTrue);
      });
      
      test('should return true for upcoming event', () {
        final activity = TimelineActivity(
          id: 'test', type: 'event', title: 'Test', timestamp: testTimestamp,
          icon: '📅', color: '#000', status: 'pending', details: {},
          dueDate: DateTime.now().add(const Duration(days: 1)),
        );
        expect(activity.isUpcoming, isTrue);
      });
      
      test('should return false for past task', () {
        final activity = TimelineActivity(
          id: 'test', type: 'task', title: 'Test', timestamp: testTimestamp,
          icon: '✓', color: '#000', status: 'pending', details: {},
          dueDate: DateTime.now().subtract(const Duration(days: 1)),
        );
        expect(activity.isUpcoming, isFalse);
      });
    });
    
    group('Edge Cases', () {
      test('should handle empty title', () {
        final activity = TimelineActivity(
          id: 'test', type: 'meal', title: '', timestamp: testTimestamp,
          icon: '🍎', color: '#000', status: 'active', details: {},
        );
        expect(activity.title, equals(''));
      });
      
      test('should handle very long title', () {
        final longTitle = 'A' * 10000;
        final activity = TimelineActivity(
          id: 'test', type: 'meal', title: longTitle, timestamp: testTimestamp,
          icon: '🍎', color: '#000', status: 'active', details: {},
        );
        expect(activity.title.length, equals(10000));
      });
      
      test('should handle special characters in title', () {
        final activity = TimelineActivity(
          id: 'test', type: 'meal', title: '🍎🍊🍌 & special chars!@#\$%',
          timestamp: testTimestamp, icon: '🍎', color: '#000', status: 'active',
          details: {},
        );
        expect(activity.title, contains('🍎'));
        expect(activity.title, contains('&'));
      });
      
      test('should handle empty details map', () {
        final activity = TimelineActivity(
          id: 'test', type: 'meal', title: 'Test', timestamp: testTimestamp,
          icon: '🍎', color: '#000', status: 'active', details: {},
        );
        expect(activity.details, isEmpty);
      });
      
      test('should handle very large calorie values', () {
        final activity = TimelineActivity(
          id: 'test', type: 'meal', title: 'Test', timestamp: testTimestamp,
          icon: '🍎', color: '#000', status: 'active',
          details: {'calories': 999999},
        );
        expect(activity.summary, equals('999999 cal'));
      });
      
      test('should handle negative calorie values (edge case)', () {
        final activity = TimelineActivity(
          id: 'test', type: 'meal', title: 'Test', timestamp: testTimestamp,
          icon: '🍎', color: '#000', status: 'active',
          details: {'calories': -100},
        );
        expect(activity.summary, equals('-100 cal'));
      });
    });
  });
  
  group('TimelineResponse', () {
    final testTimestamp = DateTime(2025, 11, 11, 12, 0, 0);
    
    final sampleActivity1 = TimelineActivity(
      id: 'activity-1',
      type: 'meal',
      title: '1 apple',
      timestamp: testTimestamp,
      icon: '🍎',
      color: '#4CAF50',
      status: 'logged',
      details: {'calories': 95},
    );
    
    final sampleActivity2 = TimelineActivity(
      id: 'activity-2',
      type: 'workout',
      title: '30 min running',
      timestamp: testTimestamp,
      icon: '🏃',
      color: '#2196F3',
      status: 'completed',
      details: {'duration_minutes': 30, 'calories': 300},
    );
    
    final validResponseJson = {
      'activities': [
        {
          'id': 'activity-1',
          'type': 'meal',
          'title': '1 apple',
          'timestamp': '2025-11-11T12:00:00.000',
          'icon': '🍎',
          'color': '#4CAF50',
          'status': 'logged',
          'details': {'calories': 95},
        },
        {
          'id': 'activity-2',
          'type': 'workout',
          'title': '30 min running',
          'timestamp': '2025-11-11T12:00:00.000',
          'icon': '🏃',
          'color': '#2196F3',
          'status': 'completed',
          'details': {'duration_minutes': 30, 'calories': 300},
        },
      ],
      'total_count': 50,
      'has_more': true,
      'next_offset': 20,
    };
    
    group('Constructor', () {
      test('should create TimelineResponse with all fields', () {
        // Arrange & Act
        final response = TimelineResponse(
          activities: [sampleActivity1, sampleActivity2],
          totalCount: 50,
          hasMore: true,
          nextOffset: 20,
        );
        
        // Assert
        expect(response.activities.length, equals(2));
        expect(response.totalCount, equals(50));
        expect(response.hasMore, isTrue);
        expect(response.nextOffset, equals(20));
      });
      
      test('should create TimelineResponse with empty activities', () {
        // Arrange & Act
        final response = TimelineResponse(
          activities: [],
          totalCount: 0,
          hasMore: false,
          nextOffset: 0,
        );
        
        // Assert
        expect(response.activities, isEmpty);
        expect(response.totalCount, equals(0));
        expect(response.hasMore, isFalse);
      });
    });
    
    group('fromJson', () {
      test('should deserialize valid response JSON', () {
        // Act
        final response = TimelineResponse.fromJson(validResponseJson);
        
        // Assert
        expect(response.activities.length, equals(2));
        expect(response.activities[0].id, equals('activity-1'));
        expect(response.activities[1].id, equals('activity-2'));
        expect(response.totalCount, equals(50));
        expect(response.hasMore, isTrue);
        expect(response.nextOffset, equals(20));
      });
      
      test('should deserialize response with empty activities', () {
        // Arrange
        final emptyResponseJson = {
          'activities': [],
          'total_count': 0,
          'has_more': false,
          'next_offset': 0,
        };
        
        // Act
        final response = TimelineResponse.fromJson(emptyResponseJson);
        
        // Assert
        expect(response.activities, isEmpty);
        expect(response.totalCount, equals(0));
        expect(response.hasMore, isFalse);
      });
      
      test('should deserialize response with many activities', () {
        // Arrange
        final manyActivitiesJson = {
          'activities': List.generate(100, (i) => {
            'id': 'activity-$i',
            'type': 'meal',
            'title': 'Meal $i',
            'timestamp': '2025-11-11T12:00:00.000',
            'icon': '🍎',
            'color': '#4CAF50',
            'status': 'logged',
            'details': {'calories': 100},
          }),
          'total_count': 1000,
          'has_more': true,
          'next_offset': 100,
        };
        
        // Act
        final response = TimelineResponse.fromJson(manyActivitiesJson);
        
        // Assert
        expect(response.activities.length, equals(100));
        expect(response.totalCount, equals(1000));
      });
    });
    
    group('toJson', () {
      test('should serialize TimelineResponse to JSON', () {
        // Arrange
        final response = TimelineResponse(
          activities: [sampleActivity1, sampleActivity2],
          totalCount: 50,
          hasMore: true,
          nextOffset: 20,
        );
        
        // Act
        final json = response.toJson();
        
        // Assert
        expect(json['activities'], isA<List>());
        expect(json['activities'].length, equals(2));
        expect(json['total_count'], equals(50));
        expect(json['has_more'], isTrue);
        expect(json['next_offset'], equals(20));
      });
      
      test('should serialize empty response to JSON', () {
        // Arrange
        final response = TimelineResponse(
          activities: [],
          totalCount: 0,
          hasMore: false,
          nextOffset: 0,
        );
        
        // Act
        final json = response.toJson();
        
        // Assert
        expect(json['activities'], isEmpty);
        expect(json['total_count'], equals(0));
        expect(json['has_more'], isFalse);
      });
    });
    
    group('JSON Roundtrip', () {
      test('should maintain data integrity through serialize/deserialize cycle', () {
        // Arrange
        final original = TimelineResponse(
          activities: [sampleActivity1, sampleActivity2],
          totalCount: 50,
          hasMore: true,
          nextOffset: 20,
        );
        
        // Act
        final json = original.toJson();
        final deserialized = TimelineResponse.fromJson(json);
        
        // Assert
        expect(deserialized.activities.length, equals(original.activities.length));
        expect(deserialized.activities[0].id, equals(original.activities[0].id));
        expect(deserialized.activities[1].id, equals(original.activities[1].id));
        expect(deserialized.totalCount, equals(original.totalCount));
        expect(deserialized.hasMore, equals(original.hasMore));
        expect(deserialized.nextOffset, equals(original.nextOffset));
      });
    });
  });
}

