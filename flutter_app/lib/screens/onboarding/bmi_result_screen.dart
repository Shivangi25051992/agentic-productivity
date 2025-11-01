import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:math';

import '../../providers/onboarding_provider.dart';
import '../../models/user_profile.dart';
import '../../widgets/onboarding/onboarding_step.dart';
import '../../config/onboarding_theme.dart';

class BMIResultScreen extends StatefulWidget {
  const BMIResultScreen({super.key});

  @override
  State<BMIResultScreen> createState() => _BMIResultScreenState();
}

class _BMIResultScreenState extends State<BMIResultScreen> with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    
    _scaleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.elasticOut,
      ),
    );
    
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.easeIn,
      ),
    );
    
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  double _calculateBMI(int heightCm, double weightKg) {
    final heightM = heightCm / 100.0;
    return weightKg / (heightM * heightM);
  }

  String _getBMICategory(double bmi) {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
  }

  Color _getBMIColor(double bmi) {
    if (bmi < 18.5) return OnboardingTheme.accentBlue;
    if (bmi < 25) return OnboardingTheme.success;
    if (bmi < 30) return OnboardingTheme.warning;
    return OnboardingTheme.error;
  }

  Map<String, double> _getIdealWeightRange(int heightCm, Gender gender) {
    final heightM = heightCm / 100.0;
    // Using WHO BMI standards (18.5 - 24.9)
    final minWeight = 18.5 * heightM * heightM;
    final maxWeight = 24.9 * heightM * heightM;
    
    return {
      'min': double.parse(minWeight.toStringAsFixed(1)),
      'max': double.parse(maxWeight.toStringAsFixed(1)),
    };
  }

  double _suggestTargetWeight(double currentWeight, FitnessGoal goal, Map<String, double> idealRange) {
    switch (goal) {
      case FitnessGoal.loseWeight:
        // Suggest 10% weight loss or ideal max, whichever is closer
        final tenPercent = currentWeight * 0.9;
        return min(tenPercent, idealRange['max']!);
      case FitnessGoal.gainMuscle:
        // Suggest 10% weight gain or ideal min, whichever is closer
        final tenPercent = currentWeight * 1.1;
        return max(tenPercent, idealRange['min']!);
      case FitnessGoal.maintain:
      case FitnessGoal.improveFitness:
        // Suggest current weight if in range, otherwise closest ideal
        if (currentWeight >= idealRange['min']! && currentWeight <= idealRange['max']!) {
          return currentWeight;
        }
        return currentWeight < idealRange['min']! ? idealRange['min']! : idealRange['max']!;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<OnboardingProvider>(
      builder: (context, provider, child) {
        final heightCm = provider.heightCm ?? 170;
        final weightKg = provider.weightKg ?? 70;
        final gender = provider.gender ?? Gender.male;
        final goal = provider.fitnessGoal ?? FitnessGoal.maintain;
        
        final bmi = _calculateBMI(heightCm, weightKg);
        final category = _getBMICategory(bmi);
        final color = _getBMIColor(bmi);
        final idealRange = _getIdealWeightRange(heightCm, gender);
        final suggestedTarget = _suggestTargetWeight(weightKg, goal, idealRange);

        return OnboardingStep(
          title: 'Your Health Metrics',
          stepDisplay: provider.stepDisplay,
          progress: provider.progress,
          onBack: () {
            provider.previousStep();
            Navigator.of(context).pop();
          },
          onNext: () {
            // Auto-set suggested target weight if not already set
            if (provider.targetWeightKg == null && goal == FitnessGoal.loseWeight) {
              provider.updateTargetWeight(suggestedTarget);
            }
            provider.nextStep();
            Navigator.of(context).pushNamed('/onboarding/activity-level');
          },
          isNextEnabled: true,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Helper text
              FadeTransition(
                opacity: _fadeAnimation,
                child: Text(
                  'Based on your height and weight, here\'s your health profile:',
                  style: OnboardingTheme.bodyM.copyWith(
                    color: OnboardingTheme.textSecondary,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
              const SizedBox(height: 32),

              // BMI Circle
              ScaleTransition(
                scale: _scaleAnimation,
                child: Center(
                  child: Container(
                    width: 180,
                    height: 180,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: LinearGradient(
                        colors: [
                          color.withOpacity(0.2),
                          color.withOpacity(0.1),
                        ],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: color.withOpacity(0.3),
                          blurRadius: 20,
                          offset: const Offset(0, 10),
                        ),
                      ],
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          bmi.toStringAsFixed(1),
                          style: OnboardingTheme.headingXL.copyWith(
                            color: color,
                            fontSize: 48,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'BMI',
                          style: OnboardingTheme.bodyS.copyWith(
                            color: OnboardingTheme.textTertiary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            color: color.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            category,
                            style: OnboardingTheme.bodyS.copyWith(
                              color: color,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 40),

              // Ideal Weight Range Card
              FadeTransition(
                opacity: _fadeAnimation,
                child: Container(
                  padding: const EdgeInsets.all(20),
                  decoration: OnboardingTheme.cardDecoration(
                    color: OnboardingTheme.bgGray,
                    shadow: OnboardingTheme.shadowS,
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: OnboardingTheme.success.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Icon(
                              Icons.favorite,
                              color: OnboardingTheme.success,
                              size: 20,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Ideal Weight Range',
                                  style: OnboardingTheme.headingS.copyWith(
                                    fontSize: 16,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Based on your BMI of ${bmi.toStringAsFixed(1)}, your ideal weight range is:',
                                  style: OnboardingTheme.bodyS.copyWith(
                                    color: OnboardingTheme.textTertiary,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: OnboardingTheme.bgWhite,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: OnboardingTheme.success.withOpacity(0.3),
                            width: 2,
                          ),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              '${idealRange['min']!.toStringAsFixed(1)} kg',
                              style: OnboardingTheme.headingM.copyWith(
                                color: OnboardingTheme.success,
                              ),
                            ),
                            Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 12),
                              child: Text(
                                '—',
                                style: OnboardingTheme.headingM.copyWith(
                                  color: OnboardingTheme.textTertiary,
                                ),
                              ),
                            ),
                            Text(
                              '${idealRange['max']!.toStringAsFixed(1)} kg',
                              style: OnboardingTheme.headingM.copyWith(
                                color: OnboardingTheme.success,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Suggested Target (if losing/gaining weight)
              if (goal != FitnessGoal.maintain && goal != FitnessGoal.improveFitness)
                FadeTransition(
                  opacity: _fadeAnimation,
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    decoration: OnboardingTheme.cardDecoration(
                      color: OnboardingTheme.primaryTeal.withOpacity(0.05),
                      shadow: OnboardingTheme.shadowS,
                    ),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: OnboardingTheme.primaryTeal.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Icon(
                            goal == FitnessGoal.loseWeight
                                ? Icons.trending_down
                                : Icons.trending_up,
                            color: OnboardingTheme.primaryTeal,
                            size: 20,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Suggested Target Weight',
                                style: OnboardingTheme.headingS.copyWith(
                                  fontSize: 16,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${suggestedTarget.toStringAsFixed(1)} kg',
                                style: OnboardingTheme.headingL.copyWith(
                                  color: OnboardingTheme.primaryTeal,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                goal == FitnessGoal.loseWeight
                                    ? 'A healthy, achievable goal for you'
                                    : 'A healthy target to reach',
                                style: OnboardingTheme.bodyS.copyWith(
                                  color: OnboardingTheme.textTertiary,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

              const SizedBox(height: 24),

              // Info note
              FadeTransition(
                opacity: _fadeAnimation,
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: OnboardingTheme.info.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: OnboardingTheme.info.withOpacity(0.3),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.info_outline,
                        color: OnboardingTheme.info,
                        size: 20,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Don\'t worry if you don\'t match the ideal range. We\'ll create a personalized plan just for you!',
                          style: OnboardingTheme.bodyS.copyWith(
                            color: OnboardingTheme.info,
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
      },
    );
  }
}

