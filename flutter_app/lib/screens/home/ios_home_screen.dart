import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/dashboard_provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/profile_provider.dart';
import '../../utils/constants.dart';
import '../../widgets/dashboard/water_widget.dart';
import '../../widgets/dashboard/supplement_widget.dart';

/// iOS-Optimized Home Screen
/// Features:
/// - Center-stage conversational chat
/// - Horizontal swipeable metric cards
/// - Collapsed insights (expandable)
/// - Zero regression: Uses same providers/APIs as web version
class IosHomeScreen extends StatefulWidget {
  const IosHomeScreen({Key? key}) : super(key: key);

  @override
  State<IosHomeScreen> createState() => _IosHomeScreenState();
}

class _IosHomeScreenState extends State<IosHomeScreen> {
  bool _isInsightsExpanded = false;
  final PageController _metricsPageController = PageController(viewportFraction: 0.85);
  int _currentMetricPage = 0;

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
    await dashboard.fetchDashboardData();
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.watch<ProfileProvider>();
    final userName = profile.profile?.name?.split(' ').first ?? 'there';

    return Scaffold(
      backgroundColor: AppConstants.bgLight,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _refreshData,
          child: CustomScrollView(
            physics: const BouncingScrollPhysics(),
            slivers: [
              // Compact Header
              _buildCompactHeader(userName),
              
              // Chat Bubble (Center Stage)
              _buildChatBubble(),
              
              // Horizontal Swipeable Metrics
              _buildSwipeableMetrics(),
              
              // Collapsible Insights
              _buildCollapsibleInsights(),
              
              // Quick Actions
              _buildQuickActions(),
              
              // Today's Content
              _buildTodaysContent(),
            ],
          ),
        ),
      ),
    );
  }

  /// Compact Header - Single line
  Widget _buildCompactHeader(String userName) {
    return SliverToBoxAdapter(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              AppConstants.primary.withOpacity(0.1),
              Colors.transparent,
            ],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: Row(
          children: [
            const Icon(Icons.waving_hand, size: 20),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Hi, $userName!',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1F2937),
                    ),
                  ),
                  Text(
                    _getFormattedDate(),
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
            // Profile icon
            GestureDetector(
              onTap: () => Navigator.of(context).pushNamed('/profile/edit'),
              child: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppConstants.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.person_outline,
                  size: 20,
                  color: AppConstants.primary,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Center-Stage Chat Bubble
  Widget _buildChatBubble() {
    return SliverToBoxAdapter(
      child: GestureDetector(
        onTap: () => Navigator.of(context).pushNamed('/chat'),
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                AppConstants.primary.withOpacity(0.1),
                AppConstants.primary.withOpacity(0.05),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: AppConstants.primary.withOpacity(0.3),
              width: 1.5,
            ),
          ),
          child: Column(
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppConstants.primary.withOpacity(0.2),
                      shape: BoxShape.circle,
                    ),
                    child: Text(
                      AppConstants.aiEmoji,
                      style: const TextStyle(fontSize: 24),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Chat with ${AppConstants.aiName}',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1F2937),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Log meals, track progress, get insights',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(
                    Icons.arrow_forward_ios,
                    size: 16,
                    color: AppConstants.primary,
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Icon(Icons.chat_bubble_outline, size: 18, color: Colors.grey[400]),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Type, speak, or scan...',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[500],
                        ),
                      ),
                    ),
                    Icon(Icons.mic_none, size: 20, color: AppConstants.primary),
                    const SizedBox(width: 8),
                    Icon(Icons.camera_alt_outlined, size: 20, color: AppConstants.primary),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Horizontal Swipeable Metrics
  Widget _buildSwipeableMetrics() {
    return Consumer<DashboardProvider>(
      builder: (context, dashboard, _) {
        if (dashboard.isLoading) {
          return const SliverToBoxAdapter(
            child: Center(
              child: Padding(
                padding: EdgeInsets.all(20.0),
                child: CircularProgressIndicator(),
              ),
            ),
          );
        }

        final stats = dashboard.stats;
        
        return SliverToBoxAdapter(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Your Progress',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1F2937),
                      ),
                    ),
                    Row(
                      children: List.generate(4, (index) {
                        return Container(
                          margin: const EdgeInsets.only(left: 4),
                          width: 6,
                          height: 6,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: _currentMetricPage == index
                                ? AppConstants.primary
                                : Colors.grey[300],
                          ),
                        );
                      }),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                height: 140,
                child: PageView(
                  controller: _metricsPageController,
                  onPageChanged: (index) {
                    setState(() => _currentMetricPage = index);
                  },
                  children: [
                    _buildMetricCard(
                      icon: '🔥',
                      label: 'Calories',
                      value: '${stats.caloriesConsumed}',
                      target: '${stats.caloriesGoal}',
                      unit: 'kcal',
                      progress: stats.caloriesProgress,
                      color: Colors.orange,
                    ),
                    _buildMetricCard(
                      icon: '💪',
                      label: 'Protein',
                      value: '${stats.proteinConsumed}g',
                      target: '${stats.proteinGoal}g',
                      unit: '',
                      progress: stats.proteinProgress,
                      color: Colors.blue,
                    ),
                    _buildMetricCard(
                      icon: '💧',
                      label: 'Water',
                      value: '${stats.waterGlasses}',
                      target: '${stats.waterGoal}',
                      unit: 'glasses',
                      progress: stats.waterProgress,
                      color: Colors.cyan,
                    ),
                    _buildMetricCard(
                      icon: '🚶',
                      label: 'Steps',
                      value: '${stats.stepsCompleted}',
                      target: '10000',
                      unit: 'steps',
                      progress: stats.stepsCompleted / 10000,
                      color: Colors.green,
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildMetricCard({
    required String icon,
    required String label,
    required String value,
    required String target,
    required String unit,
    required double progress,
    required Color color,
  }) {
    final isOnTrack = progress >= 0.8;
    
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 8),
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
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(icon, style: const TextStyle(fontSize: 24)),
              const SizedBox(width: 8),
              Text(
                label,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF6B7280),
                ),
              ),
              const Spacer(),
              if (isOnTrack)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    '✓',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.green,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
          const Spacer(),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                value,
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
              const SizedBox(width: 4),
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  '/ $target',
                  style: const TextStyle(
                    fontSize: 14,
                    color: Color(0xFF9CA3AF),
                  ),
                ),
              ),
            ],
          ),
          if (unit.isNotEmpty)
            Text(
              unit,
              style: const TextStyle(
                fontSize: 12,
                color: Color(0xFF9CA3AF),
              ),
            ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: progress.clamp(0.0, 1.0),
              backgroundColor: color.withOpacity(0.1),
              valueColor: AlwaysStoppedAnimation<Color>(color),
              minHeight: 6,
            ),
          ),
        ],
      ),
    );
  }

  /// Collapsible Insights Panel
  Widget _buildCollapsibleInsights() {
    return Consumer<DashboardProvider>(
      builder: (context, dashboard, _) {
        final insights = dashboard.insights;
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
                  onTap: () {
                    setState(() => _isInsightsExpanded = !_isInsightsExpanded);
                  },
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          const Color(0xFF8B5CF6).withOpacity(0.1),
                          const Color(0xFF06B6D4).withOpacity(0.1),
                        ],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: const Color(0xFF8B5CF6).withOpacity(0.3),
                        width: 1,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Text(
                              '🆙',
                              style: TextStyle(fontSize: 20),
                            ),
                            const SizedBox(width: 8),
                            const Expanded(
                              child: Text(
                                'How You\'re Leveling Up',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF1F2937),
                                ),
                              ),
                            ),
                            Icon(
                              _isInsightsExpanded
                                  ? Icons.keyboard_arrow_up
                                  : Icons.keyboard_arrow_down,
                              color: const Color(0xFF8B5CF6),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          primaryInsight.title,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF374151),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          primaryInsight.message,
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
                          insight.title,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF374151),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          insight.message,
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

  /// Quick Actions
  Widget _buildQuickActions() {
    return SliverToBoxAdapter(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '🎯 Quick Actions',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1F2937),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildQuickActionButton(
                    icon: Icons.restaurant_menu,
                    label: 'Log Meal',
                    onTap: () => Navigator.of(context).pushNamed('/chat'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildQuickActionButton(
                    icon: Icons.fitness_center,
                    label: 'Log Workout',
                    onTap: () => Navigator.of(context).pushNamed('/chat'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: AppConstants.primary.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: AppConstants.primary.withOpacity(0.3),
            width: 1,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 18, color: AppConstants.primary),
            const SizedBox(width: 8),
            Text(
              label,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: AppConstants.primary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Today's Content (Meals, Water, Supplements)
  Widget _buildTodaysContent() {
    return SliverList(
      delegate: SliverChildListDelegate([
        const SizedBox(height: 16),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            '📊 Today\'s Summary',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937),
            ),
          ),
        ),
        const SizedBox(height: 16),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20),
          child: WaterWidget(),
        ),
        const SizedBox(height: 16),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20),
          child: SupplementWidget(),
        ),
        const SizedBox(height: 80), // Space for bottom nav
      ]),
    );
  }

  String _getFormattedDate() {
    final now = DateTime.now();
    final weekday = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][now.weekday - 1];
    final month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][now.month - 1];
    return '$weekday, $month ${now.day}';
  }
}

