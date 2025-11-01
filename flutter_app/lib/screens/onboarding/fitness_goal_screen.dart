import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../../models/user_profile.dart';
import '../../providers/onboarding_provider.dart';
import '../../providers/profile_provider.dart';
import '../../widgets/onboarding/onboarding_step.dart';
import '../../widgets/onboarding/selection_card.dart';

class FitnessGoalScreen extends StatefulWidget {
  const FitnessGoalScreen({super.key});

  @override
  State<FitnessGoalScreen> createState() => _FitnessGoalScreenState();
}

class _FitnessGoalScreenState extends State<FitnessGoalScreen> {
  late TextEditingController _targetWeightController;

  @override
  void initState() {
    super.initState();
    final provider = context.read<OnboardingProvider>();
    _targetWeightController = TextEditingController(
      text: provider.targetWeightKg?.toString() ?? '',
    );
  }

  @override
  void dispose() {
    _targetWeightController.dispose();
    super.dispose();
  }

  Future<void> _handleNext(BuildContext context) async {
    final onboardingProvider = context.read<OnboardingProvider>();
    final profileProvider = context.read<ProfileProvider>();

    // Calculate goals before moving to next step
    if (onboardingProvider.isStep3Valid) {
      // Show loading
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const Center(
          child: CircularProgressIndicator(),
        ),
      );

      // Call API to calculate goals
      final goals = await profileProvider.calculateGoals(
        gender: onboardingProvider.gender!,
        age: onboardingProvider.age!,
        heightCm: onboardingProvider.heightCm!,
        weightKg: onboardingProvider.weightKg!,
        activityLevel: onboardingProvider.activityLevel!,
        fitnessGoal: onboardingProvider.fitnessGoal!,
        targetWeightKg: onboardingProvider.targetWeightKg,
      );

      // Hide loading
      if (context.mounted) {
        Navigator.of(context).pop();
      }

      if (goals != null) {
        onboardingProvider.setCalculatedGoals(goals);
        onboardingProvider.nextStep();
        if (context.mounted) {
          Navigator.of(context).pushNamed('/onboarding/preferences');
        }
      } else {
        // Show error
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Failed to calculate goals. Please try again.'),
            ),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<OnboardingProvider>(
      builder: (context, provider, child) {
        return OnboardingStep(
          title: provider.stepTitle,
          stepDisplay: provider.stepDisplay,
          progress: provider.progress,
          onBack: () {
            provider.previousStep();
            Navigator.of(context).pop();
          },
          onNext: () => _handleNext(context),
          isNextEnabled: provider.isStep3Valid,
          nextButtonText: 'Calculate My Goals',
          child: Column(
            children: [
              // Goal selection cards
              ...FitnessGoal.values.map((goal) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: SelectionCard(
                    emoji: goal.emoji,
                    title: goal.displayName,
                    description: goal.description,
                    isSelected: provider.fitnessGoal == goal,
                    onTap: () {
                      provider.updateFitnessGoal(goal);
                    },
                  ),
                );
              }),
              
              // Target weight input (show only for lose/gain goals)
              if (provider.fitnessGoal == FitnessGoal.loseWeight || 
                  provider.fitnessGoal == FitnessGoal.gainMuscle) ...[
                const SizedBox(height: 24),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.flag_outlined,
                            color: Theme.of(context).colorScheme.primary,
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Target Weight',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _targetWeightController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        inputFormatters: [
                          FilteringTextInputFormatter.allow(RegExp(r'^\d+\.?\d{0,1}')),
                        ],
                        decoration: InputDecoration(
                          labelText: 'Target Weight (kg)',
                          hintText: 'e.g., ${provider.fitnessGoal == FitnessGoal.loseWeight ? (provider.weightKg! - 5).toStringAsFixed(0) : (provider.weightKg! + 5).toStringAsFixed(0)}',
                          prefixIcon: const Icon(Icons.monitor_weight_outlined),
                          suffixText: 'kg',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          helperText: 'Optional: Set your target weight for better recommendations',
                          helperMaxLines: 2,
                        ),
                        onChanged: (value) {
                          final weight = double.tryParse(value);
                          provider.updateTargetWeight(weight);
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}


