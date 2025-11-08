import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:math' as math;
import '../../providers/dashboard_provider.dart';
import '../../providers/auth_provider.dart';
import '../chat/chat_screen.dart';

/// Variant 4: Compact Rings + Inline Chat + AI Insights Spotlight
/// - Smaller activity rings (top right corner)
/// - Inline chat that expands to full screen
/// - AI Insights with attention-grabbing animations
/// - Maximum content in minimal space
class IosHomeScreenV4Compact extends StatefulWidget {
  const IosHomeScreenV4Compact({super.key});

  @override
  State<IosHomeScreenV4Compact> createState() => _IosHomeScreenV4CompactState();
}

class _IosHomeScreenV4CompactState extends State<IosHomeScreenV4Compact> with TickerProviderStateMixin {
  final TextEditingController _chatController = TextEditingController();
  final FocusNode _chatFocusNode = FocusNode();
  bool _isChatExpanded = false;
  late AnimationController _insightsPulseController;
  late Animation<double> _insightsPulseAnimation;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = context.read<AuthProvider>();
      context.read<DashboardProvider>().fetchDailyStats(auth);
    });

    // Pulse animation for AI insights
    _insightsPulseController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    )..repeat(reverse: true);

    _insightsPulseAnimation = Tween<double>(begin: 1.0, end: 1.08).animate(
      CurvedAnimation(parent: _insightsPulseController, curve: Curves.easeInOut),
    );

    // Listen to chat focus
    _chatFocusNode.addListener(() {
      if (_chatFocusNode.hasFocus && !_isChatExpanded) {
        setState(() => _isChatExpanded = true);
      }
    });
  }

  @override
  void dispose() {
    _chatController.dispose();
    _chatFocusNode.dispose();
    _insightsPulseController.dispose();
    super.dispose();
  }

  void _handleChatSubmit() {
    if (_chatController.text.trim().isEmpty) return;
    
    // Navigate to full chat screen with the message
    Navigator.of(context).push(
      PageRouteBuilder(
        pageBuilder: (context, animation, secondaryAnimation) => ChatScreen(
          initialMessage: _chatController.text.trim(),
        ),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          return SlideTransition(
            position: Tween<Offset>(
              begin: const Offset(0, 1),
              end: Offset.zero,
            ).animate(CurvedAnimation(
              parent: animation,
              curve: Curves.easeOutCubic,
            )),
            child: child,
          );
        },
        transitionDuration: const Duration(milliseconds: 400),
      ),
    );
    
    _chatController.clear();
    _chatFocusNode.unfocus();
    setState(() => _isChatExpanded = false);
  }

  List<Map<String, dynamic>> _generateInsights(DailyStats stats) {
    final insights = <Map<String, dynamic>>[];
    
    // Calorie insight
    if (stats.caloriesConsumed > 0) {
      final remaining = stats.caloriesGoal - stats.caloriesConsumed;
      if (remaining > 0) {
        insights.add({
          'icon': '🔥',
          'title': 'Calorie Budget',
          'message': 'You have ${remaining.toInt()} calories left today',
          'color': const Color(0xFFFF6B6B),
        });
      } else {
        insights.add({
          'icon': '⚠️',
          'title': 'Over Budget',
          'message': 'You\'ve exceeded your calorie goal by ${(-remaining).toInt()}',
          'color': const Color(0xFFFF3B30),
        });
      }
    }

    // Protein insight
    if (stats.proteinG > 0) {
      final proteinPercent = (stats.proteinG / stats.proteinGoal * 100).toInt();
      if (proteinPercent >= 80) {
        insights.add({
          'icon': '💪',
          'title': 'Protein Power',
          'message': 'Great job! You\'re at $proteinPercent% of your protein goal',
          'color': const Color(0xFF34C759),
        });
      } else {
        insights.add({
          'icon': '🥩',
          'title': 'Protein Boost',
          'message': 'Add ${(stats.proteinGoal - stats.proteinG).toInt()}g more protein',
          'color': const Color(0xFFFF9500),
        });
      }
    }

    // Water insight
    final waterGlasses = (stats.waterMl / 250).round();
    final waterGoalGlasses = (stats.waterGoal / 250).round();
    if (waterGlasses < waterGoalGlasses) {
      insights.add({
        'icon': '💧',
        'title': 'Stay Hydrated',
        'message': 'Drink ${waterGoalGlasses - waterGlasses} more glasses of water',
        'color': const Color(0xFF007AFF),
      });
    }

    // Default insight if none
    if (insights.isEmpty) {
      insights.add({
        'icon': '✨',
        'title': 'Ready to Start',
        'message': 'Log your first meal or activity to get personalized insights',
        'color': const Color(0xFF6366F1),
      });
    }

    return insights;
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final dashboard = context.watch<DashboardProvider>();
    final stats = dashboard.stats;

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Stack(
          children: [
            // Main content
            CustomScrollView(
              slivers: [
                // Compact header with rings
                SliverToBoxAdapter(
                  child: _buildCompactHeader(auth, stats),
                ),

                // AI Insights Spotlight
                SliverToBoxAdapter(
                  child: _buildAIInsightsSpotlight(stats),
                ),

                // Quick Stats
                SliverToBoxAdapter(
                  child: _buildQuickStats(stats),
                ),

                // Recent Activity
                SliverToBoxAdapter(
                  child: _buildRecentActivity(),
                ),

                // Bottom padding for chat input
                const SliverToBoxAdapter(
                  child: SizedBox(height: 100),
                ),
              ],
            ),

            // Inline chat (always visible at bottom)
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: _buildInlineChat(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCompactHeader(AuthProvider auth, DailyStats? stats) {
    return Container(
      padding: const EdgeInsets.all(20),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Left: Greeting
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _getGreeting(),
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey[600],
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  auth.currentUser?.displayName?.split(' ').first ?? 'There',
                  style: const TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1F2937),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  _getMotivationalMessage(stats),
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),

          // Right: Compact rings
          if (stats != null) _buildCompactRings(stats),
        ],
      ),
    );
  }

  Widget _buildCompactRings(DailyStats stats) {
    final caloriePercent = (stats.caloriesConsumed / stats.caloriesGoal).clamp(0.0, 1.0);
    final proteinPercent = (stats.proteinG / stats.proteinGoal).clamp(0.0, 1.0);
    final waterPercent = (stats.waterMl / stats.waterGoal).clamp(0.0, 1.0);

    return SizedBox(
      width: 120,
      height: 120,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Outer ring - Calories
          _buildRing(
            size: 120,
            progress: caloriePercent,
            color: const Color(0xFFFF6B6B),
            strokeWidth: 10,
          ),
          // Middle ring - Protein
          _buildRing(
            size: 90,
            progress: proteinPercent,
            color: const Color(0xFF4ECDC4),
            strokeWidth: 10,
          ),
          // Inner ring - Water
          _buildRing(
            size: 60,
            progress: waterPercent,
            color: const Color(0xFF007AFF),
            strokeWidth: 10,
          ),
          // Center text
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '${stats.caloriesConsumed.toInt()}',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                ),
              ),
              Text(
                'kcal',
                style: TextStyle(
                  fontSize: 10,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildRing({
    required double size,
    required double progress,
    required Color color,
    required double strokeWidth,
  }) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: _RingPainter(
          progress: progress,
          color: color,
          strokeWidth: strokeWidth,
        ),
      ),
    );
  }

  Widget _buildAIInsightsSpotlight(DailyStats? stats) {
    if (stats == null) return const SizedBox.shrink();

    final insights = _generateInsights(stats);
    if (insights.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text(
                  '✨ AI INSIGHTS',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    letterSpacing: 1,
                  ),
                ),
              ),
              const Spacer(),
              Text(
                'Swipe for more →',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[500],
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 140,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 20),
            itemCount: insights.length,
            itemBuilder: (context, index) {
              final insight = insights[index];
              return Padding(
                padding: const EdgeInsets.only(right: 16),
                child: _buildInsightCard(insight, index),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildInsightCard(Map<String, dynamic> insight, int index) {
    return ScaleTransition(
      scale: _insightsPulseAnimation,
      child: GestureDetector(
        onTap: () {
          // TODO: Navigate to insights detail
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('${insight['title']} - View details'),
              behavior: SnackBarBehavior.floating,
            ),
          );
        },
        child: Container(
          width: 280,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                insight['color'].withOpacity(0.15),
                insight['color'].withOpacity(0.05),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: insight['color'].withOpacity(0.3),
              width: 2,
            ),
            boxShadow: [
              BoxShadow(
                color: insight['color'].withOpacity(0.2),
                blurRadius: 16,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  // Icon with glow
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: insight['color'].withOpacity(0.3),
                          blurRadius: 8,
                          spreadRadius: 1,
                        ),
                      ],
                    ),
                    child: Center(
                      child: Text(
                        insight['icon'],
                        style: const TextStyle(fontSize: 24),
                      ),
                    ),
                  ),
                  const Spacer(),
                  // Index indicator
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: insight['color'].withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${index + 1}',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: insight['color'],
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                insight['title'],
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 6),
              Expanded(
                child: Text(
                  insight['message'],
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey[700],
                    height: 1.3,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickStats(DailyStats? stats) {
    if (stats == null) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      child: Row(
        children: [
          _buildStatCard(
            icon: '🔥',
            value: '${stats.caloriesConsumed.toInt()}',
            label: 'Calories',
            color: const Color(0xFFFF6B6B),
          ),
          const SizedBox(width: 12),
          _buildStatCard(
            icon: '💪',
            value: '${stats.proteinG.toInt()}g',
            label: 'Protein',
            color: const Color(0xFF4ECDC4),
          ),
          const SizedBox(width: 12),
          _buildStatCard(
            icon: '💧',
            value: '${(stats.waterMl / 250).round()}',
            label: 'Glasses',
            color: const Color(0xFF007AFF),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard({
    required String icon,
    required String value,
    required String label,
    required Color color,
  }) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: color.withOpacity(0.2),
            width: 1,
          ),
        ),
        child: Column(
          children: [
            Text(icon, style: const TextStyle(fontSize: 24)),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentActivity() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Recent Activity',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                ),
              ),
              TextButton(
                onPressed: () {
                  // Navigate to timeline
                },
                child: const Text('View All'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildActivityItem(
            icon: '🍽️',
            title: 'Breakfast logged',
            time: '2 hours ago',
            color: const Color(0xFFFF9500),
          ),
          _buildActivityItem(
            icon: '💧',
            title: 'Water logged',
            time: '3 hours ago',
            color: const Color(0xFF007AFF),
          ),
          _buildActivityItem(
            icon: '🏃',
            title: 'Morning walk',
            time: '5 hours ago',
            color: const Color(0xFF34C759),
          ),
        ],
      ),
    );
  }

  Widget _buildActivityItem({
    required String icon,
    required String title,
    required String time,
    required Color color,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Center(
              child: Text(icon, style: const TextStyle(fontSize: 24)),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF1F2937),
                  ),
                ),
                Text(
                  time,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInlineChat() {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeOutCubic,
      height: _isChatExpanded ? 200 : 80,
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, -4),
          ),
        ],
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          // Drag handle (when expanded)
          if (_isChatExpanded)
            GestureDetector(
              onTap: () {
                _chatFocusNode.unfocus();
                setState(() => _isChatExpanded = false);
              },
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
            ),

          // Chat input
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            child: Row(
              children: [
                // AI icon
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
                    ),
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF6366F1).withOpacity(0.3),
                        blurRadius: 12,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: const Center(
                    child: Text('✨', style: TextStyle(fontSize: 24)),
                  ),
                ),
                const SizedBox(width: 12),
                // Text field
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    decoration: BoxDecoration(
                      color: Colors.grey[100],
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: TextField(
                      controller: _chatController,
                      focusNode: _chatFocusNode,
                      decoration: const InputDecoration(
                        hintText: 'Ask me anything...',
                        border: InputBorder.none,
                        hintStyle: TextStyle(color: Colors.grey),
                      ),
                      onSubmitted: (_) => _handleChatSubmit(),
                      textInputAction: TextInputAction.send,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                // Send button
                GestureDetector(
                  onTap: _handleChatSubmit,
                  child: Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: const Color(0xFF6366F1),
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFF6366F1).withOpacity(0.3),
                          blurRadius: 12,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: const Icon(
                      Icons.arrow_upward,
                      color: Colors.white,
                      size: 24,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Quick suggestions (when expanded)
          if (_isChatExpanded)
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _buildQuickChip('Log my breakfast'),
                    _buildQuickChip('How many calories left?'),
                    _buildQuickChip('Create meal plan'),
                    _buildQuickChip('Water reminder'),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildQuickChip(String text) {
    return GestureDetector(
      onTap: () {
        _chatController.text = text;
        _handleChatSubmit();
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: const Color(0xFF6366F1).withOpacity(0.1),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: const Color(0xFF6366F1).withOpacity(0.3),
          ),
        ),
        child: Text(
          text,
          style: const TextStyle(
            fontSize: 14,
            color: Color(0xFF6366F1),
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  }

  String _getMotivationalMessage(DailyStats? stats) {
    if (stats == null) return 'Ready to start your day?';
    
    final caloriePercent = (stats.caloriesConsumed / stats.caloriesGoal * 100).toInt();
    if (caloriePercent < 30) return 'Let\'s fuel your day!';
    if (caloriePercent < 70) return 'You\'re doing great!';
    return 'Almost at your goal!';
  }
}

/// Custom painter for activity rings
class _RingPainter extends CustomPainter {
  final double progress;
  final Color color;
  final double strokeWidth;

  _RingPainter({
    required this.progress,
    required this.color,
    required this.strokeWidth,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width - strokeWidth) / 2;

    // Background circle
    final bgPaint = Paint()
      ..color = color.withOpacity(0.2)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, bgPaint);

    // Progress arc
    final progressPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    final sweepAngle = 2 * math.pi * progress;
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      sweepAngle,
      false,
      progressPaint,
    );
  }

  @override
  bool shouldRepaint(_RingPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}

