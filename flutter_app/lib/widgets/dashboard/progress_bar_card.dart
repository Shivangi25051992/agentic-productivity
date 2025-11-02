import 'package:flutter/material.dart';

class ProgressBarCard extends StatelessWidget {
  final String emoji;
  final String label;
  final String current;
  final String goal;
  final double progress; // 0.0 to 1.0
  final Color color;
  final VoidCallback? onTap;

  const ProgressBarCard({
    super.key,
    required this.emoji,
    required this.label,
    required this.current,
    required this.goal,
    required this.progress,
    required this.color,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isOverGoal = progress > 1.0;
    final displayProgress = progress.clamp(0.0, 1.0);

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: Theme.of(context).dividerColor.withOpacity(0.1),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Text(emoji, style: const TextStyle(fontSize: 24)),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    label,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ),
                Text(
                  '$current / $goal',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: isOverGoal ? Colors.orange : color,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Progress Bar
            Stack(
              children: [
                // Background
                Container(
                  height: 8,
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                // Progress
                FractionallySizedBox(
                  widthFactor: displayProgress,
                  child: Container(
                    height: 8,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: isOverGoal
                            ? [Colors.orange, Colors.deepOrange]
                            : [color.withOpacity(0.7), color],
                      ),
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                ),
              ],
            ),
            if (isOverGoal) ...[
              const SizedBox(height: 8),
              Text(
                'Over goal by ${(progress * 100 - 100).toStringAsFixed(0)}%',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.orange,
                      fontWeight: FontWeight.w500,
                    ),
              ),
            ] else if (progress >= 0.9) ...[
              const SizedBox(height: 8),
              Text(
                'Almost there! 🎯',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: color,
                      fontWeight: FontWeight.w500,
                    ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}





