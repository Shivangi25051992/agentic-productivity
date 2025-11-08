import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/dashboard_provider.dart';
import '../../providers/profile_provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/constants.dart';
import '../chat/chat_screen.dart';

/// iOS Home Screen - Variant 2: Hybrid Recommended
/// 
/// Features:
/// - Bottom sheet chat expansion (smooth transition)
/// - Calorie ring (hybrid: Apple rings + MFP numbers)
/// - Activity feed (unified timeline)
/// - Quick stats bar (compact water/workouts)
class IosHomeScreenV2Hybrid extends StatefulWidget {
  const IosHomeScreenV2Hybrid({super.key});

  @override
  State<IosHomeScreenV2Hybrid> createState() => _IosHomeScreenV2HybridState();
}

class _IosHomeScreenV2HybridState extends State<IosHomeScreenV2Hybrid> with SingleTickerProviderStateMixin {
  final PageController _metricsPageController = PageController();
  int _currentMetricPage = 0;
  bool _isInsightsExpanded = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _refreshData();
    });
  }

  @override
  void dispose() {
    _metricsPageController.dispose();
    super.dispose();
  }

  Future<void> _refreshData() async {
    final dashboard = context.read<DashboardProvider>();
    final auth = context.read<AuthProvider>();
    await dashboard.fetchDailyStats(auth);
  }

  /// Show chat as bottom sheet (smooth expansion)
  void _showChatBottomSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.9,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) => Container(
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: Column(
            children: [
              // Handle bar
              Container(
                margin: const EdgeInsets.only(top: 12, bottom: 8),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              // Chat header
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                child: Row(
                  children: [
                    Text(
                      '${AppConstants.aiEmoji} Chat with ${AppConstants.aiName}',
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),
              ),
              const Divider(height: 1),
              // Chat screen
              const Expanded(
                child: ChatScreen(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.watch<ProfileProvider>();
    final userName = profile.profile?.name?.split(' ').first ?? 'there';

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      body: RefreshIndicator(
        onRefresh: _refreshData,
        child: CustomScrollView(
          slivers: [
            _buildCompactHeader(userName),
            _buildChatBubble(),
            _buildCalorieRingCard(),
            _buildOtherMetricsRow(),
            _buildActivityFeed(),
            _buildCollapsibleInsights(),
            const SliverToBoxAdapter(child: SizedBox(height: 100)),
          ],
        ),
      ),
    );
  }

  /// Compact Header
  Widget _buildCompactHeader(String userName) {
    return SliverToBoxAdapter(
      child: Container(
        padding: const EdgeInsets.fromLTRB(20, 60, 20, 16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '👋 Hi, $userName!',
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1F2937),
                  ),
                ),
                Text(
                  _getFormattedDate(),
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
            GestureDetector(
              onTap: () => Navigator.pushNamed(context, '/profile'),
              child: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: const Color(0xFF6366F1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.person, color: Colors.white, size: 24),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Chat Bubble (Tap to expand as bottom sheet)
  Widget _buildChatBubble() {
    return SliverToBoxAdapter(
      child: GestureDetector(
        onTap: _showChatBottomSheet,
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF6366F1).withOpacity(0.3),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Center(
                  child: Text('🤖', style: TextStyle(fontSize: 24)),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Chat with ${AppConstants.aiName}',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Log meals, track progress, get insights...',
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.white.withOpacity(0.9),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.arrow_forward_ios, color: Colors.white, size: 16),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Calorie Ring Card (Hybrid: Ring + Numbers)
  Widget _buildCalorieRingCard() {
    return SliverToBoxAdapter(
      child: Consumer<DashboardProvider>(
        builder: (context, dashboard, _) {
          final stats = dashboard.stats;
          final progress = stats.caloriesProgress;
          final remaining = stats.caloriesRemaining;
          final consumed = stats.caloriesConsumed;
          final burned = stats.caloriesBurned;

          return Container(
            margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    const Text(
                      '🔥 Calories',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1F2937),
                      ),
                    ),
                    const Spacer(),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: progress >= 1.0
                            ? Colors.red.withOpacity(0.1)
                            : progress >= 0.8
                                ? Colors.green.withOpacity(0.1)
                                : Colors.orange.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        progress >= 1.0
                            ? '⚠️ Over'
                            : progress >= 0.8
                                ? '✅ On Track'
                                : '🎯 Good',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: progress >= 1.0
                              ? Colors.red[700]
                              : progress >= 0.8
                                  ? Colors.green[700]
                                  : Colors.orange[700],
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                // Ring with center number
                SizedBox(
                  width: 200,
                  height: 200,
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      // Background ring
                      SizedBox(
                        width: 200,
                        height: 200,
                        child: CircularProgressIndicator(
                          value: 1.0,
                          strokeWidth: 20,
                          backgroundColor: Colors.grey[200],
                          valueColor: AlwaysStoppedAnimation(Colors.grey[200]!),
                        ),
                      ),
                      // Progress ring
                      SizedBox(
                        width: 200,
                        height: 200,
                        child: CircularProgressIndicator(
                          value: progress.clamp(0.0, 1.0),
                          strokeWidth: 20,
                          backgroundColor: Colors.transparent,
                          valueColor: AlwaysStoppedAnimation(
                            progress >= 1.0
                                ? Colors.red
                                : progress >= 0.8
                                    ? Colors.green
                                    : Colors.orange,
                          ),
                        ),
                      ),
                      // Center text
                      Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            remaining >= 0 ? '$remaining' : '${-remaining}',
                            style: const TextStyle(
                              fontSize: 48,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF1F2937),
                            ),
                          ),
                          Text(
                            remaining >= 0 ? 'remaining' : 'over',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                // Breakdown
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildCalorieBreakdown('🍽️', 'Eaten', consumed),
                    Container(width: 1, height: 40, color: Colors.grey[300]),
                    _buildCalorieBreakdown('💪', 'Burned', burned),
                    Container(width: 1, height: 40, color: Colors.grey[300]),
                    _buildCalorieBreakdown('🎯', 'Goal', stats.caloriesGoal),
                  ],
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildCalorieBreakdown(String emoji, String label, int value) {
    return Column(
      children: [
        Text(emoji, style: const TextStyle(fontSize: 20)),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(height: 2),
        Text(
          '$value',
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Color(0xFF1F2937),
          ),
        ),
      ],
    );
  }

  /// Other Metrics Row (Compact)
  Widget _buildOtherMetricsRow() {
    return SliverToBoxAdapter(
      child: Consumer<DashboardProvider>(
        builder: (context, dashboard, _) {
          final stats = dashboard.stats;
          return Container(
            margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            child: Row(
              children: [
                Expanded(
                  child: _buildCompactMetric(
                    '💪',
                    'Protein',
                    '${stats.proteinG.toInt()}g',
                    '${stats.proteinGoal.toInt()}g',
                    stats.proteinProgress,
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildCompactMetric(
                    '💧',
                    'Water',
                    '${(stats.waterMl / 250).toInt()}',
                    '${(stats.waterGoal / 250).toInt()}',
                    stats.waterProgress,
                    Colors.cyan,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildCompactMetric(
                    '🚶',
                    'Steps',
                    '0',
                    '10k',
                    0.0,
                    Colors.green,
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildCompactMetric(String emoji, String label, String value, String target, double progress, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Text(emoji, style: const TextStyle(fontSize: 24)),
          const SizedBox(height: 8),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937),
            ),
          ),
          Text(
            '/ $target',
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey[500],
            ),
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: progress.clamp(0.0, 1.0),
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation(color),
              minHeight: 4,
            ),
          ),
        ],
      ),
    );
  }

  /// Activity Feed (Unified Timeline)
  Widget _buildActivityFeed() {
    return SliverToBoxAdapter(
      child: Consumer<DashboardProvider>(
        builder: (context, dashboard, _) {
          final activities = dashboard.stats.activities;

          return Container(
            margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Text(
                      '🏃 Today\'s Activity',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1F2937),
                      ),
                    ),
                    const Spacer(),
                    TextButton(
                      onPressed: () => Navigator.pushNamed(context, '/timeline'),
                      child: const Text('View All →'),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                if (activities.isEmpty)
                  Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        children: [
                          Text(
                            '📝',
                            style: const TextStyle(fontSize: 48),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            'No activity yet today',
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.grey[600],
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Start logging to see your timeline!',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[500],
                            ),
                          ),
                        ],
                      ),
                    ),
                  )
                else
                  ...activities.take(5).map((activity) => _buildActivityItem(activity)),
                const SizedBox(height: 12),
                // Quick action button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _showChatBottomSheet,
                    icon: const Icon(Icons.add),
                    label: const Text('Quick Log'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF6366F1),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildActivityItem(ActivityItem activity) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F9FA),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Text(activity.emoji, style: const TextStyle(fontSize: 24)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  activity.title,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF1F2937),
                  ),
                ),
                if (activity.subtitle != null)
                  Text(
                    activity.subtitle!,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
              ],
            ),
          ),
          Text(
            _formatTime(activity.timestamp),
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  String _formatTime(DateTime time) {
    final hour = time.hour > 12 ? time.hour - 12 : time.hour;
    final period = time.hour >= 12 ? 'PM' : 'AM';
    final minute = time.minute.toString().padLeft(2, '0');
    return '$hour:$minute $period';
  }

  /// Collapsible Insights Panel
  Widget _buildCollapsibleInsights() {
    return Consumer<DashboardProvider>(
      builder: (context, dashboard, _) {
        final stats = dashboard.stats;
        
        // Generate simple insights from stats
        final insights = _generateInsights(stats);
        if (insights.isEmpty) {
          return const SliverToBoxAdapter(child: SizedBox.shrink());
        }

        // Show only the first insight by default
        final primaryInsight = insights.first;

        return SliverToBoxAdapter(
          child: Container(
            margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            child: Column(
              children: [
                GestureDetector(
                  onTap: () => setState(() => _isInsightsExpanded = !_isInsightsExpanded),
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFFF3E8FF), Color(0xFFE0E7FF)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: const Color(0xFF8B5CF6).withOpacity(0.2),
                        width: 1,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Text(
                              '🆙 How You\'re Leveling Up',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF1F2937),
                              ),
                            ),
                            const Spacer(),
                            Icon(
                              _isInsightsExpanded ? Icons.expand_less : Icons.expand_more,
                              color: const Color(0xFF8B5CF6),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          primaryInsight['title'] as String,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF374151),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          primaryInsight['message'] as String,
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey[600],
                          ),
                          maxLines: _isInsightsExpanded ? null : 2,
                          overflow: _isInsightsExpanded ? null : TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ),
                if (_isInsightsExpanded && insights.length > 1)
                  ...insights.skip(1).map((insight) => Container(
                    margin: const EdgeInsets.only(top: 12),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: Colors.grey[200]!,
                        width: 1,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          insight['title'] as String,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF374151),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          insight['message'] as String,
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  )),
              ],
            ),
          ),
        );
      },
    );
  }

  String _getFormattedDate() {
    final now = DateTime.now();
    final weekday = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][now.weekday - 1];
    final month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][now.month - 1];
    return '$weekday, $month ${now.day}';
  }

  /// Generate simple insights from stats
  List<Map<String, String>> _generateInsights(DailyStats stats) {
    final insights = <Map<String, String>>[];

    // Calorie deficit insight
    if (stats.isInDeficit) {
      final deficit = stats.caloriesGoal - stats.netCalories;
      insights.add({
        'title': '🎯 Perfect Deficit!',
        'message': 'You\'re $deficit kcal in deficit - ideal for healthy weight loss!',
      });
    } else if (stats.netCalories > stats.caloriesGoal) {
      final surplus = stats.netCalories - stats.caloriesGoal;
      insights.add({
        'title': '⚠️ Calorie Surplus',
        'message': 'You\'re $surplus kcal over your goal. Try logging a workout!',
      });
    }

    // Protein insight
    if (stats.proteinProgress >= 0.8) {
      insights.add({
        'title': '💪 Great Protein!',
        'message': 'You\'ve hit ${(stats.proteinProgress * 100).toInt()}% of your protein goal!',
      });
    } else if (stats.proteinRemaining > 50) {
      insights.add({
        'title': '🍗 Boost Your Protein',
        'message': 'You need ${stats.proteinRemaining.toInt()}g more protein. Try adding chicken breast, eggs, or Greek yogurt.',
      });
    }

    // Water insight
    if (stats.waterProgress >= 0.8) {
      insights.add({
        'title': '💧 Well Hydrated!',
        'message': 'Great job staying hydrated today!',
      });
    } else if (stats.waterProgress < 0.5) {
      insights.add({
        'title': '💧 Drink More Water',
        'message': 'You\'re only at ${(stats.waterProgress * 100).toInt()}% of your water goal. Stay hydrated!',
      });
    }

    // Default insight if none generated
    if (insights.isEmpty) {
      insights.add({
        'title': '🌟 Keep Going!',
        'message': 'Log your meals and activities to get personalized insights.',
      });
    }

    return insights;
  }
}


