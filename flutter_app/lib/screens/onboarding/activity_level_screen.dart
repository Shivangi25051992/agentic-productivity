import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../models/user_profile.dart';
import '../../providers/onboarding_provider.dart';
import '../../widgets/onboarding/onboarding_step.dart';
import '../../widgets/onboarding/selection_card.dart';

class ActivityLevelScreen extends StatelessWidget {
  const ActivityLevelScreen({super.key});

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
          onNext: () {
            provider.nextStep();
            Navigator.of(context).pushNamed('/onboarding/fitness-goal');
          },
          isNextEnabled: provider.isStep2Valid,
          child: Column(
            children: ActivityLevel.values.map((level) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: SelectionCard(
                  emoji: level.emoji,
                  title: level.displayName,
                  description: level.description,
                  isSelected: provider.activityLevel == level,
                  onTap: () {
                    provider.updateActivityLevel(level);
                  },
                ),
              );
            }).toList(),
          ),
        );
      },
    );
  }
}





