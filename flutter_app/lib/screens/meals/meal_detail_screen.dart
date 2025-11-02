import 'package:flutter/material.dart';

class MealDetailScreen extends StatelessWidget {
  final String mealType;
  final List<dynamic> activities;

  const MealDetailScreen({
    Key? key,
    required this.mealType,
    required this.activities,
  }) : super(key: key);

  String _getMealIcon(String type) {
    switch (type) {
      case 'breakfast':
        return '🌅';
      case 'lunch':
        return '🌞';
      case 'snack':
        return '🍎';
      case 'dinner':
        return '🌙';
      default:
        return '🍽️';
    }
  }

  String _getMealLabel(String type) {
    return type[0].toUpperCase() + type.substring(1);
  }

  String _formatTime(DateTime dateTime) {
    final hour = dateTime.hour;
    final minute = dateTime.minute.toString().padLeft(2, '0');
    final period = hour >= 12 ? 'PM' : 'AM';
    final displayHour = hour > 12 ? hour - 12 : (hour == 0 ? 12 : hour);
    return '$displayHour:$minute $period';
  }

  @override
  Widget build(BuildContext context) {
    // Calculate totals
    int totalCalories = 0;
    double totalProtein = 0;
    double totalCarbs = 0;
    double totalFat = 0;
    double totalFiber = 0;

    for (final activity in activities) {
      final data = activity.data ?? {};
      totalCalories += (data['calories'] as num?)?.toInt() ?? 0;
      totalProtein += (data['protein_g'] as num?)?.toDouble() ?? 0;
      totalCarbs += (data['carbs_g'] as num?)?.toDouble() ?? 0;
      totalFat += (data['fat_g'] as num?)?.toDouble() ?? 0;
      totalFiber += (data['fiber_g'] as num?)?.toDouble() ?? 0;
    }

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Text(_getMealIcon(mealType), style: const TextStyle(fontSize: 24)),
            const SizedBox(width: 8),
            Text(_getMealLabel(mealType)),
          ],
        ),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Meal Summary Card
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  gradient: LinearGradient(
                    colors: [
                      Theme.of(context).primaryColor.withOpacity(0.1),
                      Theme.of(context).primaryColor.withOpacity(0.05),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '📊 Meal Summary',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _buildNutrientColumn(
                          'Calories',
                          '$totalCalories',
                          'kcal',
                          Colors.orange,
                        ),
                        _buildNutrientColumn(
                          'Protein',
                          totalProtein.toStringAsFixed(1),
                          'g',
                          Colors.red,
                        ),
                        _buildNutrientColumn(
                          'Carbs',
                          totalCarbs.toStringAsFixed(1),
                          'g',
                          Colors.blue,
                        ),
                        _buildNutrientColumn(
                          'Fat',
                          totalFat.toStringAsFixed(1),
                          'g',
                          Colors.purple,
                        ),
                      ],
                    ),
                    if (totalFiber > 0) ...[
                      const SizedBox(height: 12),
                      Text(
                        'Fiber: ${totalFiber.toStringAsFixed(1)}g',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Food Items Section
            Text(
              '🍽️ Food Items (${activities.length})',
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),

            // List of food items
            ...activities.asMap().entries.map((entry) {
              final index = entry.key;
              final activity = entry.value;
              final data = activity.data ?? {};
              final description = data['description'] as String? ?? 'Unknown food';
              final calories = (data['calories'] as num?)?.toInt() ?? 0;
              final protein = (data['protein_g'] as num?)?.toDouble() ?? 0;
              final carbs = (data['carbs_g'] as num?)?.toDouble() ?? 0;
              final fat = (data['fat_g'] as num?)?.toDouble() ?? 0;
              final fiber = (data['fiber_g'] as num?)?.toDouble() ?? 0;
              final timestamp = activity.timestamp;

              return Card(
                elevation: 1,
                margin: const EdgeInsets.only(bottom: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Food name and time
                      Row(
                        children: [
                          Container(
                            width: 32,
                            height: 32,
                            decoration: BoxDecoration(
                              color: Theme.of(context).primaryColor.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Center(
                              child: Text(
                                '${index + 1}',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Theme.of(context).primaryColor,
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  description,
                                  style: const TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                Text(
                                  _formatTime(timestamp),
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 12),
                      const Divider(height: 1),
                      const SizedBox(height: 12),

                      // Macros
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _buildMacroChip('🔥 $calories kcal', Colors.orange),
                          _buildMacroChip('💪 ${protein.toStringAsFixed(1)}g', Colors.red),
                          _buildMacroChip('🌾 ${carbs.toStringAsFixed(1)}g', Colors.blue),
                          _buildMacroChip('🥑 ${fat.toStringAsFixed(1)}g', Colors.purple),
                        ],
                      ),

                      if (fiber > 0) ...[
                        const SizedBox(height: 8),
                        _buildMacroChip('🌿 Fiber: ${fiber.toStringAsFixed(1)}g', Colors.green),
                      ],

                      // Source/confidence if available
                      if (data['estimated'] == true) ...[
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.orange.shade50,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.info_outline, size: 14, color: Colors.orange.shade700),
                              const SizedBox(width: 4),
                              Text(
                                'Estimated',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.orange.shade700,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              );
            }).toList(),

            const SizedBox(height: 24),

            // Action buttons
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      // TODO: Implement edit meal
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Edit meal coming soon!')),
                      );
                    },
                    icon: const Icon(Icons.edit),
                    label: const Text('Edit Meal'),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      // TODO: Implement delete meal
                      _showDeleteConfirmation(context);
                    },
                    icon: const Icon(Icons.delete_outline),
                    label: const Text('Delete'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.red,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildNutrientColumn(String label, String value, String unit, Color color) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          unit,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
      ],
    );
  }

  Widget _buildMacroChip(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: color,
        ),
      ),
    );
  }

  void _showDeleteConfirmation(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Meal?'),
        content: Text('Are you sure you want to delete this ${_getMealLabel(mealType).toLowerCase()}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pop(); // Go back to home
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Delete meal coming soon!')),
              );
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}

