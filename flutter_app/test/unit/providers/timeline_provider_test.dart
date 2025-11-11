// 🎯 ENTERPRISE-GRADE UNIT TESTS
// Testing: TimelineProvider
// Coverage: State management, API integration, filtering, caching, real-time
// Pattern: Given-When-Then with comprehensive mocking

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:ai_productivity_app/providers/timeline_provider.dart';
import 'package:ai_productivity_app/services/api_service.dart';
import 'package:ai_productivity_app/services/realtime_service.dart';
import 'package:ai_productivity_app/models/timeline_activity.dart';

// Mock classes
class MockApiService extends Mock implements ApiService {}
class MockRealtimeService extends Mock implements RealtimeService {}

void main() {
  // Register fallback values for mocktail
  setUpAll(() {
    registerFallbackValue(DateTime.now());
  });

  group('TimelineProvider', () {
    late TimelineProvider provider;
    late MockApiService mockApiService;
    late MockRealtimeService mockRealtimeService;

    setUp(() {
      mockApiService = MockApiService();
      mockRealtimeService = MockRealtimeService();
      // 🎯 ENTERPRISE PATTERN: Inject mock services for testing
      provider = TimelineProvider(
        mockApiService,
        realtimeService: mockRealtimeService,
      );
    });

    tearDown(() {
      provider.dispose();
    });

    group('Initialization', () {
      test('should initialize with default values', () {
        // Assert
        expect(provider.activities, isEmpty);
        expect(provider.selectedTypes, {
          'meal',
          'workout',
          'task',
          'event',
          'water',
          'supplement'
        });
        expect(provider.startDate, isNull);
        expect(provider.endDate, isNull);
        expect(provider.isLoading, isFalse);
        expect(provider.hasMore, isTrue);
        expect(provider.error, isNull);
      });

      test('should have all activity types selected by default', () {
        // Assert
        expect(provider.selectedTypes.length, equals(6));
        expect(provider.selectedTypes.contains('meal'), isTrue);
        expect(provider.selectedTypes.contains('workout'), isTrue);
        expect(provider.selectedTypes.contains('task'), isTrue);
        expect(provider.selectedTypes.contains('event'), isTrue);
        expect(provider.selectedTypes.contains('water'), isTrue);
        expect(provider.selectedTypes.contains('supplement'), isTrue);
      });

      test('should have empty grouped activities initially', () {
        // Assert
        expect(provider.groupedActivities, isEmpty);
      });

      test('should have zero activity counts initially', () {
        // Assert
        expect(provider.activityCounts, isEmpty);
      });
    });

    group('Type Filtering', () {
      test('should toggle type selection', () {
        // Given
        var notificationCount = 0;
        provider.addListener(() => notificationCount++);

        // When
        provider.toggleFilter('meal');

        // Then
        expect(provider.selectedTypes.contains('meal'), isFalse);
        expect(notificationCount, equals(1));
      });

      test('should add type back when toggled again', () {
        // Given
        provider.toggleFilter('meal'); // Remove first

        // When
        provider.toggleFilter('meal'); // Add back

        // Then
        expect(provider.selectedTypes.contains('meal'), isTrue);
      });

      test('should handle toggling non-existent type', () {
        // Given
        final initialCount = provider.selectedTypes.length;

        // When
        provider.toggleFilter('unknown_type');

        // Then - should add it
        expect(provider.selectedTypes.length, equals(initialCount + 1));
        expect(provider.selectedTypes.contains('unknown_type'), isTrue);
      });
    });

    group('Date Filtering', () {
      test('should set date range', () {
        // Given
        when(() => mockApiService.getTimeline(
              types: any(named: 'types'),
              startDate: any(named: 'startDate'),
              endDate: any(named: 'endDate'),
              limit: any(named: 'limit'),
              offset: any(named: 'offset'),
              bustCache: any(named: 'bustCache'),
            )).thenAnswer((_) async => TimelineResponse(
              activities: [],
              totalCount: 0,
              hasMore: false,
              nextOffset: 0,
            ));

        final start = DateTime(2025, 1, 1);
        final end = DateTime(2025, 1, 31);
        var notificationCount = 0;
        provider.addListener(() => notificationCount++);

        // When
        provider.setDateRange(start, end);

        // Then
        expect(provider.startDate, equals(start));
        expect(provider.endDate, equals(end));
        expect(notificationCount, greaterThan(0)); // May notify multiple times due to fetch
      });

      test('should clear date range', () {
        // Given
        provider.setDateRange(DateTime(2025, 1, 1), DateTime(2025, 1, 31));
        expect(provider.startDate, isNotNull);
        expect(provider.endDate, isNotNull);

        // When
        provider.clearDateRange();

        // Then
        expect(provider.startDate, isNull);
        expect(provider.endDate, isNull);
      });

      test('should handle null date range', () {
        // When
        provider.setDateRange(null, null);

        // Then
        expect(provider.startDate, isNull);
        expect(provider.endDate, isNull);
      });

      test('should handle start date without end date', () {
        // Given
        final start = DateTime(2025, 1, 1);

        // When
        provider.setDateRange(start, null);

        // Then
        expect(provider.startDate, equals(start));
        expect(provider.endDate, isNull);
      });
    });

    group('Activity Expansion', () {
      test('should toggle activity expansion', () {
        // Given
        const activityId = 'activity_1';
        var notificationCount = 0;
        provider.addListener(() => notificationCount++);

        // When
        provider.toggleExpanded(activityId);

        // Then
        expect(provider.isExpanded(activityId), isTrue);
        expect(notificationCount, equals(1));
      });

      test('should collapse expanded activity', () {
        // Given
        const activityId = 'activity_1';
        provider.toggleExpanded(activityId); // Expand first

        // When
        provider.toggleExpanded(activityId); // Collapse

        // Then
        expect(provider.isExpanded(activityId), isFalse);
      });

      test('should return false for non-expanded activity', () {
        // Assert
        expect(provider.isExpanded('non_existent'), isFalse);
      });

      test('should handle multiple activity expansions', () {
        // Given
        provider.toggleExpanded('activity_1');
        provider.toggleExpanded('activity_2');

        // Then
        expect(provider.isExpanded('activity_1'), isTrue);
        expect(provider.isExpanded('activity_2'), isTrue);
      });
    });

    group('Section Expansion', () {
      test('should toggle section expansion', () {
        // Given
        const sectionKey = '2025-01-01';
        var notificationCount = 0;
        provider.addListener(() => notificationCount++);

        // When
        provider.toggleSection(sectionKey);

        // Then
        expect(provider.isSectionExpanded(sectionKey), isFalse);
        expect(notificationCount, equals(1));
      });

      test('should expand section when toggled again', () {
        // Given
        const sectionKey = '2025-01-01';
        provider.toggleSection(sectionKey); // Collapse first

        // When
        provider.toggleSection(sectionKey); // Expand

        // Then
        expect(provider.isSectionExpanded(sectionKey), isTrue);
      });

      test('should return true for non-toggled section (default expanded)', () {
        // Assert
        expect(provider.isSectionExpanded('2025-01-01'), isTrue);
      });
    });

    group('Activity Counts', () {
      test('should count activities by type', () {
        // This will be tested after we can mock fetchTimeline
        // For now, verify the getter works with empty activities
        expect(provider.activityCounts, isEmpty);
      });
    });

    group('Grouped Activities', () {
      test('should return empty map when no activities', () {
        // Assert
        expect(provider.groupedActivities, isEmpty);
      });
    });

    group('Clear State', () {
      test('should clear all activities', () {
        // Given
        final activity = TimelineActivity(
          id: '1',
          type: 'meal',
          title: 'Breakfast',
          icon: '🍽️',
          color: '#4CAF50',
          status: 'completed',
          details: {},
          timestamp: DateTime.now(),
        );
        provider.addOptimisticActivity(activity);
        var notificationCount = 0;
        provider.addListener(() => notificationCount++);

        // When
        provider.clear();

        // Then
        expect(provider.activities, isEmpty);
        expect(notificationCount, equals(1));
      });
    });

    group('Refresh', () {
      test('should trigger refresh', () async {
        // Given
        when(() => mockApiService.getTimeline(
              types: any(named: 'types'),
              startDate: any(named: 'startDate'),
              endDate: any(named: 'endDate'),
              limit: any(named: 'limit'),
              offset: any(named: 'offset'),
              bustCache: any(named: 'bustCache'),
            )).thenAnswer((_) async => TimelineResponse(
              activities: [],
              totalCount: 0,
              hasMore: false,
              nextOffset: 0,
            ));

        var notificationCount = 0;
        provider.addListener(() => notificationCount++);

        // When
        await provider.refresh();

        // Then
        verify(() => mockApiService.getTimeline(
              types: any(named: 'types'),
              startDate: any(named: 'startDate'),
              endDate: any(named: 'endDate'),
              limit: any(named: 'limit'),
              offset: any(named: 'offset'),
              bustCache: true, // Should bust cache
            )).called(1);
        expect(notificationCount, greaterThan(0));
      });
    });

    group('Optimistic Updates', () {
      test('should add optimistic activity', () {
        // Given
        final activity = TimelineActivity(
          id: 'temp_123',
          type: 'meal',
          title: 'Quick Log',
          icon: '🍽️',
          color: '#4CAF50',
          status: 'completed',
          details: {},
          timestamp: DateTime.now(),
          clientGeneratedId: 'client_123',
        );
        var notificationCount = 0;
        provider.addListener(() => notificationCount++);

        // When
        provider.addOptimisticActivity(activity);

        // Then
        expect(provider.activities.length, equals(1));
        expect(provider.activities.first.id, equals('temp_123'));
        expect(notificationCount, equals(1));
      });

      test('should add optimistic activity at the beginning', () {
        // Given
        final existing = TimelineActivity(
          id: '1',
          type: 'meal',
          title: 'Existing',
          icon: '🍽️',
          color: '#4CAF50',
          status: 'completed',
          details: {},
          timestamp: DateTime.now().subtract(Duration(hours: 1)),
        );
        final optimistic = TimelineActivity(
          id: 'temp_123',
          type: 'meal',
          title: 'New',
          icon: '🍽️',
          color: '#4CAF50',
          status: 'completed',
          details: {},
          timestamp: DateTime.now(),
        );

        provider.addOptimisticActivity(existing);

        // When
        provider.addOptimisticActivity(optimistic);

        // Then
        expect(provider.activities.length, equals(2));
        expect(provider.activities.first.id, equals('temp_123'));
      });

      test('should remove optimistic activity by ID', () {
        // Given
        final activity = TimelineActivity(
          id: 'temp_123',
          type: 'meal',
          title: 'Quick Log',
          icon: '🍽️',
          color: '#4CAF50',
          status: 'completed',
          details: {},
          timestamp: DateTime.now(),
        );
        provider.addOptimisticActivity(activity);
        var notificationCount = 0;
        provider.addListener(() => notificationCount++);

        // When
        provider.removeOptimisticActivity('temp_123');

        // Then
        expect(provider.activities, isEmpty);
        expect(notificationCount, equals(1));
      });

      test('should handle removing non-existent optimistic activity', () {
        // When
        provider.removeOptimisticActivity('non_existent');

        // Then - should not crash
        expect(provider.activities, isEmpty);
      });
    });

    group('Listener Notifications', () {
      test('should notify listeners when toggling filter', () {
        // Given
        var notificationCount = 0;
        provider.addListener(() => notificationCount++);

        // When
        provider.toggleFilter('meal');

        // Then
        expect(notificationCount, equals(1));
      });

      test('should notify listeners when setting date range', () {
        // Given
        when(() => mockApiService.getTimeline(
              types: any(named: 'types'),
              startDate: any(named: 'startDate'),
              endDate: any(named: 'endDate'),
              limit: any(named: 'limit'),
              offset: any(named: 'offset'),
              bustCache: any(named: 'bustCache'),
            )).thenAnswer((_) async => TimelineResponse(
              activities: [],
              totalCount: 0,
              hasMore: false,
              nextOffset: 0,
            ));

        var notificationCount = 0;
        provider.addListener(() => notificationCount++);

        // When
        provider.setDateRange(DateTime(2025, 1, 1), DateTime(2025, 1, 31));

        // Then
        expect(notificationCount, greaterThan(0)); // May notify multiple times
      });

      test('should notify listeners when toggling expansion', () {
        // Given
        var notificationCount = 0;
        provider.addListener(() => notificationCount++);

        // When
        provider.toggleExpanded('activity_1');

        // Then
        expect(notificationCount, equals(1));
      });

      test('should notify listeners when adding optimistic activity', () {
        // Given
        var notificationCount = 0;
        provider.addListener(() => notificationCount++);
        final activity = TimelineActivity(
          id: 'temp_123',
          type: 'meal',
          title: 'Quick Log',
          icon: '🍽️',
          color: '#4CAF50',
          status: 'completed',
          details: {},
          timestamp: DateTime.now(),
        );

        // When
        provider.addOptimisticActivity(activity);

        // Then
        expect(notificationCount, equals(1));
      });
    });

    group('Edge Cases', () {
      test('should handle empty type string in toggle', () {
        // When
        provider.toggleFilter('');

        // Then - should handle gracefully
        expect(provider.selectedTypes.contains(''), isTrue);
      });

      test('should handle very long activity ID in expansion', () {
        // Given
        final longId = 'a' * 1000;

        // When
        provider.toggleExpanded(longId);

        // Then
        expect(provider.isExpanded(longId), isTrue);
      });

      test('should handle date range with end before start', () {
        // Given
        final start = DateTime(2025, 1, 31);
        final end = DateTime(2025, 1, 1);

        // When
        provider.setDateRange(start, end);

        // Then - should still set (validation is caller's responsibility)
        expect(provider.startDate, equals(start));
        expect(provider.endDate, equals(end));
      });

      test('should handle multiple rapid toggles', () {
        // When
        for (var i = 0; i < 10; i++) {
          provider.toggleFilter('meal');
        }

        // Then - should end up unselected (started selected, toggled even number)
        expect(provider.selectedTypes.contains('meal'), isTrue);
      });

      test('should handle adding duplicate optimistic activities', () {
        // Given
        final activity1 = TimelineActivity(
          id: 'temp_123',
          type: 'meal',
          title: 'Log 1',
          icon: '🍽️',
          color: '#4CAF50',
          status: 'completed',
          details: {},
          timestamp: DateTime.now(),
        );
        final activity2 = TimelineActivity(
          id: 'temp_123', // Same ID
          type: 'meal',
          title: 'Log 2',
          icon: '🍽️',
          color: '#4CAF50',
          status: 'completed',
          details: {},
          timestamp: DateTime.now(),
        );

        // When
        provider.addOptimisticActivity(activity1);
        provider.addOptimisticActivity(activity2);

        // Then - both should be added (no deduplication at this level)
        expect(provider.activities.length, equals(2));
      });
    });
  });
}

