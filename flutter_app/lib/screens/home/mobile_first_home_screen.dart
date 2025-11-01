import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';

import '../../providers/dashboard_provider.dart';
import '../../providers/profile_provider.dart';
import '../../providers/auth_provider.dart';
import '../meals/meal_detail_screen.dart';
import '../../widgets/meals/expandable_meal_card.dart';
import '../../widgets/insights/ai_insights_card.dart';
import '../../services/api_service.dart';

/// Mobile-First Dashboard - Clean, Card-Based Layout
/// Optimized for thumb-zone and one-handed use
class MobileFirstHomeScreen extends StatefulWidget {
  const MobileFirstHomeScreen({super.key});

  @override
  State<MobileFirstHomeScreen> createState() => _MobileFirstHomeScreenState();
}

class _MobileFirstHomeScreenState extends State<MobileFirstHomeScreen> {
  List<Map<String, dynamic>> _insights = [];
  String? _insightsSummary;
  bool _isLoadingInsights = false;

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

    if (profile.profile == null) {
      await profile.fetchProfile(auth);
    }

    if (profile.profile != null) {
      dashboard.updateGoalsFromProfile(profile.profile!.dailyGoals.toJson());
    }

    await dashboard.fetchDailyStats(auth);
    await _loadInsights();
  }

  Future<void> _loadInsights() async {
    setState(() => _isLoadingInsights = true);
    try {
      final auth = context.read<AuthProvider>();
      final api = ApiService(auth, onUnauthorized: () {
        Navigator.of(context).pushReplacementNamed('/login');
      });
      
      final response = await api.dio.get('/insights');
      if (response.statusCode == 200 && response.data != null) {
        final data = response.data as Map<String, dynamic>;
        setState(() {
          _insights = (data['insights'] as List?)?.cast<Map<String, dynamic>>() ?? [];
          _insightsSummary = data['summary'] as String?;
        });
      }
    } catch (e) {
      debugPrint('Error loading insights: $e');
    } finally {
      setState(() => _isLoadingInsights = false);
    }
  }

  Future<void> _refreshData() async {
    final auth = context.read<AuthProvider>();
    final dashboard = context.read<DashboardProvider>();
    await dashboard.fetchDailyStats(auth);
    await _loadInsights();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA), // Light background
      body: Consumer3<DashboardProvider, ProfileProvider, AuthProvider>(
        builder: (context, dashboard, profile, auth, child) {
          final caloriesConsumed = dashboard.stats.caloriesConsumed;
          final caloriesGoal = dashboard.stats.caloriesGoal;
          final caloriesRemaining = dashboard.stats.caloriesRemaining;
          final progress = dashboard.stats.caloriesProgress;
          final calorieDeficit = dashboard.stats.calorieDeficit;
          final isInDeficit = dashboard.stats.isInDeficit;

          return SafeArea(
            child: RefreshIndicator(
              onRefresh: _refreshData,
              child: CustomScrollView(
                slivers: [
                  // Compact Header
                  SliverToBoxAdapter(
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            Theme.of(context).colorScheme.primary,
                            Theme.of(context).colorScheme.secondary,
                          ],
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              IconButton(
                                icon: const Icon(Icons.menu, color: Colors.white),
                                onPressed: () => Scaffold.of(context).openDrawer(),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      '👋 Hi, ${profile.profile?.name ?? "there"}!',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 20,
                                        fontWeight: FontWeight.bold,
                                      ),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    Text(
                                      DateFormat('EEEE, MMM d').format(dashboard.selectedDate),
                                      style: TextStyle(
                                        color: Colors.white.withOpacity(0.9),
                                        fontSize: 14,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              IconButton(
                                icon: const Icon(Icons.account_circle, color: Colors.white),
                                onPressed: () => _showAccountMenu(context, auth, profile),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Main Content
                  SliverPadding(
                    padding: const EdgeInsets.all(16),
                    sliver: SliverList(
                      delegate: SliverChildListDelegate([
                        // Calorie Card
                        _CalorieCard(
                          consumed: caloriesConsumed,
                          goal: caloriesGoal,
                          remaining: caloriesRemaining,
                          progress: progress,
                          deficit: calorieDeficit,
                          isInDeficit: isInDeficit,
                        ),
                        
                        const SizedBox(height: 16),
                        
                        // AI Insights Card (THE DIFFERENTIATOR!)
                        if (_insights.isNotEmpty || _insightsSummary != null)
                          AIInsightsCard(
                            insights: _insights,
                            summary: _insightsSummary,
                          ),
                        
                        if (_insights.isNotEmpty || _insightsSummary != null)
                          const SizedBox(height: 16),
                        
                        // Macros Card
                        _MacrosCard(
                          protein: dashboard.stats.proteinG,
                          proteinGoal: dashboard.stats.proteinGoal,
                          carbs: dashboard.stats.carbsG,
                          carbsGoal: dashboard.stats.carbsGoal,
                          fat: dashboard.stats.fatG,
                          fatGoal: dashboard.stats.fatGoal,
                        ),
                        
                        const SizedBox(height: 16),
                        
                        // Today's Meals Card
                        _TodaysMealsCard(
                          meals: _getMealsSummary(dashboard),
                        ),
                        
                        const SizedBox(height: 16),
                        
                        // Activity Card
                        _ActivityCard(
                          workouts: dashboard.stats.workoutsCompleted,
                        ),
                        
                        const SizedBox(height: 80), // Space for FAB
                      ]),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
      
      // Floating Action Buttons - Thumb Zone Friendly
      floatingActionButton: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          FloatingActionButton.extended(
            onPressed: () => Navigator.of(context).pushNamed('/chat'),
            icon: const Icon(Icons.chat_bubble),
            label: const Text('Log Food'),
            heroTag: 'chat',
          ),
          const SizedBox(height: 12),
          FloatingActionButton(
            onPressed: () => Navigator.of(context).pushNamed('/plan'),
            child: const Icon(Icons.add),
            heroTag: 'add',
          ),
        ],
      ),
    );
  }

  List<Map<String, dynamic>> _getMealsSummary(DashboardProvider dashboard) {
    final meals = <Map<String, dynamic>>[];
    
    // Group activities by meal type
    final mealsByType = <String, List<dynamic>>{};
    for (final activity in dashboard.stats.activities) {
      if (activity.type == 'meal') {
        final type = activity.data?['meal_type'] ?? 'other';
        mealsByType.putIfAbsent(type, () => []).add(activity);
      }
    }
    
    // Create summary for each meal type
    final mealTypes = ['breakfast', 'lunch', 'snack', 'dinner'];
    for (final type in mealTypes) {
      final typeMeals = mealsByType[type] ?? [];
      final totalCal = typeMeals.fold<int>(0, (sum, m) {
        final cal = m.data?['calories'] as num? ?? 0;
        return sum + cal.toInt();
      });
      meals.add({
        'type': type,
        'count': typeMeals.length,
        'calories': totalCal,
        'logged': typeMeals.isNotEmpty,
        'activities': typeMeals, // Include activities for detail view
      });
    }
    
    return meals;
  }

  void _showAccountMenu(BuildContext context, AuthProvider auth, ProfileProvider profile) {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.person),
              title: Text(profile.profile?.name ?? 'User'),
              subtitle: Text(auth.currentUser?.email ?? ''),
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.settings),
              title: const Text('Settings'),
              onTap: () {
                Navigator.pop(context);
                // Navigate to settings
              },
            ),
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.red),
              title: const Text('Logout', style: TextStyle(color: Colors.red)),
              onTap: () async {
                Navigator.pop(context);
                await auth.signOut();
                if (context.mounted) {
                  Navigator.of(context).pushNamedAndRemoveUntil('/login', (route) => false);
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}

// Calorie Card Widget
class _CalorieCard extends StatelessWidget {
  final int consumed;
  final int goal;
  final int remaining;
  final double progress;
  final int deficit;
  final bool isInDeficit;

  const _CalorieCard({
    required this.consumed,
    required this.goal,
    required this.remaining,
    required this.progress,
    required this.deficit,
    required this.isInDeficit,
  });

  @override
  Widget build(BuildContext context) {
    final isOver = remaining < 0;
    
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Colors.orange.shade50,
              Colors.orange.shade100,
            ],
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.local_fire_department, color: Colors.orange, size: 28),
                const SizedBox(width: 8),
                const Text(
                  'Calories',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: isOver ? Colors.red.shade100 : Colors.green.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    isOver ? 'Over' : 'On Track',
                    style: TextStyle(
                      color: isOver ? Colors.red.shade700 : Colors.green.shade700,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 20),
            
            // Big Numbers
            Row(
              crossAxisAlignment: CrossAxisAlignment.baseline,
              textBaseline: TextBaseline.alphabetic,
              children: [
                Text(
                  '$consumed',
                  style: const TextStyle(
                    fontSize: 48,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  '/ $goal',
                  style: TextStyle(
                    fontSize: 24,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 8),
            
            Text(
              isOver 
                ? '${remaining.abs()} cal over budget'
                : '$remaining cal remaining',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey.shade700,
              ),
            ),
            
            const SizedBox(height: 12),
            
            // Calorie Deficit/Surplus Badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: isInDeficit ? Colors.green.shade50 : Colors.red.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isInDeficit ? Colors.green.shade200 : Colors.red.shade200,
                  width: 1,
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    isInDeficit ? Icons.trending_down : Icons.trending_up,
                    color: isInDeficit ? Colors.green.shade700 : Colors.red.shade700,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    isInDeficit 
                        ? 'Deficit: ${deficit.abs()} kcal' 
                        : 'Surplus: ${deficit.abs()} kcal',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: isInDeficit ? Colors.green.shade700 : Colors.red.shade700,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Icon(
                    isInDeficit ? Icons.check_circle_outline : Icons.warning_amber_rounded,
                    color: isInDeficit ? Colors.green.shade700 : Colors.red.shade700,
                    size: 18,
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Progress Bar
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: progress,
                minHeight: 12,
                backgroundColor: Colors.white,
                valueColor: AlwaysStoppedAnimation<Color>(
                  isOver ? Colors.red : Colors.orange,
                ),
              ),
            ),
            
            const SizedBox(height: 8),
            
            Text(
              '${(progress * 100).toInt()}% of daily goal',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Macros Card Widget
class _MacrosCard extends StatelessWidget {
  final double protein;
  final double proteinGoal;
  final double carbs;
  final double carbsGoal;
  final double fat;
  final double fatGoal;

  const _MacrosCard({
    required this.protein,
    required this.proteinGoal,
    required this.carbs,
    required this.carbsGoal,
    required this.fat,
    required this.fatGoal,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '💪 Macros',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            _MacroRow(
              label: 'Protein',
              value: protein,
              goal: proteinGoal,
              color: Colors.blue,
              icon: Icons.fitness_center,
            ),
            const SizedBox(height: 12),
            _MacroRow(
              label: 'Carbs',
              value: carbs,
              goal: carbsGoal,
              color: Colors.amber,
              icon: Icons.grain,
            ),
            const SizedBox(height: 12),
            _MacroRow(
              label: 'Fat',
              value: fat,
              goal: fatGoal,
              color: Colors.purple,
              icon: Icons.water_drop,
            ),
          ],
        ),
      ),
    );
  }
}

class _MacroRow extends StatelessWidget {
  final String label;
  final double value;
  final double goal;
  final Color color;
  final IconData icon;

  const _MacroRow({
    required this.label,
    required this.value,
    required this.goal,
    required this.color,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final progress = goal > 0 ? (value / goal).clamp(0.0, 1.0) : 0.0;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 20, color: color),
            const SizedBox(width: 8),
            Text(
              label,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
            const Spacer(),
            Text(
              '${value.toStringAsFixed(0)}g / ${goal.toStringAsFixed(0)}g',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: progress,
            minHeight: 8,
            backgroundColor: color.withOpacity(0.2),
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ),
      ],
    );
  }
}

// Today's Meals Card - Now uses expandable cards
class _TodaysMealsCard extends StatelessWidget {
  final List<Map<String, dynamic>> meals;

  const _TodaysMealsCard({required this.meals});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                '📊 Today\'s Meals',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Row(
                children: [
                  TextButton.icon(
                    onPressed: () => Navigator.of(context).pushNamed('/meals/timeline'),
                    icon: const Icon(Icons.timeline, size: 18),
                    label: const Text('Timeline'),
                    style: TextButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                    ),
                  ),
                  TextButton.icon(
                    onPressed: () => Navigator.of(context).pushNamed('/chat'),
                    icon: const Icon(Icons.add_circle_outline, size: 18),
                    label: const Text('Log Food'),
                    style: TextButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        ...meals.map((meal) => ExpandableMealCard(
          mealType: meal['type'],
          activities: (meal['activities'] as List<dynamic>?) ?? [],
          onEdit: () {
            // TODO: Navigate to edit screen
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Edit feature coming soon!')),
            );
          },
          onDelete: () {
            // TODO: Implement delete
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Delete feature coming soon!')),
            );
          },
          onMove: (newMealType) {
            // TODO: Implement move
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Move to $newMealType coming soon!')),
            );
          },
        )),
      ],
    );
  }
}

// Activity Card
class _ActivityCard extends StatelessWidget {
  final int workouts;

  const _ActivityCard({required this.workouts});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '🏃 Activity',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            if (workouts == 0)
              Column(
                children: [
                  Text(
                    'No workouts logged today',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: () => Navigator.of(context).pushNamed('/plan'),
                      icon: const Icon(Icons.add),
                      label: const Text('Log Workout'),
                    ),
                  ),
                ],
              )
            else
              Text(
                '$workouts workout${workouts > 1 ? 's' : ''} completed 💪',
                style: const TextStyle(fontSize: 14),
              ),
          ],
        ),
      ),
    );
  }
}

