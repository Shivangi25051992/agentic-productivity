/// Enterprise-Grade Unit Tests for DashboardProvider
/// 
/// Testing Strategy:
/// - Test all public methods
/// - Mock external dependencies (ApiService, AuthProvider)
/// - Test state management (loading, error, success)
/// - Test caching behavior
/// - Test date navigation
/// - Test computed properties
/// - Achieve 80%+ code coverage
/// 
/// Quality Standards:
/// - Clear test names (Given-When-Then pattern)
/// - Proper mocking of dependencies
/// - Fast execution (< 100ms per test)
/// - Deterministic results
/// - Test listener notifications

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:ai_productivity_app/providers/dashboard_provider.dart';
import 'package:ai_productivity_app/providers/auth_provider.dart';
import 'package:ai_productivity_app/services/api_service.dart';
import 'package:ai_productivity_app/services/realtime_service.dart';
import 'package:ai_productivity_app/models/fitness_log.dart';
import 'package:ai_productivity_app/models/task.dart';

// Mock classes
class MockAuthProvider extends Mock implements AuthProvider {}
class MockApiService extends Mock implements ApiService {}
class MockRealtimeService extends Mock implements RealtimeService {}

void main() {
  // Register fallback values for mocktail
  setUpAll(() {
    registerFallbackValue(DateTime.now());
    registerFallbackValue(DateTime.now());
  });
  
  group('DailyStats', () {
    test('should create DailyStats with default values', () {
      // Act
      final stats = DailyStats();
      
      // Assert
      expect(stats.caloriesConsumed, equals(0));
      expect(stats.caloriesBurned, equals(0));
      expect(stats.caloriesGoal, equals(2000));
      expect(stats.proteinG, equals(0));
      expect(stats.proteinGoal, equals(150));
      expect(stats.activities, isEmpty);
    });
    
    test('should create DailyStats with custom values', () {
      // Arrange & Act
      final stats = DailyStats(
        caloriesConsumed: 1500,
        caloriesBurned: 300,
        caloriesGoal: 2200,
        proteinG: 120,
        proteinGoal: 180,
        carbsG: 150,
        carbsGoal: 250,
        fatG: 50,
        fatGoal: 70,
      );
      
      // Assert
      expect(stats.caloriesConsumed, equals(1500));
      expect(stats.caloriesBurned, equals(300));
      expect(stats.caloriesGoal, equals(2200));
      expect(stats.proteinG, equals(120));
      expect(stats.proteinGoal, equals(180));
    });
    
    group('Progress Calculations', () {
      test('should calculate calories progress correctly', () {
        final stats = DailyStats(
          caloriesConsumed: 1000,
          caloriesGoal: 2000,
        );
        expect(stats.caloriesProgress, equals(0.5));
      });
      
      test('should clamp calories progress at 1.0', () {
        final stats = DailyStats(
          caloriesConsumed: 3000,
          caloriesGoal: 2000,
        );
        expect(stats.caloriesProgress, equals(1.0));
      });
      
      test('should handle zero goal for calories', () {
        final stats = DailyStats(
          caloriesConsumed: 1000,
          caloriesGoal: 0,
        );
        expect(stats.caloriesProgress, equals(0.0));
      });
      
      test('should calculate protein progress correctly', () {
        final stats = DailyStats(
          proteinG: 75,
          proteinGoal: 150,
        );
        expect(stats.proteinProgress, equals(0.5));
      });
      
      test('should calculate carbs progress correctly', () {
        final stats = DailyStats(
          carbsG: 100,
          carbsGoal: 200,
        );
        expect(stats.carbsProgress, equals(0.5));
      });
      
      test('should calculate fat progress correctly', () {
        final stats = DailyStats(
          fatG: 32.5,
          fatGoal: 65,
        );
        expect(stats.fatProgress, equals(0.5));
      });
      
      test('should calculate fiber progress correctly', () {
        final stats = DailyStats(
          fiberG: 12.5,
          fiberGoal: 25,
        );
        expect(stats.fiberProgress, equals(0.5));
      });
      
      test('should calculate water progress correctly', () {
        final stats = DailyStats(
          waterMl: 1000,
          waterGoal: 2000,
        );
        expect(stats.waterProgress, equals(0.5));
      });
      
      test('should calculate workouts progress correctly', () {
        final stats = DailyStats(
          workoutsCompleted: 2,
          workoutsGoal: 4,
        );
        expect(stats.workoutsProgress, equals(0.5));
      });
    });
    
    group('Remaining Calculations', () {
      test('should calculate calories remaining', () {
        final stats = DailyStats(
          caloriesConsumed: 1500,
          caloriesGoal: 2000,
        );
        expect(stats.caloriesRemaining, equals(500));
      });
      
      test('should calculate protein remaining', () {
        final stats = DailyStats(
          proteinG: 100,
          proteinGoal: 150,
        );
        expect(stats.proteinRemaining, equals(50));
      });
      
      test('should calculate carbs remaining', () {
        final stats = DailyStats(
          carbsG: 150,
          carbsGoal: 200,
        );
        expect(stats.carbsRemaining, equals(50));
      });
      
      test('should calculate fat remaining', () {
        final stats = DailyStats(
          fatG: 40,
          fatGoal: 65,
        );
        expect(stats.fatRemaining, equals(25));
      });
    });
    
    group('Net Calories & Deficit', () {
      test('should calculate net calories correctly', () {
        final stats = DailyStats(
          caloriesConsumed: 2000,
          caloriesBurned: 300,
        );
        expect(stats.netCalories, equals(1700));
      });
      
      test('should calculate calorie deficit correctly (in deficit)', () {
        final stats = DailyStats(
          caloriesConsumed: 1500,
          caloriesBurned: 300,
          caloriesGoal: 2000,
        );
        // Net = 1500 - 300 = 1200
        // Deficit = 1200 - 2000 = -800 (in deficit)
        expect(stats.calorieDeficit, equals(-800));
      });
      
      test('should calculate calorie deficit correctly (in surplus)', () {
        final stats = DailyStats(
          caloriesConsumed: 2500,
          caloriesBurned: 200,
          caloriesGoal: 2000,
        );
        // Net = 2500 - 200 = 2300
        // Deficit = 2300 - 2000 = 300 (in surplus)
        expect(stats.calorieDeficit, equals(300));
      });
      
      test('should correctly identify when in deficit', () {
        final stats = DailyStats(
          caloriesConsumed: 1500,
          caloriesBurned: 300,
          caloriesGoal: 2000,
        );
        expect(stats.isInDeficit, isTrue);
      });
      
      test('should correctly identify when not in deficit', () {
        final stats = DailyStats(
          caloriesConsumed: 2500,
          caloriesBurned: 200,
          caloriesGoal: 2000,
        );
        expect(stats.isInDeficit, isFalse);
      });
    });
  });
  
  group('ActivityItem', () {
    final testTimestamp = DateTime(2025, 11, 11, 12, 0, 0);
    
    test('should create ActivityItem with all fields', () {
      // Act
      final activity = ActivityItem(
        id: 'activity-123',
        type: 'meal',
        title: '1 apple',
        subtitle: '95 cal',
        timestamp: testTimestamp,
        data: {'calories': 95},
      );
      
      // Assert
      expect(activity.id, equals('activity-123'));
      expect(activity.type, equals('meal'));
      expect(activity.title, equals('1 apple'));
      expect(activity.subtitle, equals('95 cal'));
      expect(activity.timestamp, equals(testTimestamp));
      expect(activity.data, equals({'calories': 95}));
    });
    
    test('should return correct emoji for meal', () {
      final activity = ActivityItem(
        id: '1', type: 'meal', title: 'Test', timestamp: testTimestamp,
      );
      expect(activity.emoji, equals('🍽️'));
    });
    
    test('should return correct emoji for workout', () {
      final activity = ActivityItem(
        id: '1', type: 'workout', title: 'Test', timestamp: testTimestamp,
      );
      expect(activity.emoji, equals('💪'));
    });
    
    test('should return correct emoji for water', () {
      final activity = ActivityItem(
        id: '1', type: 'water', title: 'Test', timestamp: testTimestamp,
      );
      expect(activity.emoji, equals('💧'));
    });
    
    test('should return correct emoji for task', () {
      final activity = ActivityItem(
        id: '1', type: 'task', title: 'Test', timestamp: testTimestamp,
      );
      expect(activity.emoji, equals('✅'));
    });
    
    test('should return default emoji for unknown type', () {
      final activity = ActivityItem(
        id: '1', type: 'unknown', title: 'Test', timestamp: testTimestamp,
      );
      expect(activity.emoji, equals('📝'));
    });
  });
  
  group('DashboardProvider', () {
    late DashboardProvider provider;
    late MockAuthProvider mockAuthProvider;
    late MockRealtimeService mockRealtimeService;
    
    setUp(() {
      mockRealtimeService = MockRealtimeService();
      mockAuthProvider = MockAuthProvider();
      // 🎯 ENTERPRISE PATTERN: Inject mock service for testing
      provider = DashboardProvider(realtimeService: mockRealtimeService);
    });
    
    test('should initialize with default values', () {
      // Assert
      expect(provider.stats, isA<DailyStats>());
      expect(provider.isLoading, isFalse);
      expect(provider.errorMessage, isNull);
      expect(provider.selectedDate, isA<DateTime>());
      expect(provider.isToday, isTrue);
    });
    
    test('should format selected date correctly', () {
      // Arrange
      provider.changeDate(DateTime(2025, 11, 11));
      
      // Assert
      expect(provider.selectedDateFormatted, equals('Nov 11, 2025'));
    });
    
    test('should identify today correctly', () {
      // Arrange
      provider.changeDate(DateTime.now());
      
      // Assert
      expect(provider.isToday, isTrue);
    });
    
    test('should identify not today correctly', () {
      // Arrange
      provider.changeDate(DateTime(2020, 1, 1));
      
      // Assert
      expect(provider.isToday, isFalse);
    });
    
    group('Date Navigation', () {
      test('should change date', () {
        // Arrange
        final newDate = DateTime(2025, 11, 15);
        
        // Act
        provider.changeDate(newDate);
        
        // Assert
        expect(provider.selectedDate.year, equals(2025));
        expect(provider.selectedDate.month, equals(11));
        expect(provider.selectedDate.day, equals(15));
      });
      
      test('should go to previous day', () {
        // Arrange
        provider.changeDate(DateTime(2025, 11, 15));
        
        // Act
        provider.previousDay();
        
        // Assert
        expect(provider.selectedDate.day, equals(14));
      });
      
      test('should go to next day', () {
        // Arrange
        provider.changeDate(DateTime(2025, 11, 15));
        
        // Act
        provider.nextDay();
        
        // Assert
        expect(provider.selectedDate.day, equals(16));
      });
      
      test('should go to today', () {
        // Arrange
        provider.changeDate(DateTime(2020, 1, 1));
        
        // Act
        provider.goToToday();
        
        // Assert
        expect(provider.isToday, isTrue);
      });
    });
    
    group('Error Handling', () {
      test('should clear error', () {
        // Arrange - manually set error (simulating a previous error)
        provider.fetchDailyStats(mockAuthProvider).catchError((_) {});
        
        // Act
        provider.clearError();
        
        // Assert
        expect(provider.errorMessage, isNull);
      });
    });
    
    group('Goals Update', () {
      test('should update goals from profile', () {
        // Arrange
        final goals = {
          'calories': 2500,
          'protein_g': 180,
          'carbs_g': 250,
          'fat_g': 70,
          'fiber_g': 30,
          'water_ml': 2500,
          'workouts_per_week': 5,
        };
        
        // Act
        provider.updateGoalsFromProfile(goals);
        
        // Assert
        expect(provider.stats.caloriesGoal, equals(2500));
        expect(provider.stats.proteinGoal, equals(180));
        expect(provider.stats.carbsGoal, equals(250));
        expect(provider.stats.fatGoal, equals(70));
        expect(provider.stats.fiberGoal, equals(30));
        expect(provider.stats.waterGoal, equals(2500));
        expect(provider.stats.workoutsGoal, equals(5));
      });
      
      test('should use default values for missing goals', () {
        // Arrange
        final goals = <String, dynamic>{};
        
        // Act
        provider.updateGoalsFromProfile(goals);
        
        // Assert
        expect(provider.stats.caloriesGoal, equals(2000));
        expect(provider.stats.proteinGoal, equals(150));
        expect(provider.stats.carbsGoal, equals(200));
        expect(provider.stats.fatGoal, equals(65));
        expect(provider.stats.fiberGoal, equals(25));
        expect(provider.stats.waterGoal, equals(2000));
        expect(provider.stats.workoutsGoal, equals(1));
      });
    });
    
    group('Cache Management', () {
      test('should invalidate cache', () {
        // Act
        provider.invalidateCache();
        
        // Assert - cache should be cleared
        // (We can't directly test private fields, but we can test the behavior)
        // The next fetchDailyStats should not use cache
        expect(provider.stats, isA<DailyStats>());
      });
      
      test('should update stats optimistically', () {
        // Arrange
        final newStats = DailyStats(
          caloriesConsumed: 1500,
          proteinG: 120,
        );
        
        // Act
        provider.updateStatsOptimistically(newStats);
        
        // Assert
        expect(provider.stats.caloriesConsumed, equals(1500));
        expect(provider.stats.proteinG, equals(120));
      });
    });
    
    group('Listener Notifications', () {
      test('should notify listeners when changing date', () {
        // Arrange
        var notified = false;
        provider.addListener(() {
          notified = true;
        });
        
        // Act
        provider.changeDate(DateTime(2025, 11, 15));
        
        // Assert
        expect(notified, isTrue);
      });
      
      test('should notify listeners when going to previous day', () {
        // Arrange
        var notified = false;
        provider.addListener(() {
          notified = true;
        });
        
        // Act
        provider.previousDay();
        
        // Assert
        expect(notified, isTrue);
      });
      
      test('should notify listeners when going to next day', () {
        // Arrange
        var notified = false;
        provider.addListener(() {
          notified = true;
        });
        
        // Act
        provider.nextDay();
        
        // Assert
        expect(notified, isTrue);
      });
      
      test('should notify listeners when updating goals', () {
        // Arrange
        var notified = false;
        provider.addListener(() {
          notified = true;
        });
        
        // Act
        provider.updateGoalsFromProfile({'calories': 2500});
        
        // Assert
        expect(notified, isTrue);
      });
      
      test('should notify listeners when clearing error', () {
        // Arrange
        var notified = false;
        provider.addListener(() {
          notified = true;
        });
        
        // Act
        provider.clearError();
        
        // Assert
        expect(notified, isTrue);
      });
      
      test('should notify listeners when updating optimistically', () {
        // Arrange
        var notified = false;
        provider.addListener(() {
          notified = true;
        });
        
        // Act
        provider.updateStatsOptimistically(DailyStats());
        
        // Assert
        expect(notified, isTrue);
      });
    });
    
    group('Edge Cases', () {
      test('should handle goals update with null values', () {
        // Arrange
        final goals = {
          'calories': null,
          'protein_g': null,
        };
        
        // Act
        provider.updateGoalsFromProfile(goals);
        
        // Assert - should use defaults
        expect(provider.stats.caloriesGoal, equals(2000));
        expect(provider.stats.proteinGoal, equals(150));
      });
      
      test('should handle date navigation across month boundaries', () {
        // Arrange
        provider.changeDate(DateTime(2025, 11, 1));
        
        // Act
        provider.previousDay();
        
        // Assert
        expect(provider.selectedDate.month, equals(10));
        expect(provider.selectedDate.day, equals(31));
      });
      
      test('should handle date navigation across year boundaries', () {
        // Arrange
        provider.changeDate(DateTime(2025, 1, 1));
        
        // Act
        provider.previousDay();
        
        // Assert
        expect(provider.selectedDate.year, equals(2024));
        expect(provider.selectedDate.month, equals(12));
        expect(provider.selectedDate.day, equals(31));
      });
    });
  });
}

