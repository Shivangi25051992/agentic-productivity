import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../models/user_profile.dart';
import '../../providers/onboarding_provider.dart';
import '../../widgets/onboarding/onboarding_step.dart';

class GoalReviewScreen extends StatelessWidget {
  const GoalReviewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<OnboardingProvider>(
      builder: (context, provider, child) {
        final goals = provider.calculatedGoals;
        if (goals == null) {
          return const Scaffold(
            body: Center(child: Text('No goals calculated')),
          );
        }

        final recommendedGoals = goals['recommended_goals'] as Map<String, dynamic>?;
        final metabolicInfo = goals['metabolic_info'] as Map<String, dynamic>?;
        final tips = (goals['tips'] as List<dynamic>?)?.cast<String>() ?? [];

        return OnboardingStep(
          title: provider.stepTitle,
          stepDisplay: provider.stepDisplay,
          progress: provider.progress,
          onBack: () {
            provider.previousStep();
            Navigator.of(context).pop();
          },
          onNext: () {
            provider.nextStep();
            Navigator.of(context).pushNamed('/onboarding/preferences');
          },
          isNextEnabled: provider.isStep4Valid,
          nextButtonText: 'Looks Good!',
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Success message
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    const Text('🎯', style: TextStyle(fontSize: 32)),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Your personalized plan is ready!',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Metabolic Info
              if (metabolicInfo != null) ...[
                Text(
                  'Your Metabolism',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surface,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: Theme.of(context).dividerColor.withOpacity(0.2),
                    ),
                  ),
                  child: Column(
                    children: [
                      _MetricRow(
                        label: 'BMR (at rest)',
                        value: '${metabolicInfo['bmr']} cal/day',
                        icon: '💤',
                      ),
                      const Divider(height: 24),
                      _MetricRow(
                        label: 'TDEE (total)',
                        value: '${metabolicInfo['tdee']} cal/day',
                        icon: '🔥',
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  metabolicInfo['explanation'] as String? ?? '',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 24),
              ],

              // Daily Goals
              if (recommendedGoals != null) ...[
                Text(
                  'Your Daily Goals',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 12),
                _GoalCard(
                  icon: '🔥',
                  label: 'Calories',
                  value: '${recommendedGoals['calories']} cal',
                  color: Colors.orange,
                ),
                const SizedBox(height: 8),
                _GoalCard(
                  icon: '💪',
                  label: 'Protein',
                  value: '${recommendedGoals['protein_g']}g',
                  color: Colors.red,
                ),
                const SizedBox(height: 8),
                _GoalCard(
                  icon: '🌾',
                  label: 'Carbs',
                  value: '${recommendedGoals['carbs_g']}g',
                  color: Colors.amber,
                ),
                const SizedBox(height: 8),
                _GoalCard(
                  icon: '🥑',
                  label: 'Fat',
                  value: '${recommendedGoals['fat_g']}g',
                  color: Colors.green,
                ),
                const SizedBox(height: 8),
                _GoalCard(
                  icon: '🥬',
                  label: 'Fiber',
                  value: '${recommendedGoals['fiber_g']}g',
                  color: Colors.lightGreen,
                ),
                const SizedBox(height: 8),
                _GoalCard(
                  icon: '💧',
                  label: 'Water',
                  value: '${(recommendedGoals['water_ml'] as int) / 1000}L',
                  color: Colors.blue,
                ),
                const SizedBox(height: 8),
                _GoalCard(
                  icon: '🏋️',
                  label: 'Workouts',
                  value: '${recommendedGoals['workouts_per_week']}/week',
                  color: Colors.purple,
                ),
                const SizedBox(height: 24),
              ],

              // Tips
              if (tips.isNotEmpty) ...[
                Text(
                  'Tips for Success',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 12),
                ...tips.map((tip) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('💡 ', style: TextStyle(fontSize: 16)),
                          Expanded(
                            child: Text(
                              tip,
                              style: Theme.of(context).textTheme.bodyMedium,
                            ),
                          ),
                        ],
                      ),
                    )),
              ],
            ],
          ),
        );
      },
    );
  }
}

class _MetricRow extends StatelessWidget {
  final String label;
  final String value;
  final String icon;

  const _MetricRow({
    required this.label,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(icon, style: const TextStyle(fontSize: 24)),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ),
        Text(
          value,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
      ],
    );
  }
}

class _GoalCard extends StatelessWidget {
  final String icon;
  final String label;
  final String value;
  final Color color;

  const _GoalCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.3),
        ),
      ),
      child: Row(
        children: [
          Text(icon, style: const TextStyle(fontSize: 24)),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
            ),
          ),
          Text(
            value,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
          ),
        ],
      ),
    );
  }
}





