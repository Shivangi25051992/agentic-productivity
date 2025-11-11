import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../screens/chat/chat_screen.dart';

/// 🎯 Radial Quick Actions Menu - Modern, Animated, Delightful
/// 
/// Features:
/// - Radial/fan animation from center FAB
/// - Haptic feedback on tap
/// - Gradient backgrounds
/// - Emoji + icon combo
/// - Smooth animations
/// - Dark overlay dismiss
class RadialQuickActions extends StatefulWidget {
  final VoidCallback onClose;

  const RadialQuickActions({super.key, required this.onClose});

  @override
  State<RadialQuickActions> createState() => _RadialQuickActionsState();
}

class _RadialQuickActionsState extends State<RadialQuickActions>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 400),
      vsync: this,
    );

    _scaleAnimation = CurvedAnimation(
      parent: _controller,
      curve: Curves.elasticOut,
    );

    _fadeAnimation = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOut,
    );

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _close() {
    _controller.reverse().then((_) => widget.onClose());
  }

  void _actionTapped(int actionIndex, BuildContext context) {
    // Haptic feedback for delight
    HapticFeedback.mediumImpact();

    // Close animation
    _controller.reverse().then((_) {
      widget.onClose();

      // Navigate based on action
      switch (actionIndex) {
        case 0: // Chat (NEW - opens empty chat)
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => ChatScreen(),
            ),
          );
          break;
        case 1: // Voice Log
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('🎤 Voice Log - Coming soon!'),
              behavior: SnackBarBehavior.floating,
              duration: Duration(seconds: 2),
            ),
          );
          break;
        case 2: // Log Meal
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => ChatScreen(initialMessage: 'Log my meal'),
            ),
          );
          break;
        case 3: // Log Water
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => ChatScreen(initialMessage: 'Log water'),
            ),
          );
          break;
        case 4: // Scan Food
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('📸 Scan Food - Coming soon!'),
              behavior: SnackBarBehavior.floating,
              duration: Duration(seconds: 2),
            ),
          );
          break;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final actions = [
      _ActionData(
        icon: Icons.chat_bubble,
        emoji: '💬',
        label: 'Chat',
        gradient: const LinearGradient(
          colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
        ),
      ),
      _ActionData(
        icon: Icons.mic,
        emoji: '🎤',
        label: 'Voice',
        gradient: const LinearGradient(
          colors: [Color(0xFFFF0055), Color(0xFFFF6B6B)],
        ),
      ),
      _ActionData(
        icon: Icons.restaurant,
        emoji: '🍽️',
        label: 'Meal',
        gradient: const LinearGradient(
          colors: [Color(0xFF34C759), Color(0xFF9CFF00)],
        ),
      ),
      _ActionData(
        icon: Icons.water_drop,
        emoji: '💧',
        label: 'Water',
        gradient: const LinearGradient(
          colors: [Color(0xFF007AFF), Color(0xFF00E8E8)],
        ),
      ),
      _ActionData(
        icon: Icons.camera_alt,
        emoji: '📸',
        label: 'Scan',
        gradient: const LinearGradient(
          colors: [Color(0xFFFF6B00), Color(0xFFFFB800)],
        ),
      ),
    ];

    return Material(
      color: Colors.transparent,
      child: Stack(
        fit: StackFit.expand,
        children: [
          // Dark overlay with fade animation
          FadeTransition(
            opacity: _fadeAnimation,
            child: GestureDetector(
              onTap: _close,
              child: Container(
                color: Colors.black.withOpacity(0.6),
              ),
            ),
          ),

          // Radial menu
          Center(
            child: SizedBox(
              width: 320,
              height: 320,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // Action buttons in radial layout
                  ...List.generate(actions.length, (i) {
                    // Calculate angle for radial spread
                    // Spread 5 items in a semi-circle (180 degrees)
                    final angle = (i - 2) * (pi / 4); // 45 degrees apart
                    final radius = 110.0;

                    return AnimatedBuilder(
                      animation: _scaleAnimation,
                      builder: (_, child) {
                        final currentRadius = radius * _scaleAnimation.value;
                        return Transform.translate(
                          offset: Offset(
                            currentRadius * sin(angle),
                            -currentRadius * cos(angle),
                          ),
                          child: child,
                        );
                      },
                      child: _buildActionButton(
                        context,
                        actions[i],
                        i,
                      ),
                    );
                  }),

                  // Center close button with scale animation
                  ScaleTransition(
                    scale: Tween<double>(begin: 0.0, end: 1.0).animate(
                      CurvedAnimation(
                        parent: _controller,
                        curve: Curves.elasticOut,
                      ),
                    ),
                    child: GestureDetector(
                      onTap: _close,
                      child: Container(
                        width: 64,
                        height: 64,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: const LinearGradient(
                            colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFF6366F1).withOpacity(0.4),
                              blurRadius: 20,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.close,
                          color: Colors.white,
                          size: 32,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton(
    BuildContext context,
    _ActionData action,
    int index,
  ) {
    return ScaleTransition(
      scale: Tween<double>(begin: 0.0, end: 1.0).animate(
        CurvedAnimation(
          parent: _controller,
          curve: Interval(
            0.1 * index,
            0.5 + (0.1 * index),
            curve: Curves.elasticOut,
          ),
        ),
      ),
      child: GestureDetector(
        onTap: () => _actionTapped(index, context),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Action button with gradient
            Container(
              width: 68,
              height: 68,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: action.gradient,
                boxShadow: [
                  BoxShadow(
                    color: action.gradient.colors.first.withOpacity(0.4),
                    blurRadius: 16,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // Icon
                  Icon(
                    action.icon,
                    color: Colors.white,
                    size: 32,
                  ),
                  // Emoji badge
                  Positioned(
                    top: 4,
                    right: 4,
                    child: Container(
                      width: 24,
                      height: 24,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.2),
                            blurRadius: 4,
                          ),
                        ],
                      ),
                      child: Center(
                        child: Text(
                          action.emoji,
                          style: const TextStyle(fontSize: 14),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),
            // Label
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 8,
                  ),
                ],
              ),
              child: Text(
                action.label,
                style: const TextStyle(
                  color: Color(0xFF1F2937),
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ActionData {
  final IconData icon;
  final String emoji;
  final String label;
  final Gradient gradient;

  _ActionData({
    required this.icon,
    required this.emoji,
    required this.label,
    required this.gradient,
  });
}

