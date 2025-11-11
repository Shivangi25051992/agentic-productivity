import 'dart:ui';
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
      backgroundColor: const Color(0xFF0A0A0A), // Dark background
      appBar: AppBar(
        title: const Text(
          'Timeline',
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor: const Color(0xFF0A0A0A),
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings, color: Colors.white70),
            onPressed: () {
              // TODO: Show filter settings (date range picker)
              _showFilterSettings();
            },
          ),
        ],
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              const Color(0xFF0A0A0A),
              const Color(0xFF1A1A2A),
            ],
          ),
        ),
        child: Consumer<TimelineProvider>(
          builder: (context, provider, child) {
            if (provider.isLoading && provider.activities.isEmpty) {
              return const Center(
                child: CircularProgressIndicator(
                  color: Colors.blue,
                ),
              );
            }

            if (provider.error != null) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.error_outline, size: 48, color: Colors.redAccent),
                    const SizedBox(height: 16),
                    Text(
                      'Error: ${provider.error}',
                      style: const TextStyle(color: Colors.white70),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: _loadTimeline,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue,
                        foregroundColor: Colors.white,
                      ),
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
                // Timeline List
                Expanded(
                  child: RefreshIndicator(
                    onRefresh: provider.refresh,
                    color: Colors.blue,
                    backgroundColor: const Color(0xFF1A1A1A),
                    child: ListView.builder(
                      controller: _scrollController,
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
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
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue.withOpacity(0.2),
              foregroundColor: Colors.blue,
              side: BorderSide(color: Colors.blue.withOpacity(0.3)),
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
            ),
            child: const Text('View More'),
          ),
        ),
      );
    }

    // Loading indicator
    if (provider.isLoading && provider.activities.isNotEmpty && currentIndex == index) {
      return const Padding(
        padding: EdgeInsets.all(16),
        child: Center(
          child: CircularProgressIndicator(color: Colors.blue),
        ),
      );
    }

    return const SizedBox.shrink();
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                colors: [
                  Colors.blue.withOpacity(0.2),
                  Colors.purple.withOpacity(0.2),
                ],
              ),
            ),
            child: const Icon(
              Icons.timeline,
              size: 64,
              color: Colors.blue,
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'No activities yet',
            style: TextStyle(
              fontSize: 20,
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Start logging meals, workouts, and tasks!',
            style: TextStyle(
              fontSize: 14,
              color: Colors.white.withOpacity(0.6),
            ),
          ),
          const SizedBox(height: 32),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.of(context).pushNamed('/chat');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(24),
              ),
            ),
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

