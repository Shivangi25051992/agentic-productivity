import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:math' as math;

import '../../providers/onboarding_provider.dart';
import '../../config/onboarding_theme.dart';

class SuccessScreenEnhanced extends StatefulWidget {
  const SuccessScreenEnhanced({super.key});

  @override
  State<SuccessScreenEnhanced> createState() => _SuccessScreenEnhancedState();
}

class _SuccessScreenEnhancedState extends State<SuccessScreenEnhanced>
    with TickerProviderStateMixin {
  late AnimationController _confettiController;
  late AnimationController _scaleController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  final List<_ConfettiParticle> _confetti = [];

  @override
  void initState() {
    super.initState();

    // Confetti animation
    _confettiController = AnimationController(
      duration: const Duration(seconds: 3),
      vsync: this,
    );

    // Scale animation for success icon
    _scaleController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _scaleController,
        curve: Curves.elasticOut,
      ),
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _scaleController,
        curve: Curves.easeIn,
      ),
    );

    // Generate confetti particles
    _generateConfetti();

    // Start animations
    _scaleController.forward();
    _confettiController.forward();
  }

  void _generateConfetti() {
    final random = math.Random();
    for (int i = 0; i < 50; i++) {
      _confetti.add(_ConfettiParticle(
        x: random.nextDouble(),
        y: -0.1 - random.nextDouble() * 0.2,
        color: _getRandomColor(random),
        size: 4 + random.nextDouble() * 6,
        rotation: random.nextDouble() * math.pi * 2,
        velocityY: 0.3 + random.nextDouble() * 0.5,
        velocityX: -0.1 + random.nextDouble() * 0.2,
      ));
    }
  }

  Color _getRandomColor(math.Random random) {
    final colors = [
      OnboardingTheme.primaryTeal,
      OnboardingTheme.accentBlue,
      OnboardingTheme.accentPurple,
      OnboardingTheme.accentPink,
      OnboardingTheme.accentOrange,
      OnboardingTheme.accentGreen,
    ];
    return colors[random.nextInt(colors.length)];
  }

  @override
  void dispose() {
    _confettiController.dispose();
    _scaleController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: OnboardingTheme.bgCream,
      body: Stack(
        children: [
          // Confetti
          AnimatedBuilder(
            animation: _confettiController,
            builder: (context, child) {
              return CustomPaint(
                painter: _ConfettiPainter(
                  confetti: _confetti,
                  animation: _confettiController.value,
                ),
                size: Size.infinite,
              );
            },
          ),

          // Content
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Consumer<OnboardingProvider>(
                builder: (context, provider, child) {
                  final goals = provider.getFinalGoals();
                  
                  return Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Spacer(),

                      // Success Icon
                      ScaleTransition(
                        scale: _scaleAnimation,
                        child: Container(
                          width: 140,
                          height: 140,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: LinearGradient(
                              colors: [
                                OnboardingTheme.success,
                                OnboardingTheme.success.withOpacity(0.7),
                              ],
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: OnboardingTheme.success.withOpacity(0.4),
                                blurRadius: 30,
                                offset: const Offset(0, 10),
                              ),
                            ],
                          ),
                          child: const Icon(
                            Icons.check_circle,
                            size: 80,
                            color: Colors.white,
                          ),
                        ),
                      ),
                      const SizedBox(height: 40),

                      // Success Message
                      FadeTransition(
                        opacity: _fadeAnimation,
                        child: Column(
                          children: [
                            Text(
                              'You\'re All Set,\n${provider.name ?? 'Champion'}! 🎉',
                              textAlign: TextAlign.center,
                              style: OnboardingTheme.headingXL.copyWith(
                                height: 1.2,
                              ),
                            ),
                            const SizedBox(height: 16),
                            Text(
                              'Your personalized fitness plan is ready.\nLet\'s start your transformation!',
                              textAlign: TextAlign.center,
                              style: OnboardingTheme.bodyL.copyWith(
                                color: OnboardingTheme.textSecondary,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 48),

                      // Goals Summary Card
                      if (goals != null)
                        FadeTransition(
                          opacity: _fadeAnimation,
                          child: Container(
                            padding: const EdgeInsets.all(24),
                            decoration: OnboardingTheme.cardDecoration(
                              gradient: LinearGradient(
                                colors: [
                                  OnboardingTheme.primaryTeal.withOpacity(0.1),
                                  OnboardingTheme.accentBlue.withOpacity(0.05),
                                ],
                              ),
                            ),
                            child: Column(
                              children: [
                                Row(
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.all(8),
                                      decoration: BoxDecoration(
                                        color: OnboardingTheme.primaryTeal.withOpacity(0.2),
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Icon(
                                        Icons.emoji_events,
                                        color: OnboardingTheme.primaryTeal,
                                        size: 24,
                                      ),
                                    ),
                                    const SizedBox(width: 12),
                                    Text(
                                      'Your Daily Goals',
                                      style: OnboardingTheme.headingS,
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 20),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                                  children: [
                                    _buildGoalStat(
                                      '${goals.calories.round()}',
                                      'Calories',
                                      Icons.local_fire_department,
                                      OnboardingTheme.accentOrange,
                                    ),
                                    _buildGoalStat(
                                      '${goals.proteinG}g',
                                      'Protein',
                                      Icons.egg,
                                      OnboardingTheme.accentPurple,
                                    ),
                                    _buildGoalStat(
                                      '${goals.carbsG}g',
                                      'Carbs',
                                      Icons.bakery_dining,
                                      OnboardingTheme.accentBlue,
                                    ),
                                    _buildGoalStat(
                                      '${goals.fatG}g',
                                      'Fat',
                                      Icons.water_drop,
                                      OnboardingTheme.accentGreen,
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ),
                      const Spacer(),

                      // Start Journey Button
                      FadeTransition(
                        opacity: _fadeAnimation,
                        child: Column(
                          children: [
                            SizedBox(
                              width: double.infinity,
                              height: 56,
                              child: ElevatedButton(
                                onPressed: () {
                                  Navigator.of(context).pushReplacementNamed('/home');
                                },
                                style: OnboardingTheme.primaryButton,
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      'Start Your Journey',
                                      style: OnboardingTheme.buttonL.copyWith(
                                        color: Colors.white,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    const Icon(Icons.arrow_forward, size: 20),
                                  ],
                                ),
                              ),
                            ),
                            const SizedBox(height: 16),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: OnboardingTheme.info.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    Icons.lightbulb_outline,
                                    color: OnboardingTheme.info,
                                    size: 16,
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    'Tip: Use the chat to log meals instantly!',
                                    style: OnboardingTheme.bodyS.copyWith(
                                      color: OnboardingTheme.info,
                                      fontSize: 12,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 20),
                    ],
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGoalStat(String value, String label, IconData icon, Color color) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: color, size: 20),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: OnboardingTheme.headingS.copyWith(
            color: color,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: OnboardingTheme.caption.copyWith(
            color: OnboardingTheme.textTertiary,
          ),
        ),
      ],
    );
  }
}

class _ConfettiParticle {
  double x;
  double y;
  final Color color;
  final double size;
  double rotation;
  final double velocityY;
  final double velocityX;

  _ConfettiParticle({
    required this.x,
    required this.y,
    required this.color,
    required this.size,
    required this.rotation,
    required this.velocityY,
    required this.velocityX,
  });
}

class _ConfettiPainter extends CustomPainter {
  final List<_ConfettiParticle> confetti;
  final double animation;

  _ConfettiPainter({required this.confetti, required this.animation});

  @override
  void paint(Canvas canvas, Size size) {
    for (var particle in confetti) {
      final paint = Paint()
        ..color = particle.color.withOpacity(1.0 - animation * 0.5)
        ..style = PaintingStyle.fill;

      final x = particle.x * size.width + particle.velocityX * animation * size.width;
      final y = particle.y * size.height + particle.velocityY * animation * size.height;

      canvas.save();
      canvas.translate(x, y);
      canvas.rotate(particle.rotation + animation * math.pi * 4);
      canvas.drawRect(
        Rect.fromCenter(
          center: Offset.zero,
          width: particle.size,
          height: particle.size,
        ),
        paint,
      );
      canvas.restore();
    }
  }

  @override
  bool shouldRepaint(_ConfettiPainter oldDelegate) => true;
}

