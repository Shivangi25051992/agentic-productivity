import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../models/user_profile.dart';
import '../../providers/onboarding_provider.dart';
import '../../widgets/onboarding/onboarding_step.dart';
import '../../widgets/onboarding/selection_card.dart';

class PreferencesScreen extends StatefulWidget {
  const PreferencesScreen({super.key});

  @override
  State<PreferencesScreen> createState() => _PreferencesScreenState();
}

class _PreferencesScreenState extends State<PreferencesScreen> {
  final _allergyController = TextEditingController();
  final _dislikedFoodController = TextEditingController();

  @override
  void dispose() {
    _allergyController.dispose();
    _dislikedFoodController.dispose();
    super.dispose();
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
          onNext: () {
            provider.nextStep();
            Navigator.of(context).pushNamed('/onboarding/review');
          },
          isNextEnabled: provider.isStep5Valid,
          nextButtonText: 'Continue',
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Diet Preference
              Text(
                'Diet Preference (Optional)',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 12),
              ...DietPreference.values.map((pref) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: SelectionCard(
                    emoji: _getDietEmoji(pref),
                    title: pref.displayName,
                    description: '',
                    isSelected: provider.dietPreference == pref,
                    onTap: () {
                      provider.updatePreferences(diet: pref);
                    },
                  ),
                );
              }),
              const SizedBox(height: 24),

              // Allergies
              Text(
                'Allergies (Optional)',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'Let us know if you have any food allergies',
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _allergyController,
                      decoration: InputDecoration(
                        hintText: 'e.g., Peanuts, Shellfish',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      onSubmitted: (value) {
                        if (value.trim().isNotEmpty) {
                          provider.addAllergy(value.trim());
                          _allergyController.clear();
                        }
                      },
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    onPressed: () {
                      if (_allergyController.text.trim().isNotEmpty) {
                        provider.addAllergy(_allergyController.text.trim());
                        _allergyController.clear();
                      }
                    },
                    icon: const Icon(Icons.add_circle),
                    color: Theme.of(context).colorScheme.primary,
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: provider.allergies.map((allergy) {
                  return Chip(
                    label: Text(allergy),
                    onDeleted: () {
                      provider.removeAllergy(allergy);
                    },
                    deleteIcon: const Icon(Icons.close, size: 18),
                  );
                }).toList(),
              ),
              const SizedBox(height: 24),

              // Disliked Foods
              Text(
                'Disliked Foods (Optional)',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'Foods you prefer to avoid',
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _dislikedFoodController,
                      decoration: InputDecoration(
                        hintText: 'e.g., Broccoli, Mushrooms',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      onSubmitted: (value) {
                        if (value.trim().isNotEmpty) {
                          provider.addDislikedFood(value.trim());
                          _dislikedFoodController.clear();
                        }
                      },
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    onPressed: () {
                      if (_dislikedFoodController.text.trim().isNotEmpty) {
                        provider.addDislikedFood(_dislikedFoodController.text.trim());
                        _dislikedFoodController.clear();
                      }
                    },
                    icon: const Icon(Icons.add_circle),
                    color: Theme.of(context).colorScheme.primary,
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: provider.dislikedFoods.map((food) {
                  return Chip(
                    label: Text(food),
                    onDeleted: () {
                      provider.removeDislikedFood(food);
                    },
                    deleteIcon: const Icon(Icons.close, size: 18),
                  );
                }).toList(),
              ),
            ],
          ),
        );
      },
    );
  }

  String _getDietEmoji(DietPreference pref) {
    switch (pref) {
      case DietPreference.none:
        return '🍽️';
      case DietPreference.vegetarian:
        return '🥗';
      case DietPreference.vegan:
        return '🌱';
      case DietPreference.pescatarian:
        return '🐟';
      case DietPreference.keto:
        return '🥓';
      case DietPreference.paleo:
        return '🥩';
      case DietPreference.lowCarb:
        return '🥬';
      case DietPreference.highProtein:
        return '💪';
    }
  }
}





