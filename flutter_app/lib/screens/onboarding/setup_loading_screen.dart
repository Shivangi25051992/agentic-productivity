import 'package:flutter/material.dart';
import 'dart:async';
import '../../config/onboarding_theme.dart';

class SetupLoadingScreen extends StatefulWidget {
  const SetupLoadingScreen({super.key});

  @override
  State<SetupLoadingScreen> createState() => _SetupLoadingScreenState();
}

class _SetupLoadingScreenState extends State<SetupLoadingScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  int _currentStep = 0;

  final List<_SetupStep> _steps = [
    _SetupStep(
      icon: Icons.restaurant_menu,
      title: 'Enabling Diet Plan',
      description: 'Setting up your personalized meal recommendations',
    ),
    _SetupStep(
      icon: Icons.fitness_center,
      title: 'Configuring Workout Goals',
      description: 'Tailoring exercises to your fitness level',
    ),
    _SetupStep(
      icon: Icons.analytics,
      title: 'Preparing Analytics',
      description: 'Building your progress tracking dashboard',
    ),
    _SetupStep(
      icon: Icons.check_circle,
      title: 'Finalizing Setup',
      description: 'Almost there! Getting everything ready',
    ),
  ];

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();

    _startSetupSequence();
  }

  void _startSetupSequence() async {
    for (int i = 0; i < _steps.length; i++) {
      await Future.delayed(const Duration(milliseconds: 1200));
      if (mounted) {
        setState(() => _currentStep = i);
      }
    }

    // Wait a bit before navigating
    await Future.delayed(const Duration(milliseconds: 800));
    if (mounted) {
      Navigator.of(context).pushReplacementNamed('/onboarding/success');
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: OnboardingTheme.bgCream,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Spacer(),

              // Main Title
              Text(
                'Setting up Your\nPersonalized Plan...',
                textAlign: TextAlign.center,
                style: OnboardingTheme.headingL.copyWith(
                  height: 1.3,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'This will only take a moment',
                textAlign: TextAlign.center,
                style: OnboardingTheme.bodyM.copyWith(
                  color: OnboardingTheme.textSecondary,
                ),
              ),
              const SizedBox(height: 60),

              // Animated Loading Circle
              SizedBox(
                width: 120,
                height: 120,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    // Rotating circle
                    AnimatedBuilder(
                      animation: _animationController,
                      builder: (context, child) {
                        return Transform.rotate(
                          angle: _animationController.value * 2 * 3.14159,
                          child: Container(
                            width: 120,
                            height: 120,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: OnboardingTheme.primaryTeal.withOpacity(0.2),
                                width: 3,
                              ),
                            ),
                            child: CustomPaint(
                              painter: _LoadingPainter(
                                progress: _animationController.value,
                                color: OnboardingTheme.primaryTeal,
                              ),
                            ),
                          ),
                        );
                      },
                    ),
                    // Center icon
                    Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: OnboardingTheme.primaryTeal.withOpacity(0.1),
                      ),
                      child: Icon(
                        _steps[_currentStep].icon,
                        size: 40,
                        color: OnboardingTheme.primaryTeal,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 60),

              // Setup Steps List
              SizedBox(
                height: 280,
                child: ListView.builder(
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _steps.length,
                  itemBuilder: (context, index) {
                    final step = _steps[index];
                    final isCompleted = index < _currentStep;
                    final isCurrent = index == _currentStep;
                    final isPending = index > _currentStep;

                    return AnimatedOpacity(
                      duration: const Duration(milliseconds: 300),
                      opacity: isPending ? 0.3 : 1.0,
                      child: Padding(
                        padding: const EdgeInsets.only(bottom: 16),
                        child: Row(
                          children: [
                            // Status Icon
                            AnimatedContainer(
                              duration: const Duration(milliseconds: 300),
                              width: 32,
                              height: 32,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: isCompleted
                                    ? OnboardingTheme.success
                                    : isCurrent
                                        ? OnboardingTheme.primaryTeal
                                        : OnboardingTheme.bgGray,
                                border: Border.all(
                                  color: isCompleted
                                      ? OnboardingTheme.success
                                      : isCurrent
                                          ? OnboardingTheme.primaryTeal
                                          : OnboardingTheme.textTertiary,
                                  width: 2,
                                ),
                              ),
                              child: isCompleted
                                  ? const Icon(
                                      Icons.check,
                                      size: 18,
                                      color: Colors.white,
                                    )
                                  : isCurrent
                                      ? Container(
                                          margin: const EdgeInsets.all(6),
                                          decoration: BoxDecoration(
                                            shape: BoxShape.circle,
                                            color: Colors.white,
                                          ),
                                        )
                                      : null,
                            ),
                            const SizedBox(width: 16),

                            // Step Info
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    step.title,
                                    style: OnboardingTheme.headingS.copyWith(
                                      fontSize: 15,
                                      color: isCompleted || isCurrent
                                          ? OnboardingTheme.textPrimary
                                          : OnboardingTheme.textTertiary,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    step.description,
                                    style: OnboardingTheme.bodyS.copyWith(
                                      fontSize: 12,
                                      color: OnboardingTheme.textTertiary,
                                    ),
                                  ),
                                ],
                              ),
                            ),

                            // Loading indicator for current step
                            if (isCurrent)
                              SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                    OnboardingTheme.primaryTeal,
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
              const Spacer(),

              // Progress indicator
              Column(
                children: [
                  Text(
                    '${((_currentStep + 1) / _steps.length * 100).round()}% Complete',
                    style: OnboardingTheme.bodyS.copyWith(
                      color: OnboardingTheme.textSecondary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 12),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(10),
                    child: LinearProgressIndicator(
                      value: (_currentStep + 1) / _steps.length,
                      backgroundColor: OnboardingTheme.bgGray,
                      valueColor: AlwaysStoppedAnimation<Color>(
                        OnboardingTheme.primaryTeal,
                      ),
                      minHeight: 8,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SetupStep {
  final IconData icon;
  final String title;
  final String description;

  _SetupStep({
    required this.icon,
    required this.title,
    required this.description,
  });
}

class _LoadingPainter extends CustomPainter {
  final double progress;
  final Color color;

  _LoadingPainter({required this.progress, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -3.14159 / 2,
      progress * 2 * 3.14159 * 0.75,
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(_LoadingPainter oldDelegate) => true;
}



