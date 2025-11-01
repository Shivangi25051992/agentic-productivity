import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';

import '../../providers/dashboard_provider.dart';
import '../../providers/profile_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/dashboard/macro_pie_chart.dart';
import '../../widgets/dashboard/progress_bar_card.dart';
import '../../widgets/dashboard/activity_timeline.dart';
import '../../widgets/dashboard/activity_rings.dart';
import '../../widgets/dashboard/calorie_deficit_card.dart';

class EnhancedHomeScreen extends StatefulWidget {
  const EnhancedHomeScreen({super.key});

  @override
  State<EnhancedHomeScreen> createState() => _EnhancedHomeScreenState();
}

class _EnhancedHomeScreenState extends State<EnhancedHomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    final auth = context.read<AuthProvider>();
    final profile = context.read<ProfileProvider>();
    final dashboard = context.read<DashboardProvider>();

    // Load profile if not loaded
    if (profile.profile == null) {
      await profile.fetchProfile(auth);
    }

    // Update goals from profile
    if (profile.profile != null) {
      dashboard.updateGoalsFromProfile(profile.profile!.dailyGoals.toJson());
    }

    // Load daily stats
    await dashboard.fetchDailyStats(auth);
  }

  Future<void> _refreshData() async {
    final auth = context.read<AuthProvider>();
    final dashboard = context.read<DashboardProvider>();
    await dashboard.fetchDailyStats(auth);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer3<DashboardProvider, ProfileProvider, AuthProvider>(
        builder: (context, dashboard, profile, auth, child) {
          return RefreshIndicator(
            onRefresh: _refreshData,
            child: CustomScrollView(
              slivers: [
                // App Bar with date selector
                SliverAppBar(
                  floating: true,
                  pinned: true,
                  expandedHeight: 120,
                  automaticallyImplyLeading: false,
                  leading: Builder(
                    builder: (context) => IconButton(
                      icon: const Icon(Icons.menu, color: Colors.white),
                      onPressed: () => Scaffold.of(context).openDrawer(),
                    ),
                  ),
                  actions: [
                    // Logout button
                    PopupMenuButton<String>(
                      icon: const Icon(Icons.account_circle, color: Colors.white),
                      tooltip: 'Account',
                      onSelected: (value) async {
                        if (value == 'logout') {
                          final shouldLogout = await showDialog<bool>(
                            context: context,
                            builder: (context) => AlertDialog(
                              title: const Text('Logout'),
                              content: const Text('Are you sure you want to logout?'),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.of(context).pop(false),
                                  child: const Text('Cancel'),
                                ),
                                FilledButton(
                                  onPressed: () => Navigator.of(context).pop(true),
                                  child: const Text('Logout'),
                                ),
                              ],
                            ),
                          );
                          
                          if (shouldLogout == true && context.mounted) {
                            await auth.signOut();
                            if (context.mounted) {
                              Navigator.of(context).pushNamedAndRemoveUntil(
                                '/login',
                                (route) => false,
                              );
                            }
                          }
                        }
                      },
                      itemBuilder: (context) => [
                        PopupMenuItem<String>(
                          enabled: false,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                profile.profile?.name ?? auth.currentUser?.email ?? 'User',
                                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              if (auth.currentUser?.email != null)
                                Text(
                                  auth.currentUser!.email!,
                                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                                  ),
                                ),
                            ],
                          ),
                        ),
                        const PopupMenuDivider(),
                        const PopupMenuItem<String>(
                          value: 'logout',
                          child: Row(
                            children: [
                              Icon(Icons.logout, size: 20),
                              SizedBox(width: 12),
                              Text('Logout'),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                  flexibleSpace: FlexibleSpaceBar(
                    background: Container(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            Theme.of(context).colorScheme.primary,
                            Theme.of(context).colorScheme.secondary,
                          ],
                        ),
                      ),
                      child: SafeArea(
                        child: Padding(
                          padding: const EdgeInsets.fromLTRB(60.0, 16.0, 60.0, 16.0), // Add left/right padding to avoid overlap
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.end,
                            children: [
                              Text(
                                'Hi, ${profile.profile?.name ?? "there"}! 👋',
                                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                    ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              const SizedBox(height: 8),
                              Row(
                                children: [
                                  IconButton(
                                    onPressed: () {
                                      dashboard.previousDay();
                                      _refreshData();
                                    },
                                    icon: const Icon(Icons.chevron_left, color: Colors.white),
                                  ),
                                  Expanded(
                                    child: Text(
                                      dashboard.selectedDateFormatted,
                                      textAlign: TextAlign.center,
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 16,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ),
                                  IconButton(
                                    onPressed: dashboard.isToday
                                        ? null
                                        : () {
                                            dashboard.nextDay();
                                            _refreshData();
                                          },
                                    icon: Icon(
                                      Icons.chevron_right,
                                      color: dashboard.isToday ? Colors.white38 : Colors.white,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),

                // Content
                if (dashboard.isLoading)
                  const SliverFillRemaining(
                    child: Center(child: CircularProgressIndicator()),
                  )
                else
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Calorie Deficit Card (Net Calories)
                          CalorieDeficitCard(
                            caloriesConsumed: dashboard.stats.caloriesConsumed,
                            caloriesBurned: dashboard.stats.caloriesBurned,
                            caloriesGoal: dashboard.stats.caloriesGoal,
                            netCalories: dashboard.stats.netCalories,
                            deficit: dashboard.stats.calorieDeficit,
                            isInDeficit: dashboard.stats.isInDeficit,
                          ),
                          const SizedBox(height: 24),

                          // Activity Rings Section (Apple Watch Style)
                          Text(
                            'Today\'s Progress',
                            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                          const SizedBox(height: 16),
                          Container(
                            padding: const EdgeInsets.all(24),
                            decoration: BoxDecoration(
                              color: Theme.of(context).colorScheme.surface,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                color: Theme.of(context).dividerColor.withOpacity(0.1),
                              ),
                            ),
                            child: ActivityRings(
                              caloriesProgress: dashboard.stats.caloriesProgress,
                              proteinProgress: dashboard.stats.proteinProgress,
                              carbsProgress: dashboard.stats.carbsProgress,
                              fatProgress: dashboard.stats.fatProgress,
                              caloriesConsumed: dashboard.stats.caloriesConsumed,
                              caloriesGoal: dashboard.stats.caloriesGoal,
                              proteinG: dashboard.stats.proteinG,
                              proteinGoal: dashboard.stats.proteinGoal,
                              carbsG: dashboard.stats.carbsG,
                              carbsGoal: dashboard.stats.carbsGoal,
                              fatG: dashboard.stats.fatG,
                              fatGoal: dashboard.stats.fatGoal,
                              size: 220,
                            ),
                          ),
                          const SizedBox(height: 24),

                          // Progress Bars
                          Text(
                            'Daily Progress',
                            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                          const SizedBox(height: 16),
                          ProgressBarCard(
                            emoji: '💪',
                            label: 'Protein',
                            current: '${dashboard.stats.proteinG.toStringAsFixed(0)}g',
                            goal: '${dashboard.stats.proteinGoal.toStringAsFixed(0)}g',
                            progress: dashboard.stats.proteinProgress,
                            color: Colors.red,
                          ),
                          const SizedBox(height: 12),
                          ProgressBarCard(
                            emoji: '🌾',
                            label: 'Carbs',
                            current: '${dashboard.stats.carbsG.toStringAsFixed(0)}g',
                            goal: '${dashboard.stats.carbsGoal.toStringAsFixed(0)}g',
                            progress: dashboard.stats.carbsProgress,
                            color: Colors.amber,
                          ),
                          const SizedBox(height: 12),
                          ProgressBarCard(
                            emoji: '🥑',
                            label: 'Fat',
                            current: '${dashboard.stats.fatG.toStringAsFixed(0)}g',
                            goal: '${dashboard.stats.fatGoal.toStringAsFixed(0)}g',
                            progress: dashboard.stats.fatProgress,
                            color: Colors.green,
                          ),
                          const SizedBox(height: 12),
                          ProgressBarCard(
                            emoji: '💧',
                            label: 'Water',
                            current: '${dashboard.stats.waterMl}ml',
                            goal: '${dashboard.stats.waterGoal}ml',
                            progress: dashboard.stats.waterProgress,
                            color: Colors.blue,
                          ),
                          const SizedBox(height: 12),
                          ProgressBarCard(
                            emoji: '🏋️',
                            label: 'Workouts',
                            current: '${dashboard.stats.workoutsCompleted}',
                            goal: '${dashboard.stats.workoutsGoal}',
                            progress: dashboard.stats.workoutsProgress,
                            color: Colors.purple,
                          ),
                          const SizedBox(height: 24),

                          // Activity Timeline
                          Text(
                            'Today\'s Activity',
                            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                          const SizedBox(height: 16),
                          ActivityTimeline(activities: dashboard.stats.activities),
                          const SizedBox(height: 80), // Space for FAB
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.of(context).pushNamed('/chat');
        },
        icon: const Icon(Icons.add),
        label: const Text('Log Activity'),
      ),
    );
  }

  Widget _buildCaloriesCard(BuildContext context, DailyStats stats) {
    final remaining = stats.caloriesRemaining;
    final isOver = remaining < 0;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: isOver
              ? [Colors.deepOrange, Colors.orange]
              : [
                  Theme.of(context).colorScheme.primary,
                  Theme.of(context).colorScheme.secondary,
                ],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                '🔥 Calories',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '${(stats.caloriesProgress * 100).toStringAsFixed(0)}%',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${stats.caloriesConsumed}',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                  height: 1,
                ),
              ),
              const SizedBox(width: 8),
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(
                  '/ ${stats.caloriesGoal} cal',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 18,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: stats.caloriesProgress.clamp(0.0, 1.0),
              backgroundColor: Colors.white.withOpacity(0.2),
              valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
              minHeight: 8,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            isOver
                ? 'Over by ${remaining.abs()} cal'
                : remaining > 0
                    ? '$remaining cal remaining'
                    : 'Goal reached! 🎯',
            style: TextStyle(
              color: Colors.white.withOpacity(0.9),
              fontSize: 16,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

