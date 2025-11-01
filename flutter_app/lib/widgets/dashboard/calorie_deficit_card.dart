import 'package:flutter/material.dart';

/// Card showing calorie deficit/surplus
class CalorieDeficitCard extends StatelessWidget {
  final int caloriesConsumed;
  final int caloriesBurned;
  final int caloriesGoal;
  final int netCalories;
  final int deficit;
  final bool isInDeficit;

  const CalorieDeficitCard({
    super.key,
    required this.caloriesConsumed,
    required this.caloriesBurned,
    required this.caloriesGoal,
    required this.netCalories,
    required this.deficit,
    required this.isInDeficit,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    
    // Color based on deficit/surplus
    final statusColor = isInDeficit ? Colors.green : Colors.orange;
    final statusText = isInDeficit ? 'Deficit' : 'Surplus';
    final deficitAbs = deficit.abs();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            statusColor.withOpacity(0.1),
            statusColor.withOpacity(0.05),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: statusColor.withOpacity(0.3),
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Icon(
                isInDeficit ? Icons.trending_down : Icons.trending_up,
                color: statusColor,
                size: 24,
              ),
              const SizedBox(width: 8),
              Text(
                'Calorie Balance',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: statusColor),
                ),
                child: Text(
                  statusText,
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: statusColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Net Calories (Big Number)
          Center(
            child: Column(
              children: [
                Text(
                  'Net Calories',
                  style: theme.textTheme.labelMedium?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '$netCalories',
                  style: theme.textTheme.displayMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: statusColor,
                  ),
                ),
                Text(
                  'of $caloriesGoal goal',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Breakdown
          Row(
            children: [
              Expanded(
                child: _MetricColumn(
                  icon: Icons.restaurant,
                  label: 'Consumed',
                  value: '$caloriesConsumed',
                  color: Colors.blue,
                ),
              ),
              Container(
                width: 1,
                height: 40,
                color: colorScheme.outlineVariant,
              ),
              Expanded(
                child: _MetricColumn(
                  icon: Icons.local_fire_department,
                  label: 'Burned',
                  value: '$caloriesBurned',
                  color: Colors.orange,
                ),
              ),
              Container(
                width: 1,
                height: 40,
                color: colorScheme.outlineVariant,
              ),
              Expanded(
                child: _MetricColumn(
                  icon: isInDeficit ? Icons.arrow_downward : Icons.arrow_upward,
                  label: statusText,
                  value: '$deficitAbs',
                  color: statusColor,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _MetricColumn extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _MetricColumn({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }
}




