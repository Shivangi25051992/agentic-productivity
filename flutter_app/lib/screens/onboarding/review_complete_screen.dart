import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/onboarding_provider.dart';
import '../../providers/profile_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/onboarding/onboarding_step.dart';
import '../../models/user_profile.dart';

class ReviewCompleteScreen extends StatefulWidget {
  const ReviewCompleteScreen({super.key});

  @override
  State<ReviewCompleteScreen> createState() => _ReviewCompleteScreenState();
}

class _ReviewCompleteScreenState extends State<ReviewCompleteScreen> {
  bool _isCreating = false;

  Future<void> _createProfile() async {
    final onboarding = context.read<OnboardingProvider>();
    final profile = context.read<ProfileProvider>();
    final auth = context.read<AuthProvider>();

    setState(() {
      _isCreating = true;
    });

    final success = await profile.completeOnboarding(
      name: onboarding.name!,
      gender: onboarding.gender!,
      age: onboarding.age!,
      heightCm: onboarding.heightCm!,
      weightKg: onboarding.weightKg!,
      activityLevel: onboarding.activityLevel!,
      fitnessGoal: onboarding.fitnessGoal!,
      targetWeightKg: onboarding.targetWeightKg,
      dietPreference: onboarding.dietPreference,
      allergies: onboarding.allergies,
      dislikedFoods: onboarding.dislikedFoods,
      authProvider: auth,
    );

    setState(() {
      _isCreating = false;
    });

    if (success && mounted) {
      // Show setup loading screen
      onboarding.nextStep();
      Navigator.of(context).pushReplacementNamed('/onboarding/setup');
    } else if (mounted) {
      // Show error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(profile.errorMessage ?? 'Failed to create profile'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<OnboardingProvider>(
      builder: (context, provider, child) {
        return OnboardingStep(
          title: 'Review & Confirm',
          stepDisplay: provider.stepDisplay,
          progress: provider.progress,
          onBack: _isCreating
              ? null
              : () {
                  provider.previousStep();
                  Navigator.of(context).pop();
                },
          onNext: _isCreating ? null : _createProfile,
          isNextEnabled: !_isCreating,
          nextButtonText: _isCreating ? 'Creating Profile...' : 'Create My Profile 🎉',
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Summary card
              _SummarySection(
                title: 'Basic Info',
                icon: '👤',
                items: [
                  'Name: ${provider.name}',
                  'Gender: ${provider.gender?.displayName}',
                  'Age: ${provider.age} years',
                  'Height: ${provider.heightCm} cm',
                  'Weight: ${provider.weightKg} kg',
                ],
              ),
              const SizedBox(height: 16),
              _SummarySection(
                title: 'Activity & Goals',
                icon: '🎯',
                items: [
                  'Activity: ${provider.activityLevel?.displayName}',
                  'Goal: ${provider.fitnessGoal?.displayName}',
                ],
              ),
              const SizedBox(height: 16),
              _SummarySection(
                title: 'Daily Targets',
                icon: '📊',
                items: [
                  'Calories: ${provider.calculatedGoals?['recommended_goals']?['calories']} cal',
                  'Protein: ${provider.calculatedGoals?['recommended_goals']?['protein_g']}g',
                  'Carbs: ${provider.calculatedGoals?['recommended_goals']?['carbs_g']}g',
                  'Fat: ${provider.calculatedGoals?['recommended_goals']?['fat_g']}g',
                ],
              ),
              if (provider.dietPreference != DietPreference.none ||
                  provider.allergies.isNotEmpty ||
                  provider.dislikedFoods.isNotEmpty) ...[
                const SizedBox(height: 16),
                _SummarySection(
                  title: 'Preferences',
                  icon: '🥗',
                  items: [
                    if (provider.dietPreference != DietPreference.none)
                      'Diet: ${provider.dietPreference.displayName}',
                    if (provider.allergies.isNotEmpty) 'Allergies: ${provider.allergies.join(", ")}',
                    if (provider.dislikedFoods.isNotEmpty)
                      'Avoid: ${provider.dislikedFoods.join(", ")}',
                  ],
                ),
              ],
              const SizedBox(height: 24),
              // Info message
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    const Text('💡', style: TextStyle(fontSize: 24)),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'You can always update these settings later in your profile.',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _SummarySection extends StatelessWidget {
  final String title;
  final String icon;
  final List<String> items;

  const _SummarySection({
    required this.title,
    required this.icon,
    required this.items,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).dividerColor.withOpacity(0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(icon, style: const TextStyle(fontSize: 24)),
              const SizedBox(width: 8),
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...items.map((item) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  '• $item',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              )),
        ],
      ),
    );
  }
}


