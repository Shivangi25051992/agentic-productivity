import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../../models/user_profile.dart';
import '../../providers/onboarding_provider.dart';
import '../../widgets/onboarding/onboarding_step.dart';
import '../../config/onboarding_theme.dart';

class BasicInfoScreenEnhanced extends StatefulWidget {
  const BasicInfoScreenEnhanced({super.key});

  @override
  State<BasicInfoScreenEnhanced> createState() => _BasicInfoScreenEnhancedState();
}

class _BasicInfoScreenEnhancedState extends State<BasicInfoScreenEnhanced> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _ageController;
  late TextEditingController _heightFtController;
  late TextEditingController _heightInController;
  late TextEditingController _heightCmController;
  late TextEditingController _weightController;

  bool _isHeightMetric = true; // true = cm, false = ft/in
  bool _isWeightMetric = true; // true = kg, false = lb

  @override
  void initState() {
    super.initState();
    final provider = context.read<OnboardingProvider>();
    _nameController = TextEditingController(text: provider.name);
    _ageController = TextEditingController(text: provider.age?.toString());
    
    // Initialize height controllers
    if (provider.heightCm != null) {
      _heightCmController = TextEditingController(text: provider.heightCm.toString());
      final feet = (provider.heightCm! / 30.48).floor();
      final inches = ((provider.heightCm! / 2.54) - (feet * 12)).round();
      _heightFtController = TextEditingController(text: feet.toString());
      _heightInController = TextEditingController(text: inches.toString());
    } else {
      _heightCmController = TextEditingController();
      _heightFtController = TextEditingController();
      _heightInController = TextEditingController();
    }
    
    // Initialize weight controller
    if (provider.weightKg != null) {
      _weightController = TextEditingController(text: provider.weightKg.toString());
    } else {
      _weightController = TextEditingController();
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _ageController.dispose();
    _heightFtController.dispose();
    _heightInController.dispose();
    _heightCmController.dispose();
    _weightController.dispose();
    super.dispose();
  }

  int? _getHeightInCm() {
    if (_isHeightMetric) {
      return int.tryParse(_heightCmController.text);
    } else {
      final ft = int.tryParse(_heightFtController.text) ?? 0;
      final inches = int.tryParse(_heightInController.text) ?? 0;
      if (ft > 0 || inches > 0) {
        return ((ft * 12 + inches) * 2.54).round();
      }
    }
    return null;
  }

  double? _getWeightInKg() {
    final value = double.tryParse(_weightController.text);
    if (value == null) return null;
    return _isWeightMetric ? value : value * 0.453592; // lb to kg
  }

  void _convertHeight(bool toMetric) {
    if (toMetric) {
      // Convert ft/in to cm
      final ft = int.tryParse(_heightFtController.text) ?? 0;
      final inches = int.tryParse(_heightInController.text) ?? 0;
      if (ft > 0 || inches > 0) {
        final cm = ((ft * 12 + inches) * 2.54).round();
        _heightCmController.text = cm.toString();
      }
    } else {
      // Convert cm to ft/in
      final cm = int.tryParse(_heightCmController.text) ?? 0;
      if (cm > 0) {
        final totalInches = (cm / 2.54).round();
        final ft = totalInches ~/ 12;
        final inches = totalInches % 12;
        _heightFtController.text = ft.toString();
        _heightInController.text = inches.toString();
      }
    }
  }

  void _convertWeight(bool toMetric) {
    final value = double.tryParse(_weightController.text);
    if (value != null) {
      if (toMetric) {
        // Convert lb to kg
        _weightController.text = (value * 0.453592).toStringAsFixed(1);
      } else {
        // Convert kg to lb
        _weightController.text = (value / 0.453592).toStringAsFixed(1);
      }
    }
  }

  void _handleNext() {
    if (_formKey.currentState!.validate()) {
      final provider = context.read<OnboardingProvider>();
      provider.updateBasicInfo(
        name: _nameController.text.trim(),
        age: int.tryParse(_ageController.text),
        heightCm: _getHeightInCm(),
        weightKg: _getWeightInKg(),
      );
      provider.nextStep();
      Navigator.of(context).pushNamed('/onboarding/bmi-result');
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
          onNext: _handleNext,
          isNextEnabled: provider.isStep1Valid,
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Helper text
                Text(
                  'This will help us calculate your body metrics and personalize your experience.',
                  style: OnboardingTheme.bodyM.copyWith(
                    color: OnboardingTheme.textSecondary,
                  ),
                ),
                const SizedBox(height: 24),

                // Name
                TextFormField(
                  controller: _nameController,
                  decoration: OnboardingTheme.inputDecoration(
                    label: 'What\'s your name?',
                    hint: 'Enter your name',
                    prefixIcon: Icon(Icons.person_outline, color: OnboardingTheme.primaryTeal),
                  ),
                  textCapitalization: TextCapitalization.words,
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Please enter your name';
                    }
                    return null;
                  },
                  onChanged: (value) {
                    provider.updateBasicInfo(name: value.trim());
                  },
                ),
                const SizedBox(height: 24),

                // Gender
                Text(
                  'Gender',
                  style: OnboardingTheme.headingS.copyWith(fontSize: 16),
                ),
                const SizedBox(height: 8),
                Text(
                  'We support all forms of gender expression. However, we need this to calculate your body metrics.',
                  style: OnboardingTheme.bodyS.copyWith(
                    color: OnboardingTheme.textTertiary,
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: _GenderCard(
                        icon: Icons.male,
                        label: 'Male',
                        isSelected: provider.gender == Gender.male,
                        onTap: () {
                          provider.updateBasicInfo(gender: Gender.male);
                        },
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _GenderCard(
                        icon: Icons.female,
                        label: 'Female',
                        isSelected: provider.gender == Gender.female,
                        onTap: () {
                          provider.updateBasicInfo(gender: Gender.female);
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // Age
                TextFormField(
                  controller: _ageController,
                  decoration: OnboardingTheme.inputDecoration(
                    label: 'Age',
                    hint: 'Enter your age',
                    prefixIcon: Icon(Icons.cake_outlined, color: OnboardingTheme.primaryTeal),
                  ),
                  keyboardType: TextInputType.number,
                  inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter your age';
                    }
                    final age = int.tryParse(value);
                    if (age == null || age < 13 || age > 120) {
                      return 'Please enter a valid age (13-120)';
                    }
                    return null;
                  },
                  onChanged: (value) {
                    provider.updateBasicInfo(age: int.tryParse(value));
                  },
                ),
                const SizedBox(height: 24),

                // Height
                Text(
                  'Height',
                  style: OnboardingTheme.headingS.copyWith(fontSize: 16),
                ),
                const SizedBox(height: 8),
                Text(
                  'Your height will help us calculate important body stats to help you reach your goals faster.',
                  style: OnboardingTheme.bodyS.copyWith(
                    color: OnboardingTheme.textTertiary,
                  ),
                ),
                const SizedBox(height: 12),
                
                // Height unit toggle
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    _UnitToggle(
                      label: 'Ft/In',
                      isSelected: !_isHeightMetric,
                      onTap: () {
                        if (_isHeightMetric) {
                          _convertHeight(false);
                          setState(() => _isHeightMetric = false);
                        }
                      },
                    ),
                    const SizedBox(width: 12),
                    _UnitToggle(
                      label: 'Cm',
                      isSelected: _isHeightMetric,
                      onTap: () {
                        if (!_isHeightMetric) {
                          _convertHeight(true);
                          setState(() => _isHeightMetric = true);
                        }
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // Height input
                if (_isHeightMetric)
                  TextFormField(
                    controller: _heightCmController,
                    decoration: OnboardingTheme.inputDecoration(
                      label: 'Height (cm)',
                      hint: 'Enter height in cm',
                      prefixIcon: Icon(Icons.height, color: OnboardingTheme.primaryTeal),
                    ),
                    keyboardType: TextInputType.number,
                    inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter your height';
                      }
                      final height = int.tryParse(value);
                      if (height == null || height < 100 || height > 250) {
                        return 'Please enter a valid height (100-250 cm)';
                      }
                      return null;
                    },
                    onChanged: (value) {
                      provider.updateBasicInfo(heightCm: int.tryParse(value));
                    },
                  )
                else
                  Row(
                    children: [
                      Expanded(
                        child: TextFormField(
                          controller: _heightFtController,
                          decoration: OnboardingTheme.inputDecoration(
                            label: 'Feet',
                            hint: 'Ft',
                          ),
                          keyboardType: TextInputType.number,
                          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                          validator: (value) {
                            if ((value == null || value.isEmpty) && 
                                (_heightInController.text.isEmpty)) {
                              return 'Required';
                            }
                            return null;
                          },
                          onChanged: (value) {
                            provider.updateBasicInfo(heightCm: _getHeightInCm());
                          },
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: TextFormField(
                          controller: _heightInController,
                          decoration: OnboardingTheme.inputDecoration(
                            label: 'Inches',
                            hint: 'In',
                          ),
                          keyboardType: TextInputType.number,
                          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                          validator: (value) {
                            if ((value == null || value.isEmpty) && 
                                (_heightFtController.text.isEmpty)) {
                              return 'Required';
                            }
                            final inches = int.tryParse(value ?? '0') ?? 0;
                            if (inches > 11) {
                              return 'Max 11';
                            }
                            return null;
                          },
                          onChanged: (value) {
                            provider.updateBasicInfo(heightCm: _getHeightInCm());
                          },
                        ),
                      ),
                    ],
                  ),
                const SizedBox(height: 24),

                // Weight
                Text(
                  'Weight',
                  style: OnboardingTheme.headingS.copyWith(fontSize: 16),
                ),
                const SizedBox(height: 8),
                Text(
                  'This will help us determine your goal, and monitor your progress over time.',
                  style: OnboardingTheme.bodyS.copyWith(
                    color: OnboardingTheme.textTertiary,
                  ),
                ),
                const SizedBox(height: 12),
                
                // Weight unit toggle
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    _UnitToggle(
                      label: 'Kg',
                      isSelected: _isWeightMetric,
                      onTap: () {
                        if (!_isWeightMetric) {
                          _convertWeight(true);
                          setState(() => _isWeightMetric = true);
                        }
                      },
                    ),
                    const SizedBox(width: 12),
                    _UnitToggle(
                      label: 'Lb',
                      isSelected: !_isWeightMetric,
                      onTap: () {
                        if (_isWeightMetric) {
                          _convertWeight(false);
                          setState(() => _isWeightMetric = false);
                        }
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // Weight input
                TextFormField(
                  controller: _weightController,
                  decoration: OnboardingTheme.inputDecoration(
                    label: 'Weight (${_isWeightMetric ? 'kg' : 'lb'})',
                    hint: 'Enter your current weight',
                    prefixIcon: Icon(Icons.monitor_weight_outlined, color: OnboardingTheme.primaryTeal),
                  ),
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  inputFormatters: [
                    FilteringTextInputFormatter.allow(RegExp(r'^\d+\.?\d{0,1}')),
                  ],
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter your weight';
                    }
                    final weight = double.tryParse(value);
                    if (weight == null) {
                      return 'Please enter a valid weight';
                    }
                    final minKg = _isWeightMetric ? 30 : 66;
                    final maxKg = _isWeightMetric ? 300 : 661;
                    if (weight < minKg || weight > maxKg) {
                      return 'Please enter a valid weight ($minKg-$maxKg ${_isWeightMetric ? 'kg' : 'lb'})';
                    }
                    return null;
                  },
                  onChanged: (value) {
                    provider.updateBasicInfo(weightKg: _getWeightInKg());
                  },
                ),
                const SizedBox(height: 16),

                // Info note
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: OnboardingTheme.info.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.info_outline,
                        color: OnboardingTheme.info,
                        size: 16,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Don\'t worry if you don\'t know it precisely - you can change this later from settings.',
                          style: OnboardingTheme.bodyS.copyWith(
                            color: OnboardingTheme.info,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _GenderCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _GenderCard({
    required this.icon,
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(OnboardingTheme.radiusM),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 20),
        decoration: OnboardingTheme.selectableCard(isSelected: isSelected),
        child: Column(
          children: [
            Icon(
              icon,
              size: 32,
              color: isSelected ? OnboardingTheme.primaryTeal : OnboardingTheme.textSecondary,
            ),
            const SizedBox(height: 8),
            Text(
              label,
              style: OnboardingTheme.bodyM.copyWith(
                color: isSelected ? OnboardingTheme.primaryTeal : OnboardingTheme.textSecondary,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _UnitToggle extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _UnitToggle({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? OnboardingTheme.primaryTeal : OnboardingTheme.bgGray,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? OnboardingTheme.primaryTeal : Colors.transparent,
            width: 2,
          ),
        ),
        child: Text(
          label,
          style: OnboardingTheme.buttonM.copyWith(
            color: isSelected ? Colors.white : OnboardingTheme.textSecondary,
          ),
        ),
      ),
    );
  }
}



