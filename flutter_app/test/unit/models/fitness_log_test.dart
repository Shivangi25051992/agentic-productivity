/// Enterprise-Grade Unit Tests for FitnessLogModel
/// 
/// Testing Strategy:
/// - Test all public methods
/// - Test edge cases and error conditions
/// - Test JSON serialization/deserialization
/// - Achieve 100% code coverage
/// 
/// Quality Standards:
/// - Clear test names (Given-When-Then pattern)
/// - Isolated tests (no dependencies)
/// - Fast execution (< 100ms per test)
/// - Deterministic results

import 'package:flutter_test/flutter_test.dart';
import 'package:ai_productivity_app/models/fitness_log.dart';

void main() {
  group('FitnessLogModel', () {
    // Test Fixtures (Arrange)
    final testTimestamp = DateTime(2025, 11, 11, 12, 0, 0);
    
    final validMealJson = {
      'log_id': 'test-meal-123',
      'user_id': 'user-456',
      'log_type': 'meal',
      'content': '1 apple',
      'calories': 95,
      'ai_parsed_data': {
        'items': ['apple'],
        'quantity': 1,
      },
      'timestamp': '2025-11-11T12:00:00.000',
    };
    
    final validWorkoutJson = {
      'log_id': 'test-workout-789',
      'user_id': 'user-456',
      'log_type': 'workout',
      'content': '30 min running',
      'calories': 300,
      'ai_parsed_data': {
        'duration': 30,
        'type': 'running',
      },
      'timestamp': '2025-11-11T12:00:00.000',
    };
    
    group('Constructor', () {
      test('should create FitnessLogModel with all required fields', () {
        // Arrange & Act
        final log = FitnessLogModel(
          id: 'test-123',
          userId: 'user-456',
          type: FitnessLogType.meal,
          content: '1 apple',
          timestamp: testTimestamp,
        );
        
        // Assert
        expect(log.id, equals('test-123'));
        expect(log.userId, equals('user-456'));
        expect(log.type, equals(FitnessLogType.meal));
        expect(log.content, equals('1 apple'));
        expect(log.timestamp, equals(testTimestamp));
        expect(log.calories, isNull);
        expect(log.parsedData, isNull);
      });
      
      test('should create FitnessLogModel with optional fields', () {
        // Arrange & Act
        final log = FitnessLogModel(
          id: 'test-123',
          userId: 'user-456',
          type: FitnessLogType.meal,
          content: '1 apple',
          calories: 95,
          parsedData: {'items': ['apple']},
          timestamp: testTimestamp,
        );
        
        // Assert
        expect(log.calories, equals(95));
        expect(log.parsedData, isNotNull);
        expect(log.parsedData!['items'], equals(['apple']));
      });
      
      test('should create workout type FitnessLogModel', () {
        // Arrange & Act
        final log = FitnessLogModel(
          id: 'test-workout',
          userId: 'user-456',
          type: FitnessLogType.workout,
          content: '30 min running',
          calories: 300,
          timestamp: testTimestamp,
        );
        
        // Assert
        expect(log.type, equals(FitnessLogType.workout));
        expect(log.content, equals('30 min running'));
        expect(log.calories, equals(300));
      });
    });
    
    group('fromJson', () {
      test('should deserialize valid meal JSON', () {
        // Act
        final log = FitnessLogModel.fromJson(validMealJson);
        
        // Assert
        expect(log.id, equals('test-meal-123'));
        expect(log.userId, equals('user-456'));
        expect(log.type, equals(FitnessLogType.meal));
        expect(log.content, equals('1 apple'));
        expect(log.calories, equals(95));
        expect(log.parsedData, isNotNull);
        expect(log.parsedData!['items'], equals(['apple']));
        expect(log.timestamp, equals(DateTime.parse('2025-11-11T12:00:00.000')));
      });
      
      test('should deserialize valid workout JSON', () {
        // Act
        final log = FitnessLogModel.fromJson(validWorkoutJson);
        
        // Assert
        expect(log.id, equals('test-workout-789'));
        expect(log.type, equals(FitnessLogType.workout));
        expect(log.content, equals('30 min running'));
        expect(log.calories, equals(300));
        expect(log.parsedData!['duration'], equals(30));
      });
      
      test('should handle alternative JSON field names (log_id vs id)', () {
        // Arrange
        final jsonWithId = {
          'id': 'test-alt-123',  // Alternative field name
          'user_id': 'user-456',
          'log_type': 'meal',
          'content': '1 apple',
          'timestamp': '2025-11-11T12:00:00.000',
        };
        
        // Act
        final log = FitnessLogModel.fromJson(jsonWithId);
        
        // Assert
        expect(log.id, equals('test-alt-123'));
      });
      
      test('should handle alternative JSON field names (userId vs user_id)', () {
        // Arrange
        final jsonWithUserId = {
          'log_id': 'test-123',
          'userId': 'user-alt-789',  // Alternative field name
          'log_type': 'meal',
          'content': '1 apple',
          'timestamp': '2025-11-11T12:00:00.000',
        };
        
        // Act
        final log = FitnessLogModel.fromJson(jsonWithUserId);
        
        // Assert
        expect(log.userId, equals('user-alt-789'));
      });
      
      test('should handle alternative JSON field names (parsedData vs ai_parsed_data)', () {
        // Arrange
        final jsonWithParsedData = {
          'log_id': 'test-123',
          'user_id': 'user-456',
          'log_type': 'meal',
          'content': '1 apple',
          'parsedData': {'items': ['apple']},  // Alternative field name
          'timestamp': '2025-11-11T12:00:00.000',
        };
        
        // Act
        final log = FitnessLogModel.fromJson(jsonWithParsedData);
        
        // Assert
        expect(log.parsedData, isNotNull);
        expect(log.parsedData!['items'], equals(['apple']));
      });
      
      test('should default to meal type when log_type is missing', () {
        // Arrange
        final jsonWithoutType = {
          'log_id': 'test-123',
          'user_id': 'user-456',
          'content': '1 apple',
          'timestamp': '2025-11-11T12:00:00.000',
        };
        
        // Act
        final log = FitnessLogModel.fromJson(jsonWithoutType);
        
        // Assert
        expect(log.type, equals(FitnessLogType.meal));
      });
      
      test('should default to meal type for unknown log_type', () {
        // Arrange
        final jsonWithUnknownType = {
          'log_id': 'test-123',
          'user_id': 'user-456',
          'log_type': 'unknown_type',
          'content': '1 apple',
          'timestamp': '2025-11-11T12:00:00.000',
        };
        
        // Act
        final log = FitnessLogModel.fromJson(jsonWithUnknownType);
        
        // Assert
        expect(log.type, equals(FitnessLogType.meal));
      });
      
      test('should handle null calories', () {
        // Arrange
        final jsonWithoutCalories = {
          'log_id': 'test-123',
          'user_id': 'user-456',
          'log_type': 'meal',
          'content': '1 apple',
          'timestamp': '2025-11-11T12:00:00.000',
        };
        
        // Act
        final log = FitnessLogModel.fromJson(jsonWithoutCalories);
        
        // Assert
        expect(log.calories, isNull);
      });
      
      test('should handle null parsedData', () {
        // Arrange
        final jsonWithoutParsedData = {
          'log_id': 'test-123',
          'user_id': 'user-456',
          'log_type': 'meal',
          'content': '1 apple',
          'timestamp': '2025-11-11T12:00:00.000',
        };
        
        // Act
        final log = FitnessLogModel.fromJson(jsonWithoutParsedData);
        
        // Assert
        expect(log.parsedData, isNull);
      });
      
      test('should handle case-insensitive log_type (WORKOUT)', () {
        // Arrange
        final jsonWithUppercaseType = {
          'log_id': 'test-123',
          'user_id': 'user-456',
          'log_type': 'WORKOUT',
          'content': '30 min running',
          'timestamp': '2025-11-11T12:00:00.000',
        };
        
        // Act
        final log = FitnessLogModel.fromJson(jsonWithUppercaseType);
        
        // Assert
        expect(log.type, equals(FitnessLogType.workout));
      });
      
      test('should handle case-insensitive log_type (Workout)', () {
        // Arrange
        final jsonWithMixedCaseType = {
          'log_id': 'test-123',
          'user_id': 'user-456',
          'log_type': 'Workout',
          'content': '30 min running',
          'timestamp': '2025-11-11T12:00:00.000',
        };
        
        // Act
        final log = FitnessLogModel.fromJson(jsonWithMixedCaseType);
        
        // Assert
        expect(log.type, equals(FitnessLogType.workout));
      });
    });
    
    group('toJson', () {
      test('should serialize FitnessLogModel to JSON with all fields', () {
        // Arrange
        final log = FitnessLogModel(
          id: 'test-123',
          userId: 'user-456',
          type: FitnessLogType.meal,
          content: '1 apple',
          calories: 95,
          parsedData: {'items': ['apple']},
          timestamp: testTimestamp,
        );
        
        // Act
        final json = log.toJson();
        
        // Assert
        expect(json['log_id'], equals('test-123'));
        expect(json['user_id'], equals('user-456'));
        expect(json['log_type'], equals('meal'));
        expect(json['content'], equals('1 apple'));
        expect(json['calories'], equals(95));
        expect(json['ai_parsed_data'], isNotNull);
        expect(json['ai_parsed_data']['items'], equals(['apple']));
        expect(json['timestamp'], equals('2025-11-11T12:00:00.000'));
      });
      
      test('should serialize workout type to JSON', () {
        // Arrange
        final log = FitnessLogModel(
          id: 'test-workout',
          userId: 'user-456',
          type: FitnessLogType.workout,
          content: '30 min running',
          calories: 300,
          timestamp: testTimestamp,
        );
        
        // Act
        final json = log.toJson();
        
        // Assert
        expect(json['log_type'], equals('workout'));
        expect(json['content'], equals('30 min running'));
        expect(json['calories'], equals(300));
      });
      
      test('should omit null values from JSON', () {
        // Arrange
        final log = FitnessLogModel(
          id: 'test-123',
          userId: 'user-456',
          type: FitnessLogType.meal,
          content: '1 apple',
          timestamp: testTimestamp,
          // calories and parsedData are null
        );
        
        // Act
        final json = log.toJson();
        
        // Assert
        expect(json.containsKey('calories'), isFalse);
        expect(json.containsKey('ai_parsed_data'), isFalse);
      });
      
      test('should preserve timestamp precision in JSON', () {
        // Arrange
        final preciseTimestamp = DateTime(2025, 11, 11, 12, 30, 45, 123);
        final log = FitnessLogModel(
          id: 'test-123',
          userId: 'user-456',
          type: FitnessLogType.meal,
          content: '1 apple',
          timestamp: preciseTimestamp,
        );
        
        // Act
        final json = log.toJson();
        
        // Assert
        expect(json['timestamp'], equals('2025-11-11T12:30:45.123'));
      });
    });
    
    group('JSON Roundtrip', () {
      test('should maintain data integrity through serialize/deserialize cycle', () {
        // Arrange
        final original = FitnessLogModel(
          id: 'test-roundtrip',
          userId: 'user-roundtrip',
          type: FitnessLogType.meal,
          content: 'Complex meal with multiple items',
          calories: 450,
          parsedData: {
            'items': ['chicken', 'rice', 'broccoli'],
            'meal_type': 'lunch',
            'confidence': 0.95,
          },
          timestamp: testTimestamp,
        );
        
        // Act
        final json = original.toJson();
        final deserialized = FitnessLogModel.fromJson(json);
        
        // Assert
        expect(deserialized.id, equals(original.id));
        expect(deserialized.userId, equals(original.userId));
        expect(deserialized.type, equals(original.type));
        expect(deserialized.content, equals(original.content));
        expect(deserialized.calories, equals(original.calories));
        expect(deserialized.parsedData, equals(original.parsedData));
        expect(deserialized.timestamp, equals(original.timestamp));
      });
      
      test('should maintain workout data through roundtrip', () {
        // Arrange
        final original = FitnessLogModel(
          id: 'test-workout-roundtrip',
          userId: 'user-456',
          type: FitnessLogType.workout,
          content: '45 min HIIT workout',
          calories: 500,
          parsedData: {
            'duration': 45,
            'type': 'HIIT',
            'intensity': 'high',
          },
          timestamp: testTimestamp,
        );
        
        // Act
        final json = original.toJson();
        final deserialized = FitnessLogModel.fromJson(json);
        
        // Assert
        expect(deserialized.type, equals(FitnessLogType.workout));
        expect(deserialized.calories, equals(500));
        expect(deserialized.parsedData!['duration'], equals(45));
        expect(deserialized.parsedData!['type'], equals('HIIT'));
      });
    });
    
    group('Edge Cases', () {
      test('should handle empty content string', () {
        // Arrange & Act
        final log = FitnessLogModel(
          id: 'test-empty',
          userId: 'user-456',
          type: FitnessLogType.meal,
          content: '',
          timestamp: testTimestamp,
        );
        
        // Assert
        expect(log.content, equals(''));
      });
      
      test('should handle very long content string', () {
        // Arrange
        final longContent = 'A' * 10000;  // 10,000 characters
        
        // Act
        final log = FitnessLogModel(
          id: 'test-long',
          userId: 'user-456',
          type: FitnessLogType.meal,
          content: longContent,
          timestamp: testTimestamp,
        );
        
        // Assert
        expect(log.content.length, equals(10000));
      });
      
      test('should handle zero calories', () {
        // Arrange & Act
        final log = FitnessLogModel(
          id: 'test-zero',
          userId: 'user-456',
          type: FitnessLogType.meal,
          content: 'Water',
          calories: 0,
          timestamp: testTimestamp,
        );
        
        // Assert
        expect(log.calories, equals(0));
      });
      
      test('should handle negative calories (edge case)', () {
        // Arrange & Act
        final log = FitnessLogModel(
          id: 'test-negative',
          userId: 'user-456',
          type: FitnessLogType.meal,
          content: 'Test',
          calories: -100,  // Edge case - should be handled by validation elsewhere
          timestamp: testTimestamp,
        );
        
        // Assert
        expect(log.calories, equals(-100));
      });
      
      test('should handle very large calorie values', () {
        // Arrange & Act
        final log = FitnessLogModel(
          id: 'test-large',
          userId: 'user-456',
          type: FitnessLogType.meal,
          content: 'Massive meal',
          calories: 999999,
          timestamp: testTimestamp,
        );
        
        // Assert
        expect(log.calories, equals(999999));
      });
      
      test('should handle empty parsedData map', () {
        // Arrange & Act
        final log = FitnessLogModel(
          id: 'test-empty-data',
          userId: 'user-456',
          type: FitnessLogType.meal,
          content: '1 apple',
          parsedData: {},
          timestamp: testTimestamp,
        );
        
        // Assert
        expect(log.parsedData, isNotNull);
        expect(log.parsedData!.isEmpty, isTrue);
      });
      
      test('should handle complex nested parsedData', () {
        // Arrange
        final complexData = {
          'items': [
            {'name': 'chicken', 'quantity': 200, 'unit': 'g'},
            {'name': 'rice', 'quantity': 150, 'unit': 'g'},
          ],
          'nutrition': {
            'protein': 45.5,
            'carbs': 60.2,
            'fat': 12.3,
          },
          'metadata': {
            'confidence': 0.95,
            'source': 'llm',
            'model': 'gpt-4',
          },
        };
        
        // Act
        final log = FitnessLogModel(
          id: 'test-complex',
          userId: 'user-456',
          type: FitnessLogType.meal,
          content: 'Complex meal',
          parsedData: complexData,
          timestamp: testTimestamp,
        );
        
        // Assert
        expect(log.parsedData, isNotNull);
        expect(log.parsedData!['items'], isA<List>());
        expect(log.parsedData!['nutrition'], isA<Map>());
        expect(log.parsedData!['metadata']['confidence'], equals(0.95));
      });
    });
    
    group('Type Conversion', () {
      test('_typeFrom should handle all valid workout variations', () {
        // Test lowercase
        expect(
          FitnessLogModel.fromJson({
            ...validMealJson,
            'log_type': 'workout',
          }).type,
          equals(FitnessLogType.workout),
        );
        
        // Test uppercase
        expect(
          FitnessLogModel.fromJson({
            ...validMealJson,
            'log_type': 'WORKOUT',
          }).type,
          equals(FitnessLogType.workout),
        );
        
        // Test mixed case
        expect(
          FitnessLogModel.fromJson({
            ...validMealJson,
            'log_type': 'Workout',
          }).type,
          equals(FitnessLogType.workout),
        );
      });
      
      test('_typeFrom should default to meal for any other value', () {
        final testCases = ['meal', 'MEAL', 'Meal', 'food', 'snack', '', 'invalid'];
        
        for (final testCase in testCases) {
          expect(
            FitnessLogModel.fromJson({
              ...validMealJson,
              'log_type': testCase,
            }).type,
            equals(FitnessLogType.meal),
            reason: 'Failed for input: $testCase',
          );
        }
      });
    });
  });
}

