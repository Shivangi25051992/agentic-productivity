import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:math' as math;
import '../../providers/dashboard_provider.dart';
import '../../providers/auth_provider.dart';
import '../chat/chat_screen.dart';

/// Variant 5: Yuvi AI-First - Chat-Centric, Hero Ring, AI Nudges
/// - Chat input at TOP (primary action)
/// - Apple-style activity rings as hero widget
/// - Yuvi's AI nudge card (swipeable)
/// - Horizontal recent activity feed
/// - Sticky voice/quick/chat action bar
class IosHomeScreenV5YuviAiFirst extends StatefulWidget {
  const IosHomeScreenV5YuviAiFirst({super.key});

  @override
  State<IosHomeScreenV5YuviAiFirst> createState() => _IosHomeScreenV5YuviAiFirstState();
}

class _IosHomeScreenV5YuviAiFirstState extends State<IosHomeScreenV5YuviAiFirst> with TickerProviderStateMixin {
  final TextEditingController _chatController = TextEditingController();
  final FocusNode _chatFocusNode = FocusNode();
  late AnimationController _nudgeController;
  late Animation<double> _nudgeAnimation;
  int _currentNudgeIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = context.read<AuthProvider>();
      context.read<DashboardProvider>().fetchDailyStats(auth);
    });

    // Pulse animation for nudge card
    _nudgeController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat(reverse: true);

    _nudgeAnimation = Tween<double>(begin: 1.0, end: 1.03).animate(
      CurvedAnimation(parent: _nudgeController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _chatController.dispose();
    _chatFocusNode.dispose();
    _nudgeController.dispose();
    super.dispose();
  }

  void _handleChatSubmit() {
    if (_chatController.text.trim().isEmpty) return;
    
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => ChatScreen(
          initialMessage: _chatController.text.trim(),
        ),
      ),
    );
    
    _chatController.clear();
    _chatFocusNode.unfocus();
  }

  void _handleQuickAction(String action) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => ChatScreen(
          initialMessage: action,
        ),
      ),
    );
  }

  List<Map<String, dynamic>> _generateNudges(DailyStats stats) {
    final nudges = <Map<String, dynamic>>[];
    
    // Hydration nudge
    final waterPercent = (stats.waterMl / stats.waterGoal * 100).toInt();
    if (waterPercent < 50) {
      nudges.add({
        'icon': '💧',
        'title': 'Hydration Check!',
        'message': 'You\'re only at $waterPercent% of your water goal. Want a tip to drink more?',
        'action': 'Show me tips',
        'color': const Color(0xFF007AFF),
      });
    }

    // Streak nudge
    nudges.add({
      'icon': '🔥',
      'title': 'Keep the Streak!',
      'message': 'You\'re on a roll! Log one more activity to keep your momentum.',
      'action': 'Log activity',
      'color': const Color(0xFFFF6B6B),
    });

    // Protein nudge
    final proteinPercent = (stats.proteinG / stats.proteinGoal * 100).toInt();
    if (proteinPercent < 70) {
      nudges.add({
        'icon': '💪',
        'title': 'Protein Power!',
        'message': 'You need ${(stats.proteinGoal - stats.proteinG).toInt()}g more protein. Want meal suggestions?',
        'action': 'Suggest meals',
        'color': const Color(0xFF4ECDC4),
      });
    }

    // Celebration nudge
    if (stats.caloriesConsumed > 0 && stats.caloriesConsumed < stats.caloriesGoal * 1.1) {
      nudges.add({
        'icon': '🎉',
        'title': 'You\'re Crushing It!',
        'message': 'Great job staying on track today! Keep up the amazing work.',
        'action': 'View progress',
        'color': const Color(0xFF34C759),
      });
    }

    return nudges.isEmpty ? [{
      'icon': '✨',
      'title': 'Ready to Start?',
      'message': 'Log your first activity and let Yuvi help you reach your goals!',
      'action': 'Get started',
      'color': const Color(0xFF6366F1),
    }] : nudges;
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final dashboard = context.watch<DashboardProvider>();
    final stats = dashboard.stats;

    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Stack(
          children: [
            CustomScrollView(
              slivers: [
                // Greeting + Chat Input (TOP - Primary Action)
                SliverToBoxAdapter(
                  child: _buildChatFirstHeader(auth),
                ),

                // Quick Action Pills
                SliverToBoxAdapter(
                  child: _buildQuickPills(),
                ),

                // Hero Progress Ring (Apple Style)
                if (stats != null)
                  SliverToBoxAdapter(
                    child: _buildHeroActivityRing(stats),
                  ),

                // Yuvi's AI Nudge
                if (stats != null)
                  SliverToBoxAdapter(
                    child: _buildYuviNudge(stats),
                  ),

                // Your Day - Horizontal Recent Activity
                SliverToBoxAdapter(
                  child: _buildYourDayFeed(),
                ),

                // Streaks & Wins
                SliverToBoxAdapter(
                  child: _buildStreaksAndWins(),
                ),

                // Bottom padding for sticky bar
                const SliverToBoxAdapter(
                  child: SizedBox(height: 100),
                ),
              ],
            ),

            // Sticky Action Bar (Voice/Quick/Chat)
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: _buildStickyActionBar(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChatFirstHeader(AuthProvider auth) {
    return Container(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Greeting
          Text(
            '👋 Hi, ${auth.currentUser?.displayName?.split(' ').first ?? 'there'}!',
            style: const TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 20),

          // Chat Input - PRIMARY ACTION
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            decoration: BoxDecoration(
              color: const Color(0xFF1C1C1E),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: const Color(0xFF6366F1).withOpacity(0.3),
                width: 1.5,
              ),
            ),
            child: Row(
              children: [
                const Text('💬', style: TextStyle(fontSize: 24)),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: _chatController,
                    focusNode: _chatFocusNode,
                    style: const TextStyle(color: Colors.white, fontSize: 16),
                    decoration: const InputDecoration(
                      hintText: 'What\'s on your mind?',
                      hintStyle: TextStyle(color: Colors.grey, fontSize: 16),
                      border: InputBorder.none,
                    ),
                    onSubmitted: (_) => _handleChatSubmit(),
                  ),
                ),
                GestureDetector(
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Voice input - Coming soon!')),
                    );
                  },
                  child: Container(
                    width: 40,
                    height: 40,
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
                      ),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.mic, color: Colors.white, size: 20),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickPills() {
    final pills = [
      {'icon': '🍽️', 'text': 'Log lunch', 'action': 'Log my lunch'},
      {'icon': '🎯', 'text': 'Set goal', 'action': 'Help me set a goal'},
      {'icon': '📊', 'text': 'Analyze week', 'action': 'Analyze my week'},
      {'icon': '💧', 'text': 'Add water', 'action': 'Log water'},
    ];

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: pills.map((pill) {
          return GestureDetector(
            onTap: () => _handleQuickAction(pill['action'] as String),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: const Color(0xFF1C1C1E),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: Colors.grey.withOpacity(0.2),
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(pill['icon'] as String, style: const TextStyle(fontSize: 16)),
                  const SizedBox(width: 6),
                  Text(
                    pill['text'] as String,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildHeroActivityRing(DailyStats stats) {
    final caloriePercent = (stats.caloriesConsumed / stats.caloriesGoal).clamp(0.0, 1.0);
    final proteinPercent = (stats.proteinG / stats.proteinGoal).clamp(0.0, 1.0);
    final waterPercent = (stats.waterMl / stats.waterGoal).clamp(0.0, 1.0);

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: const Color(0xFF1C1C1E),
          borderRadius: BorderRadius.circular(24),
        ),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Activity Rings',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                Text(
                  '${(caloriePercent * 100).toInt()}%',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.grey[400],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Apple-style Activity Rings
            SizedBox(
              height: 240,
              child: Row(
                children: [
                  // Rings
                  Expanded(
                    flex: 3,
                    child: CustomPaint(
                      painter: _AppleActivityRingsPainter(
                        moveProgress: caloriePercent,
                        exerciseProgress: proteinPercent,
                        standProgress: waterPercent,
                      ),
                    ),
                  ),

                  // Stats
                  Expanded(
                    flex: 2,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildRingStat(
                          'Move',
                          '${stats.caloriesConsumed}/${stats.caloriesGoal}',
                          'KJ',
                          const Color(0xFFFF0055),
                        ),
                        const SizedBox(height: 20),
                        _buildRingStat(
                          'Exercise',
                          '${stats.proteinG.toInt()}/${stats.proteinGoal.toInt()}',
                          'g',
                          const Color(0xFF9CFF00),
                        ),
                        const SizedBox(height: 20),
                        _buildRingStat(
                          'Stand',
                          '${(stats.waterMl / 250).round()}/${(stats.waterGoal / 250).round()}',
                          'cups',
                          const Color(0xFF00E8E8),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRingStat(String label, String value, String unit, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey[400],
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 4),
        RichText(
          text: TextSpan(
            children: [
              TextSpan(
                text: value,
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
              TextSpan(
                text: ' $unit',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[500],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildYuviNudge(DailyStats stats) {
    final nudges = _generateNudges(stats);
    final currentNudge = nudges[_currentNudgeIndex % nudges.length];

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      child: ScaleTransition(
        scale: _nudgeAnimation,
        child: GestureDetector(
          onTap: () {
            setState(() {
              _currentNudgeIndex = (_currentNudgeIndex + 1) % nudges.length;
            });
          },
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  currentNudge['color'].withOpacity(0.2),
                  currentNudge['color'].withOpacity(0.05),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: currentNudge['color'].withOpacity(0.4),
                width: 2,
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    color: currentNudge['color'].withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Text(
                      currentNudge['icon'],
                      style: const TextStyle(fontSize: 28),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: currentNudge['color'],
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Text(
                              '✨ YUVI\'S NUDGE',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                                letterSpacing: 1,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        currentNudge['title'],
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        currentNudge['message'],
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.grey[400],
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Tap for another →',
                        style: TextStyle(
                          fontSize: 12,
                          color: currentNudge['color'],
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildYourDayFeed() {
    final activities = [
      {'icon': '🍳', 'label': 'Breakfast', 'time': '8:30 AM', 'color': const Color(0xFFFF9500)},
      {'icon': '🥗', 'label': 'Lunch', 'time': '12:45 PM', 'color': const Color(0xFF34C759)},
      {'icon': '💧', 'label': 'Water', 'time': '2:00 PM', 'color': const Color(0xFF007AFF)},
      {'icon': '🏃', 'label': 'Run', 'time': '5:30 PM', 'color': const Color(0xFFFF0055)},
      {'icon': '💪', 'label': 'Gym', 'time': '6:45 PM', 'color': const Color(0xFF9CFF00)},
    ];

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  '📸 Your Day',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                TextButton(
                  onPressed: () {
                    // Navigate to timeline
                  },
                  child: const Text(
                    'View All',
                    style: TextStyle(color: Color(0xFF6366F1)),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            height: 100,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 20),
              itemCount: activities.length,
              itemBuilder: (context, index) {
                final activity = activities[index];
                return Padding(
                  padding: const EdgeInsets.only(right: 12),
                  child: Column(
                    children: [
                      Container(
                        width: 64,
                        height: 64,
                        decoration: BoxDecoration(
                          color: (activity['color'] as Color).withOpacity(0.2),
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: activity['color'] as Color,
                            width: 2,
                          ),
                        ),
                        child: Center(
                          child: Text(
                            activity['icon'] as String,
                            style: const TextStyle(fontSize: 28),
                          ),
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        activity['label'] as String,
                        style: const TextStyle(
                          fontSize: 12,
                          color: Colors.white,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStreaksAndWins() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            Column(
              children: [
                const Text(
                  '🔥',
                  style: TextStyle(fontSize: 32),
                ),
                const SizedBox(height: 8),
                const Text(
                  '5 Days',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                Text(
                  'Streak',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.white.withOpacity(0.8),
                  ),
                ),
              ],
            ),
            Container(
              width: 1,
              height: 60,
              color: Colors.white.withOpacity(0.3),
            ),
            Column(
              children: [
                const Text(
                  '⭐',
                  style: TextStyle(fontSize: 32),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Level 12',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                Text(
                  'Keep going!',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.white.withOpacity(0.8),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStickyActionBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1C1C1E),
        border: Border(
          top: BorderSide(
            color: Colors.grey.withOpacity(0.2),
            width: 1,
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          _buildActionButton(
            icon: Icons.mic,
            label: 'Voice Log',
            gradient: const LinearGradient(
              colors: [Color(0xFFFF0055), Color(0xFFFF6B6B)],
            ),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Voice logging - Coming soon!')),
              );
            },
          ),
          _buildActionButton(
            icon: Icons.add_circle_outline,
            label: 'Quick Add',
            gradient: const LinearGradient(
              colors: [Color(0xFF34C759), Color(0xFF9CFF00)],
            ),
            onTap: () {
              _handleQuickAction('Quick add meal');
            },
          ),
          _buildActionButton(
            icon: Icons.chat_bubble_outline,
            label: 'Chat',
            gradient: const LinearGradient(
              colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
            ),
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (context) => const ChatScreen()),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required Gradient gradient,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              gradient: gradient,
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: Colors.white, size: 28),
          ),
          const SizedBox(height: 6),
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              color: Colors.white,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

/// Custom painter for Apple-style Activity Rings
class _AppleActivityRingsPainter extends CustomPainter {
  final double moveProgress;
  final double exerciseProgress;
  final double standProgress;

  _AppleActivityRingsPainter({
    required this.moveProgress,
    required this.exerciseProgress,
    required this.standProgress,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final strokeWidth = 16.0;

    // Move Ring (Outer - Red/Pink)
    _drawRing(
      canvas,
      center,
      size.width / 2 - strokeWidth / 2,
      strokeWidth,
      moveProgress,
      const Color(0xFFFF0055),
    );

    // Exercise Ring (Middle - Green)
    _drawRing(
      canvas,
      center,
      size.width / 2 - strokeWidth * 2.5,
      strokeWidth,
      exerciseProgress,
      const Color(0xFF9CFF00),
    );

    // Stand Ring (Inner - Cyan)
    _drawRing(
      canvas,
      center,
      size.width / 2 - strokeWidth * 4.5,
      strokeWidth,
      standProgress,
      const Color(0xFF00E8E8),
    );
  }

  void _drawRing(
    Canvas canvas,
    Offset center,
    double radius,
    double strokeWidth,
    double progress,
    Color color,
  ) {
    // Background ring
    final bgPaint = Paint()
      ..color = color.withOpacity(0.15)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, bgPaint);

    // Progress arc
    final progressPaint = Paint()
      ..shader = LinearGradient(
        colors: [
          color,
          color.withOpacity(0.7),
        ],
      ).createShader(Rect.fromCircle(center: center, radius: radius))
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
  bool shouldRepaint(_AppleActivityRingsPainter oldDelegate) {
    return oldDelegate.moveProgress != moveProgress ||
        oldDelegate.exerciseProgress != exerciseProgress ||
        oldDelegate.standProgress != standProgress;
  }
}

