import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/timeline_provider.dart';
import '../../providers/auth_provider.dart';
import '../../models/timeline_activity.dart';
import 'widgets/timeline_filter_bar.dart';
import 'widgets/timeline_section_header.dart';
import 'widgets/timeline_item.dart';

class TimelineScreen extends StatefulWidget {
  const TimelineScreen({Key? key}) : super(key: key);

  @override
  State<TimelineScreen> createState() => _TimelineScreenState();
}

class _TimelineScreenState extends State<TimelineScreen> {
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadTimeline();
    });

    // Setup scroll listener for pagination
    _scrollController.addListener(_onScroll);
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    
    // 🔄 Auto-reload timeline when screen becomes visible
    final route = ModalRoute.of(context);
    if (route != null && route.isCurrent) {
      // Screen is now visible - refresh timeline
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          _loadTimeline();
        }
      });
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent * 0.9) {
      // User scrolled to 90% - load more
      final provider = context.read<TimelineProvider>();
      if (provider.hasMore && !provider.isLoading) {
        provider.loadMore();
      }
    }
  }

  Future<void> _loadTimeline() async {
    final provider = context.read<TimelineProvider>();
    final auth = context.read<AuthProvider>();
    
    // 🔴 PHASE 1: Start real-time listener (if enabled)
    if (auth.currentUser != null) {
      provider.startRealtimeListener(auth.currentUser!.uid);
    }
    
    // Fetch initial data (polling fallback if real-time disabled)
    await provider.fetchTimeline();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Timeline'),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // TODO: Show filter settings (date range picker)
              _showFilterSettings();
            },
          ),
        ],
      ),
      body: Consumer<TimelineProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading && provider.activities.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.error != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 48, color: Colors.red),
                  const SizedBox(height: 16),
                  Text('Error: ${provider.error}'),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _loadTimeline,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }

          if (provider.activities.isEmpty) {
            return _buildEmptyState();
          }

          final groupedActivities = provider.groupedActivities;

          return Column(
            children: [
              // Filter Bar
              TimelineFilterBar(
                selectedTypes: provider.selectedTypes,
                onToggle: (type) => provider.toggleFilter(type),
                activityCounts: provider.activityCounts,
              ),
              const Divider(height: 1),
              // Timeline List
              Expanded(
                child: RefreshIndicator(
                  onRefresh: provider.refresh,
                  child: ListView.builder(
                    controller: _scrollController,
                    itemCount: _calculateItemCount(groupedActivities, provider),
                    itemBuilder: (context, index) {
                      return _buildItem(context, index, groupedActivities, provider);
                    },
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  int _calculateItemCount(Map<String, List<TimelineActivity>> groupedActivities, TimelineProvider provider) {
    int count = 0;
    for (var section in groupedActivities.entries) {
      count++; // Section header
      // Only count activities if section is expanded
      if (provider.isSectionExpanded(section.key)) {
        count += section.value.length; // Activities
      }
    }
    if (provider.hasMore) {
      count++; // "View More" button
    }
    if (provider.isLoading && provider.activities.isNotEmpty) {
      count++; // Loading indicator
    }
    return count;
  }

  Widget _buildItem(
    BuildContext context,
    int index,
    Map<String, List<TimelineActivity>> groupedActivities,
    TimelineProvider provider,
  ) {
    int currentIndex = 0;
    bool isFirstSection = true;

    for (var section in groupedActivities.entries) {
      // Section header
      if (currentIndex == index) {
        final isExpanded = provider.isSectionExpanded(section.key);
        return TimelineSectionHeader(
          title: section.key,
          count: section.value.length,
          isFirst: isFirstSection,
          isExpanded: isExpanded,
          onTap: () => provider.toggleSection(section.key),
        );
      }
      currentIndex++;
      isFirstSection = false;

      // Activities in this section (only if expanded)
      final isSectionExpanded = provider.isSectionExpanded(section.key);
      if (isSectionExpanded) {
        for (int i = 0; i < section.value.length; i++) {
          if (currentIndex == index) {
            final activity = section.value[i];
            final isFirst = i == 0;
            final isLast = i == section.value.length - 1;

            // Wrap in RepaintBoundary for performance
            return RepaintBoundary(
              child: TimelineItem(
                activity: activity,
                isExpanded: provider.isExpanded(activity.id),
                onTap: () => provider.toggleExpanded(activity.id),
                isFirst: isFirst,
                isLast: isLast,
              ),
            );
          }
          currentIndex++;
        }
      }
    }

    // "View More" button
    if (provider.hasMore && currentIndex == index) {
      return Padding(
        padding: const EdgeInsets.all(16),
        child: Center(
          child: ElevatedButton(
            onPressed: provider.isLoading ? null : () => provider.loadMore(),
            child: const Text('View More'),
          ),
        ),
      );
    }

    // Loading indicator
    if (provider.isLoading && provider.activities.isNotEmpty && currentIndex == index) {
      return const Padding(
        padding: EdgeInsets.all(16),
        child: Center(child: CircularProgressIndicator()),
      );
    }

    return const SizedBox.shrink();
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.timeline, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            'No activities yet',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Start logging meals, workouts, and tasks!',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.of(context).pushNamed('/chat');
            },
            icon: const Icon(Icons.add),
            label: const Text('Log Activity'),
          ),
        ],
      ),
    );
  }

  void _showFilterSettings() {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Filter Settings',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              ListTile(
                leading: const Icon(Icons.date_range),
                title: const Text('Date Range'),
                subtitle: const Text('Select custom date range'),
                onTap: () {
                  Navigator.pop(context);
                  _showDateRangePicker();
                },
              ),
              ListTile(
                leading: const Icon(Icons.clear_all),
                title: const Text('Clear Filters'),
                subtitle: const Text('Show all activities'),
                onTap: () {
                  Navigator.pop(context);
                  context.read<TimelineProvider>().clearDateRange();
                },
              ),
            ],
          ),
        );
      },
    );
  }

  Future<void> _showDateRangePicker() async {
    final provider = context.read<TimelineProvider>();
    final DateTimeRange? picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime.now().subtract(const Duration(days: 365)),
      lastDate: DateTime.now(),
      initialDateRange: provider.startDate != null && provider.endDate != null
          ? DateTimeRange(start: provider.startDate!, end: provider.endDate!)
          : null,
    );

    if (picked != null) {
      provider.setDateRange(picked.start, picked.end);
    }
  }
}

