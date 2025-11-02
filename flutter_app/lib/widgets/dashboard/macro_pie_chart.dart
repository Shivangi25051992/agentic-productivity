import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class MacroPieChart extends StatelessWidget {
  final double proteinG;
  final double carbsG;
  final double fatG;
  final double proteinGoal;
  final double carbsGoal;
  final double fatGoal;

  const MacroPieChart({
    super.key,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.proteinGoal,
    required this.carbsGoal,
    required this.fatGoal,
  });

  @override
  Widget build(BuildContext context) {
    final total = proteinG + carbsG + fatG;
    
    if (total == 0) {
      return _buildEmptyState(context);
    }

    return Column(
      children: [
        // Pie Chart
        SizedBox(
          height: 200,
          child: PieChart(
            PieChartData(
              sectionsSpace: 2,
              centerSpaceRadius: 60,
              sections: [
                // Protein
                PieChartSectionData(
                  value: proteinG,
                  title: '${(proteinG / total * 100).toStringAsFixed(0)}%',
                  color: Colors.red,
                  radius: 50,
                  titleStyle: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                // Carbs
                PieChartSectionData(
                  value: carbsG,
                  title: '${(carbsG / total * 100).toStringAsFixed(0)}%',
                  color: Colors.amber,
                  radius: 50,
                  titleStyle: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                // Fat
                PieChartSectionData(
                  value: fatG,
                  title: '${(fatG / total * 100).toStringAsFixed(0)}%',
                  color: Colors.green,
                  radius: 50,
                  titleStyle: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        // Legend
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _buildLegendItem(
              context,
              color: Colors.red,
              label: 'Protein',
              value: '${proteinG.toStringAsFixed(0)}g',
              goal: '${proteinGoal.toStringAsFixed(0)}g',
            ),
            _buildLegendItem(
              context,
              color: Colors.amber,
              label: 'Carbs',
              value: '${carbsG.toStringAsFixed(0)}g',
              goal: '${carbsGoal.toStringAsFixed(0)}g',
            ),
            _buildLegendItem(
              context,
              color: Colors.green,
              label: 'Fat',
              value: '${fatG.toStringAsFixed(0)}g',
              goal: '${fatGoal.toStringAsFixed(0)}g',
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const SizedBox(height: 40),
        Text(
          '🍽️',
          style: const TextStyle(fontSize: 48),
        ),
        const SizedBox(height: 16),
        Text(
          'No meals logged yet',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Theme.of(context).textTheme.bodySmall?.color,
              ),
        ),
        const SizedBox(height: 8),
        Text(
          'Start tracking your nutrition!',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        const SizedBox(height: 40),
      ],
    );
  }

  Widget _buildLegendItem(
    BuildContext context, {
    required Color color,
    required String label,
    required String value,
    required String goal,
  }) {
    return Column(
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 4),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        Text(
          'of $goal',
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }
}





