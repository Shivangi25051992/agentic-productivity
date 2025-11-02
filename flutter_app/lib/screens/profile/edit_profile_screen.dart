import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../../models/user_profile.dart';
import '../../providers/profile_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/common/custom_button.dart';

class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({super.key});

  @override
  State<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _weightController;
  late TextEditingController _targetWeightController;
  
  ActivityLevel? _selectedActivityLevel;
  FitnessGoal? _selectedFitnessGoal;
  DietPreference? _selectedDietPreference;
  List<String> _allergies = [];
  List<String> _dislikedFoods = [];
  
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    final profile = context.read<ProfileProvider>().profile!;
    
    _nameController = TextEditingController(text: profile.name);
    _weightController = TextEditingController(text: profile.weightKg.toString());
    _targetWeightController = TextEditingController(
      text: profile.targetWeightKg?.toString() ?? '',
    );
    
    _selectedActivityLevel = profile.activityLevel;
    _selectedFitnessGoal = profile.fitnessGoal;
    _selectedDietPreference = profile.dietPreference;
    _allergies = List.from(profile.allergies);
    _dislikedFoods = List.from(profile.dislikedFoods);
  }

  @override
  void dispose() {
    _nameController.dispose();
    _weightController.dispose();
    _targetWeightController.dispose();
    super.dispose();
  }

  Future<void> _saveChanges() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final profileProvider = context.read<ProfileProvider>();
    final authProvider = context.read<AuthProvider>();

    final success = await profileProvider.updateProfile(
      name: _nameController.text.trim(),
      weightKg: double.tryParse(_weightController.text),
      activityLevel: _selectedActivityLevel,
      fitnessGoal: _selectedFitnessGoal,
      targetWeightKg: _targetWeightController.text.isEmpty
          ? null
          : double.tryParse(_targetWeightController.text),
      dietPreference: _selectedDietPreference,
      allergies: _allergies,
      dislikedFoods: _dislikedFoods,
      authProvider: authProvider,
    );

    setState(() => _isLoading = false);

    if (mounted) {
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Profile updated successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.of(context).pop();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(profileProvider.errorMessage ?? 'Failed to update profile'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Profile'),
        actions: [
          if (_isLoading)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Basic Info Section
            _buildSectionHeader('Basic Information'),
            const SizedBox(height: 16),
            
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Name',
                prefixIcon: Icon(Icons.person),
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter your name';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            
            TextFormField(
              controller: _weightController,
              decoration: const InputDecoration(
                labelText: 'Current Weight (kg)',
                prefixIcon: Icon(Icons.monitor_weight),
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'^\d+\.?\d{0,1}')),
              ],
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Please enter your weight';
                }
                final weight = double.tryParse(value);
                if (weight == null || weight < 30 || weight > 300) {
                  return 'Please enter a valid weight (30-300 kg)';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            
            TextFormField(
              controller: _targetWeightController,
              decoration: const InputDecoration(
                labelText: 'Target Weight (kg) - Optional',
                prefixIcon: Icon(Icons.flag),
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'^\d+\.?\d{0,1}')),
              ],
              validator: (value) {
                if (value != null && value.isNotEmpty) {
                  final weight = double.tryParse(value);
                  if (weight == null || weight < 30 || weight > 300) {
                    return 'Please enter a valid weight (30-300 kg)';
                  }
                }
                return null;
              },
            ),
            
            const SizedBox(height: 32),
            
            // Activity & Goals Section
            _buildSectionHeader('Activity & Goals'),
            const SizedBox(height: 16),
            
            DropdownButtonFormField<ActivityLevel>(
              value: _selectedActivityLevel,
              decoration: const InputDecoration(
                labelText: 'Activity Level',
                prefixIcon: Icon(Icons.directions_run),
                border: OutlineInputBorder(),
              ),
              items: ActivityLevel.values.map((level) {
                return DropdownMenuItem(
                  value: level,
                  child: Text('${level.emoji} ${level.displayName}'),
                );
              }).toList(),
              onChanged: (value) {
                setState(() => _selectedActivityLevel = value);
              },
              validator: (value) {
                if (value == null) return 'Please select activity level';
                return null;
              },
            ),
            const SizedBox(height: 16),
            
            DropdownButtonFormField<FitnessGoal>(
              value: _selectedFitnessGoal,
              decoration: const InputDecoration(
                labelText: 'Fitness Goal',
                prefixIcon: Icon(Icons.emoji_events),
                border: OutlineInputBorder(),
              ),
              items: FitnessGoal.values.map((goal) {
                return DropdownMenuItem(
                  value: goal,
                  child: Text('${goal.emoji} ${goal.displayName}'),
                );
              }).toList(),
              onChanged: (value) {
                setState(() => _selectedFitnessGoal = value);
              },
              validator: (value) {
                if (value == null) return 'Please select fitness goal';
                return null;
              },
            ),
            
            const SizedBox(height: 32),
            
            // Preferences Section
            _buildSectionHeader('Dietary Preferences'),
            const SizedBox(height: 16),
            
            DropdownButtonFormField<DietPreference>(
              value: _selectedDietPreference,
              decoration: const InputDecoration(
                labelText: 'Diet Preference',
                prefixIcon: Icon(Icons.restaurant),
                border: OutlineInputBorder(),
              ),
              items: DietPreference.values.map((pref) {
                return DropdownMenuItem(
                  value: pref,
                  child: Text(pref.displayName),
                );
              }).toList(),
              onChanged: (value) {
                setState(() => _selectedDietPreference = value);
              },
            ),
            const SizedBox(height: 16),
            
            // Allergies
            _buildListEditor(
              label: 'Allergies',
              items: _allergies,
              onAdd: (value) {
                setState(() => _allergies.add(value));
              },
              onRemove: (index) {
                setState(() => _allergies.removeAt(index));
              },
              icon: Icons.warning_amber,
            ),
            const SizedBox(height: 16),
            
            // Disliked Foods
            _buildListEditor(
              label: 'Disliked Foods',
              items: _dislikedFoods,
              onAdd: (value) {
                setState(() => _dislikedFoods.add(value));
              },
              onRemove: (index) {
                setState(() => _dislikedFoods.removeAt(index));
              },
              icon: Icons.block,
            ),
            
            const SizedBox(height: 32),
            
            // Save Button
            CustomButton(
              text: 'Save Changes',
              onPressed: _isLoading ? null : _saveChanges,
              isLoading: _isLoading,
            ),
            const SizedBox(height: 16),
            
            // Cancel Button
            OutlinedButton(
              onPressed: _isLoading ? null : () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Text(
      title,
      style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
    );
  }

  Widget _buildListEditor({
    required String label,
    required List<String> items,
    required Function(String) onAdd,
    required Function(int) onRemove,
    required IconData icon,
  }) {
    final controller = TextEditingController();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 8),
        
        // Add new item
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: controller,
                decoration: InputDecoration(
                  hintText: 'Add $label',
                  prefixIcon: Icon(icon),
                  border: const OutlineInputBorder(),
                ),
                onSubmitted: (value) {
                  if (value.trim().isNotEmpty) {
                    onAdd(value.trim());
                    controller.clear();
                  }
                },
              ),
            ),
            const SizedBox(width: 8),
            IconButton(
              onPressed: () {
                if (controller.text.trim().isNotEmpty) {
                  onAdd(controller.text.trim());
                  controller.clear();
                }
              },
              icon: const Icon(Icons.add_circle),
              color: Theme.of(context).colorScheme.primary,
            ),
          ],
        ),
        const SizedBox(height: 8),
        
        // List of items
        if (items.isEmpty)
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Text(
              'No $label added',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey,
                  ),
            ),
          )
        else
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: items.asMap().entries.map((entry) {
              return Chip(
                label: Text(entry.value),
                deleteIcon: const Icon(Icons.close, size: 18),
                onDeleted: () => onRemove(entry.key),
              );
            }).toList(),
          ),
      ],
    );
  }
}

