import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../config/onboarding_theme.dart';

class WelcomeScreenEnhanced extends StatefulWidget {
  const WelcomeScreenEnhanced({super.key});

  @override
  State<WelcomeScreenEnhanced> createState() => _WelcomeScreenEnhancedState();
}

class _WelcomeScreenEnhancedState extends State<WelcomeScreenEnhanced>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: const Interval(0.0, 0.6, curve: Curves.easeIn),
      ),
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: const Interval(0.3, 1.0, curve: Curves.easeOut),
      ),
    );

    _animationController.forward();
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
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          TextButton.icon(
            onPressed: () async {
              final auth = context.read<AuthProvider>();
              await auth.signOut();
              if (context.mounted) {
                Navigator.of(context).pushReplacementNamed('/login');
              }
            },
            icon: const Icon(Icons.logout, size: 18),
            label: const Text('Logout'),
            style: TextButton.styleFrom(
              foregroundColor: OnboardingTheme.textTertiary,
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            children: [
              const SizedBox(height: 20),
              
              // Animated Logo
              FadeTransition(
                opacity: _fadeAnimation,
                child: Container(
                  width: 140,
                  height: 140,
                  decoration: BoxDecoration(
                    gradient: OnboardingTheme.primaryGradient,
                    borderRadius: BorderRadius.circular(35),
                    boxShadow: OnboardingTheme.shadowGlow,
                  ),
                  child: const Icon(
                    Icons.fitness_center,
                    size: 70,
                    color: Colors.white,
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // Welcome Text
              FadeTransition(
                opacity: _fadeAnimation,
                child: Column(
                  children: [
                    Text(
                      'Welcome to Your\nFitness Journey! 🎯',
                      textAlign: TextAlign.center,
                      style: OnboardingTheme.headingXL.copyWith(
                        height: 1.2,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Let\'s personalize your experience\nand set you up for success',
                      textAlign: TextAlign.center,
                      style: OnboardingTheme.bodyL.copyWith(
                        color: OnboardingTheme.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 40),

              // Social Proof Stats
              SlideTransition(
                position: _slideAnimation,
                child: FadeTransition(
                  opacity: _fadeAnimation,
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    decoration: OnboardingTheme.cardDecoration(
                      gradient: LinearGradient(
                        colors: [
                          OnboardingTheme.primaryTeal.withOpacity(0.1),
                          OnboardingTheme.accentBlue.withOpacity(0.05),
                        ],
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _buildStat('10K+', 'Active Users', Icons.people),
                        Container(
                          width: 1,
                          height: 40,
                          color: OnboardingTheme.textTertiary.withOpacity(0.2),
                        ),
                        _buildStat('500K+', 'Meals Logged', Icons.restaurant),
                        Container(
                          width: 1,
                          height: 40,
                          color: OnboardingTheme.textTertiary.withOpacity(0.2),
                        ),
                        _buildStat('5kg', 'Avg. Lost', Icons.trending_down),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 40),

              // Features List
              SlideTransition(
                position: _slideAnimation,
                child: FadeTransition(
                  opacity: _fadeAnimation,
                  child: Column(
                    children: [
                      _buildFeature(
                        context,
                        icon: '🍽️',
                        iconColor: OnboardingTheme.accentOrange,
                        title: 'Smart Nutrition Tracking',
                        description: 'Log meals with AI-powered macro breakdown',
                      ),
                      const SizedBox(height: 16),
                      _buildFeature(
                        context,
                        icon: '💪',
                        iconColor: OnboardingTheme.accentPurple,
                        title: 'Personalized Goals',
                        description: 'Get custom calorie and macro targets',
                      ),
                      const SizedBox(height: 16),
                      _buildFeature(
                        context,
                        icon: '📊',
                        iconColor: OnboardingTheme.accentBlue,
                        title: 'Progress Insights',
                        description: 'Track your journey with detailed analytics',
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 40),

              // Get Started Button
              SlideTransition(
                position: _slideAnimation,
                child: FadeTransition(
                  opacity: _fadeAnimation,
                  child: Column(
                    children: [
                      SizedBox(
                        width: double.infinity,
                        height: 56,
                        child: ElevatedButton(
                          onPressed: () {
                            Navigator.of(context).pushReplacementNamed('/onboarding/basic-info');
                          },
                          style: OnboardingTheme.primaryButton,
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                'Get Started',
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
                      // Skip Button
                      TextButton(
                        onPressed: () {
                          Navigator.of(context).pushReplacementNamed('/home');
                        },
                        style: OnboardingTheme.textButton,
                        child: Text(
                          'Skip for now',
                          style: OnboardingTheme.bodyM.copyWith(
                            color: OnboardingTheme.textTertiary,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStat(String value, String label, IconData icon) {
    return Column(
      children: [
        Icon(
          icon,
          color: OnboardingTheme.primaryTeal,
          size: 24,
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: OnboardingTheme.headingM.copyWith(
            color: OnboardingTheme.primaryTeal,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: OnboardingTheme.caption.copyWith(
            color: OnboardingTheme.textSecondary,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildFeature(
    BuildContext context, {
    required String icon,
    required Color iconColor,
    required String title,
    required String description,
  }) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: OnboardingTheme.cardDecoration(),
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: iconColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Center(
              child: Text(
                icon,
                style: const TextStyle(fontSize: 28),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: OnboardingTheme.headingS.copyWith(
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: OnboardingTheme.bodyS.copyWith(
                    color: OnboardingTheme.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}



