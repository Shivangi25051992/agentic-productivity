import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:math' as math;
import '../../providers/auth_provider.dart';
import '../../providers/dashboard_provider.dart';
import '../../providers/timeline_provider.dart';
import '../../models/timeline_activity.dart';
import '../chat/chat_screen.dart';

/// V7: Mobile-First Feed Layout
/// Based on user's wireframe design
/// - Top: Chat input with quick log chips
/// - Suggestion banner
/// - Highlight card (streaks/wins)
/// - Vertical feed (timeline)
/// - Stats/rings at bottom
class IosHomeScreenV7MobileFirst extends StatefulWidget {
  const IosHomeScreenV7MobileFirst({Key? key}) : super(key: key);

  @override
  State<IosHomeScreenV7MobileFirst> createState() => _IosHomeScreenV7MobileFirstState();
}

class _IosHomeScreenV7MobileFirstState extends State<IosHomeScreenV7MobileFirst> with SingleTickerProviderStateMixin {
  final TextEditingController _chatController = TextEditingController();
  bool _isSending = false;
  bool _isDashboardExpanded = false;
  late AnimationController _dashboardAnimationController;
  late Animation<double> _dashboardAnimation;

  @override
  void initState() {
    super.initState();
    _dashboardAnimationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _dashboardAnimation = CurvedAnimation(
      parent: _dashboardAnimationController,
      curve: Curves.easeInOut,
    );
    _loadData();
  }

  @override
  void dispose() {
    _chatController.dispose();
    _dashboardAnimationController.dispose();
    super.dispose();
  }

  void _toggleDashboard() {
    setState(() {
      _isDashboardExpanded = !_isDashboardExpanded;
      if (_isDashboardExpanded) {
        _dashboardAnimationController.forward();
      } else {
        _dashboardAnimationController.reverse();
      }
    });
  }

  Future<void> _loadData() async {
    final auth = context.read<AuthProvider>();
    final dashboard = context.read<DashboardProvider>();
    final timeline = context.read<TimelineProvider>();

    await Future.wait([
      dashboard.fetchDailyStats(auth),
      timeline.fetchTimeline(),
    ]);
  }

  Future<void> _handleChatSubmit(String message) async {
    if (message.trim().isEmpty) return;

    setState(() => _isSending = true);
    _chatController.clear();

    try {
      // Navigate to chat screen with initial message
      if (mounted) {
        await Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ChatScreen(initialMessage: message),
          ),
        );
      }

      // Refresh data after returning
      final auth = context.read<AuthProvider>();
      final timeline = context.read<TimelineProvider>();
      final dashboard = context.read<DashboardProvider>();
      
      await Future.wait([
        timeline.fetchTimeline(forceRefresh: true),
        dashboard.fetchDailyStats(auth, forceRefresh: true),
      ]);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error: $e'),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSending = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadData,
          color: Colors.blue,
          child: CustomScrollView(
            slivers: [
              // 1. CHAT INPUT BAR (Sticky at top)
              SliverAppBar(
                floating: true,
                pinned: true,
                backgroundColor: const Color(0xFF0A0A0A),
                elevation: 0,
                toolbarHeight: 120,
                flexibleSpace: _buildChatInputBar(),
              ),

              // 1.5. FLOATING STICKY DASHBOARD
              SliverAppBar(
                floating: false,
                pinned: true,
                backgroundColor: Colors.transparent,
                elevation: 0,
                toolbarHeight: _isDashboardExpanded ? 280 : 76,
                flexibleSpace: _buildFloatingDashboard(),
              ),

              // 2. SUGGESTION BANNER
              SliverToBoxAdapter(
                child: _buildSuggestionBanner(),
              ),

              // 3. HIGHLIGHT CARD (Streaks/Wins)
              SliverToBoxAdapter(
                child: _buildHighlightCard(),
              ),

              // 4. FEED HEADER
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 24, 16, 12),
                  child: Row(
                    children: [
                      Text(
                        'Your Activity Feed',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Spacer(),
                      Icon(Icons.filter_list, color: Colors.white54, size: 20),
                    ],
                  ),
                ),
              ),

              // 5. VERTICAL FEED (Timeline)
              _buildFeed(),

              // Bottom padding
              SliverToBoxAdapter(
                child: SizedBox(height: 100),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // 1. CHAT INPUT BAR
  Widget _buildChatInputBar() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0A0A),
        border: Border(
          bottom: BorderSide(
            color: Colors.white.withOpacity(0.1),
            width: 1,
          ),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          // Chat input
          Container(
            height: 44,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 0),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.05),
              borderRadius: BorderRadius.circular(24),
              border: Border.all(
                color: Colors.blue.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Icon(Icons.mic_outlined, color: Colors.blue, size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: _chatController,
                    style: TextStyle(color: Colors.white, fontSize: 14),
                    decoration: InputDecoration(
                      border: InputBorder.none,
                      hintText: 'Log meal, workout, or chat...',
                      hintStyle: TextStyle(color: Colors.white38, fontSize: 14),
                      isDense: true,
                      contentPadding: EdgeInsets.zero,
                    ),
                    onSubmitted: _handleChatSubmit,
                    enabled: !_isSending,
                  ),
                ),
                if (_isSending)
                  SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.blue,
                    ),
                  )
                else
                  IconButton(
                    icon: Icon(Icons.send, color: Colors.blue, size: 18),
                    padding: EdgeInsets.all(4),
                    constraints: BoxConstraints(minWidth: 32, minHeight: 32),
                    onPressed: () => _handleChatSubmit(_chatController.text),
                  ),
              ],
            ),
          ),
          
          const SizedBox(height: 8),
          
          // Quick log chips
          SizedBox(
            height: 32,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: EdgeInsets.zero,
              children: [
                _buildQuickChip('🍎 Log Meal', () => _handleChatSubmit('I ate ')),
                const SizedBox(width: 8),
                _buildQuickChip('💪 Log Workout', () => _handleChatSubmit('I did ')),
                const SizedBox(width: 8),
                _buildQuickChip('💧 Log Water', () => _handleChatSubmit('I drank water')),
                const SizedBox(width: 8),
                _buildQuickChip('💊 Log Supplement', () => _handleChatSubmit('I took ')),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickChip(String label, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 32,
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
        decoration: BoxDecoration(
          color: Colors.blue.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: Colors.blue.withOpacity(0.3),
            width: 1,
          ),
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              color: Colors.blue,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ),
    );
  }

  // 1.5. FLOATING STICKY DASHBOARD
  Widget _buildFloatingDashboard() {
    return Consumer<DashboardProvider>(
      builder: (context, dashboard, _) {
        return GestureDetector(
          onTap: _toggleDashboard,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeInOut,
            margin: const EdgeInsets.fromLTRB(16, 4, 16, 4),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.blue.withOpacity(0.2),
                  Colors.purple.withOpacity(0.2),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: Colors.blue.withOpacity(0.3),
                width: 1,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.blue.withOpacity(0.1),
                  blurRadius: 8,
                  offset: Offset(0, 2),
                ),
              ],
            ),
            child: _isDashboardExpanded
                ? _buildExpandedDashboard(dashboard)
                : _buildCompactDashboard(dashboard),
          ),
        );
      },
    );
  }

  Widget _buildCompactDashboard(DashboardProvider dashboard) {
    return Row(
      children: [
        // Calories
        Expanded(
          child: _buildCompactStat(
            'Calories',
            '${dashboard.stats.caloriesConsumed}/${dashboard.stats.caloriesGoal}',
            dashboard.stats.caloriesProgress,
            Colors.orange,
          ),
        ),
        Container(
          width: 1,
          height: 20,
          color: Colors.white.withOpacity(0.2),
          margin: const EdgeInsets.symmetric(horizontal: 8),
        ),
        // Protein
        Expanded(
          child: _buildCompactStat(
            'Protein',
            '${dashboard.stats.proteinG.toInt()}g',
            dashboard.stats.proteinProgress,
            Colors.blue,
          ),
        ),
        Container(
          width: 1,
          height: 20,
          color: Colors.white.withOpacity(0.2),
          margin: const EdgeInsets.symmetric(horizontal: 8),
        ),
        // Carbs
        Expanded(
          child: _buildCompactStat(
            'Carbs',
            '${dashboard.stats.carbsG.toInt()}g',
            dashboard.stats.carbsProgress,
            Colors.green,
          ),
        ),
        Container(
          width: 1,
          height: 20,
          color: Colors.white.withOpacity(0.2),
          margin: const EdgeInsets.symmetric(horizontal: 8),
        ),
        // Fat
        Expanded(
          child: _buildCompactStat(
            'Fat',
            '${dashboard.stats.fatG.toInt()}g',
            dashboard.stats.fatProgress,
            Colors.purple,
          ),
        ),
        const SizedBox(width: 4),
        Icon(
          _isDashboardExpanded ? Icons.expand_less : Icons.expand_more,
          color: Colors.white70,
          size: 18,
        ),
      ],
    );
  }

  Widget _buildCompactStat(String label, String value, double progress, Color color) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          label,
          style: TextStyle(
            color: Colors.white54,
            fontSize: 8,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: TextStyle(
            color: Colors.white,
            fontSize: 10,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 2),
        LinearProgressIndicator(
          value: progress,
          backgroundColor: Colors.white.withOpacity(0.1),
          valueColor: AlwaysStoppedAnimation<Color>(color),
          minHeight: 2,
        ),
      ],
    );
  }

  Widget _buildExpandedDashboard(DashboardProvider dashboard) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Header
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Today\'s Progress',
              style: TextStyle(
                color: Colors.white,
                fontSize: 15,
                fontWeight: FontWeight.bold,
              ),
            ),
            Icon(
              Icons.expand_less,
              color: Colors.white70,
              size: 18,
            ),
          ],
        ),
        const SizedBox(height: 12),
        // Rings
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _buildMiniRing(
              'Protein',
              dashboard.stats.proteinG,
              dashboard.stats.proteinGoal,
              Colors.blue,
              size: 60,
            ),
            _buildMiniRing(
              'Carbs',
              dashboard.stats.carbsG,
              dashboard.stats.carbsGoal,
              Colors.green,
              size: 60,
            ),
            _buildMiniRing(
              'Fat',
              dashboard.stats.fatG,
              dashboard.stats.fatGoal,
              Colors.purple,
              size: 60,
            ),
          ],
        ),
        const SizedBox(height: 10),
        // Calorie summary
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Calories',
                    style: TextStyle(
                      color: Colors.white54,
                      fontSize: 10,
                    ),
                  ),
                  Text(
                    '${dashboard.stats.caloriesConsumed}',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              Text(
                '/ ${dashboard.stats.caloriesGoal}',
                style: TextStyle(
                  color: Colors.white54,
                  fontSize: 13,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMiniRing(String label, double value, double goal, Color color, {double size = 80}) {
    final percentage = goal > 0 ? (value / goal).clamp(0.0, 1.0) : 0.0;
    
    return Column(
      children: [
        SizedBox(
          width: size,
          height: size,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Background ring
              CustomPaint(
                size: Size(size, size),
                painter: _RingPainter(
                  progress: 1.0,
                  color: Colors.white.withOpacity(0.1),
                  strokeWidth: 6,
                ),
              ),
              // Progress ring
              CustomPaint(
                size: Size(size, size),
                painter: _RingPainter(
                  progress: percentage,
                  color: color,
                  strokeWidth: 6,
                ),
              ),
              // Percentage text
              Text(
                '${(percentage * 100).toInt()}%',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: size * 0.2,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            color: Colors.white70,
            fontSize: 10,
          ),
        ),
        Text(
          '${value.toInt()}g',
          style: TextStyle(
            color: Colors.white,
            fontSize: 11,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  // 2. SUGGESTION BANNER
  Widget _buildSuggestionBanner() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.purple.withOpacity(0.2),
            Colors.blue.withOpacity(0.2),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.purple.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.purple.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(Icons.lightbulb_outline, color: Colors.purple, size: 24),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '💡 Coach Tip',
                  style: TextStyle(
                    color: Colors.purple,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'You\'re 200 cal away from your goal! Keep going! 🔥',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
          Icon(Icons.chevron_right, color: Colors.white54, size: 20),
        ],
      ),
    );
  }

  // 3. HIGHLIGHT CARD (Streaks/Wins)
  Widget _buildHighlightCard() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.orange.withOpacity(0.2),
            Colors.red.withOpacity(0.2),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: Colors.orange.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                '🔥',
                style: TextStyle(fontSize: 32),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '7 Day Streak!',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'You\'re on fire! Keep it up!',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _buildStatPill('🎯', '12/15', 'Goals'),
              const SizedBox(width: 12),
              _buildStatPill('💪', '5', 'Workouts'),
              const SizedBox(width: 12),
              _buildStatPill('📈', '+2kg', 'Progress'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatPill(String emoji, String value, String label) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(emoji, style: TextStyle(fontSize: 16)),
                const SizedBox(width: 4),
                Text(
                  value,
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                color: Colors.white54,
                fontSize: 11,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 4. VERTICAL FEED
  Widget _buildFeed() {
    return Consumer<TimelineProvider>(
      builder: (context, timeline, _) {
        if (timeline.isLoading && timeline.activities.isEmpty) {
          return SliverToBoxAdapter(
            child: Center(
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: CircularProgressIndicator(color: Colors.blue),
              ),
            ),
          );
        }

        if (timeline.activities.isEmpty) {
          return SliverToBoxAdapter(
            child: Center(
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: Column(
                  children: [
                    Icon(Icons.inbox_outlined, color: Colors.white38, size: 48),
                    const SizedBox(height: 16),
                    Text(
                      'No activities yet',
                      style: TextStyle(color: Colors.white54, fontSize: 16),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Start logging your meals and workouts!',
                      style: TextStyle(color: Colors.white38, fontSize: 14),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
          );
        }

        return SliverList(
          delegate: SliverChildBuilderDelegate(
            (context, index) {
              final activity = timeline.activities[index];
              return _buildFeedItem(activity);
            },
            childCount: timeline.activities.length,
          ),
        );
      },
    );
  }

  Widget _buildFeedItem(TimelineActivity activity) {
    IconData icon;
    Color color;

    switch (activity.type.toLowerCase()) {
      case 'meal':
        icon = Icons.restaurant;
        color = Colors.green;
        break;
      case 'workout':
        icon = Icons.fitness_center;
        color = Colors.orange;
        break;
      case 'water':
        icon = Icons.water_drop;
        color = Colors.blue;
        break;
      case 'supplement':
        icon = Icons.medication;
        color = Colors.purple;
        break;
      default:
        icon = Icons.circle;
        color = Colors.grey;
    }

    final details = activity.details;
    final calories = details?['calories'] ?? 0;
    final items = details?['items'] as List<dynamic>? ?? [];

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.white.withOpacity(0.1),
          width: 1,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Icon
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          
          const SizedBox(width: 12),
          
          // Content
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  activity.title,
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                if (items.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    items.join(', '),
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 13,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
                const SizedBox(height: 8),
                Row(
                  children: [
                    if (calories > 0) ...[
                      Icon(Icons.local_fire_department, color: Colors.orange, size: 14),
                      const SizedBox(width: 4),
                      Text(
                        '$calories cal',
                        style: TextStyle(
                          color: Colors.white54,
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(width: 12),
                    ],
                    Icon(Icons.access_time, color: Colors.white38, size: 14),
                    const SizedBox(width: 4),
                    Text(
                      _formatTime(activity.timestamp),
                      style: TextStyle(
                        color: Colors.white54,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          
          // Chevron
          Icon(Icons.chevron_right, color: Colors.white38, size: 20),
        ],
      ),
    );
  }

  String _formatTime(DateTime timestamp) {
    final now = DateTime.now();
    final diff = now.difference(timestamp);

    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }

}

// Ring Painter for activity rings
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
    final paint = Paint()
      ..color = color
      ..strokeWidth = strokeWidth
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width - strokeWidth) / 2;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      2 * math.pi * progress,
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(_RingPainter oldDelegate) {
    return oldDelegate.progress != progress ||
        oldDelegate.color != color ||
        oldDelegate.strokeWidth != strokeWidth;
  }
}

