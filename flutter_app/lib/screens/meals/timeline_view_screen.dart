import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/dashboard_provider.dart';
import '../../providers/auth_provider.dart';

/// Timeline view showing all meals chronologically throughout the day
/// Provides a complete picture of eating patterns and timing
class TimelineViewScreen extends StatefulWidget {
  const TimelineViewScreen({Key? key}) : super(key: key);

  @override
  State<TimelineViewScreen> createState() => _TimelineViewScreenState();
}

class _TimelineViewScreenState extends State<TimelineViewScreen> {
  DateTime _selectedDate = DateTime.now();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final authProvider = context.read<AuthProvider>();
      await context.read<DashboardProvider>().fetchDailyStats(authProvider);
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime.now().subtract(const Duration(days: 365)),
      lastDate: DateTime.now(),
    );
    if (picked != null && picked != _selectedDate) {
      setState(() => _selectedDate = picked);
      // TODO: Load data for selected date
      _loadData();
    }
  }

  @override
  Widget build(BuildContext context) {
    final dashboardProvider = context.watch<DashboardProvider>();
    final activities = dashboardProvider.stats.activities
        .where((a) => a.type == 'meal')
        .toList()
      ..sort((a, b) => a.timestamp.compareTo(b.timestamp));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Meal Timeline'),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.calendar_today),
            onPressed: _selectDate,
            tooltip: 'Select date',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : activities.isEmpty
              ? _buildEmptyState()
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: CustomScrollView(
                    slivers: [
                      // Date header
                      SliverToBoxAdapter(
                        child: Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Theme.of(context).primaryColor.withOpacity(0.1),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    DateFormat('EEEE, MMMM d').format(_selectedDate),
                                    style: const TextStyle(
                                      fontSize: 20,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    '${activities.length} meal${activities.length != 1 ? 's' : ''} logged',
                                    style: TextStyle(
                                      fontSize: 14,
                                      color: Colors.grey.shade600,
                                    ),
                                  ),
                                ],
                              ),
                              _buildDailySummary(activities),
                            ],
                          ),
                        ),
                      ),

                      // Timeline
                      SliverPadding(
                        padding: const EdgeInsets.all(16),
                        sliver: SliverList(
                          delegate: SliverChildBuilderDelegate(
                            (context, index) {
                              final activity = activities[index];
                              final isFirst = index == 0;
                              final isLast = index == activities.length - 1;
                              
                              return _buildTimelineItem(
                                activity,
                                isFirst: isFirst,
                                isLast: isLast,
                              );
                            },
                            childCount: activities.length,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.restaurant_menu,
            size: 80,
            color: Colors.grey.shade300,
          ),
          const SizedBox(height: 16),
          Text(
            'No meals logged yet',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Start logging your meals to see your timeline',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade500,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => Navigator.of(context).pushNamed('/chat'),
            icon: const Icon(Icons.add),
            label: const Text('Log Food'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDailySummary(List<dynamic> activities) {
    int totalCalories = 0;
    double totalProtein = 0;

    for (final activity in activities) {
      final data = activity.data ?? {};
      totalCalories += (data['calories'] as num?)?.toInt() ?? 0;
      totalProtein += (data['protein_g'] as num?)?.toDouble() ?? 0;
    }

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            '$totalCalories kcal',
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.orange,
            ),
          ),
          Text(
            '${totalProtein.toStringAsFixed(0)}g protein',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTimelineItem(
    dynamic activity, {
    required bool isFirst,
    required bool isLast,
  }) {
    final data = activity.data ?? {};
    final description = data['description'] as String? ?? activity.title ?? 'Unknown';
    final calories = (data['calories'] as num?)?.toInt() ?? 0;
    final protein = (data['protein_g'] as num?)?.toDouble() ?? 0;
    final carbs = (data['carbs_g'] as num?)?.toDouble() ?? 0;
    final fat = (data['fat_g'] as num?)?.toDouble() ?? 0;
    final mealType = data['meal_type'] as String? ?? 'snack';
    final timestamp = activity.timestamp as DateTime;

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Timeline line
          SizedBox(
            width: 60,
            child: Column(
              children: [
                // Top line
                if (!isFirst)
                  Expanded(
                    child: Container(
                      width: 2,
                      color: Colors.grey.shade300,
                    ),
                  )
                else
                  const SizedBox(height: 8),

                // Time badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getMealColor(mealType),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    DateFormat('HH:mm').format(timestamp),
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),

                // Bottom line
                if (!isLast)
                  Expanded(
                    child: Container(
                      width: 2,
                      color: Colors.grey.shade300,
                    ),
                  )
                else
                  const SizedBox(height: 8),
              ],
            ),
          ),

          // Content card
          Expanded(
            child: Container(
              margin: const EdgeInsets.only(bottom: 16, left: 8),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: _getMealColor(mealType).withOpacity(0.3),
                  width: 2,
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Meal type badge
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: _getMealColor(mealType).withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              _getMealIcon(mealType),
                              style: const TextStyle(fontSize: 14),
                            ),
                            const SizedBox(width: 4),
                            Text(
                              _getMealLabel(mealType),
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color: _getMealColor(mealType),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Food description
                  Text(
                    description,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Macros
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _buildMacroChip('🔥', '$calories kcal', Colors.orange),
                      _buildMacroChip('💪', '${protein.toStringAsFixed(1)}g', Colors.red),
                      _buildMacroChip('🌾', '${carbs.toStringAsFixed(1)}g', Colors.blue),
                      _buildMacroChip('🥑', '${fat.toStringAsFixed(1)}g', Colors.purple),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMacroChip(String emoji, String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 12)),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  String _getMealIcon(String type) {
    switch (type) {
      case 'breakfast':
        return '🌅';
      case 'lunch':
        return '🌞';
      case 'snack':
        return '🍎';
      case 'dinner':
        return '🌙';
      default:
        return '🍽️';
    }
  }

  String _getMealLabel(String type) {
    return type[0].toUpperCase() + type.substring(1);
  }

  Color _getMealColor(String type) {
    switch (type) {
      case 'breakfast':
        return Colors.orange;
      case 'lunch':
        return Colors.green;
      case 'snack':
        return Colors.blue;
      case 'dinner':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }
}

