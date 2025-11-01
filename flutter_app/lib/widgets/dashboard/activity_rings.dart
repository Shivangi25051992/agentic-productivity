import 'dart:math' as math;
import 'package:flutter/material.dart';

/// Apple Watch-style Activity Rings widget
/// Shows progress for calories, protein, carbs, and fat as concentric rings
class ActivityRings extends StatelessWidget {
  final double caloriesProgress;
  final double proteinProgress;
  final double carbsProgress;
  final double fatProgress;
  final int caloriesConsumed;
  final int caloriesGoal;
  final double proteinG;
  final double proteinGoal;
  final double carbsG;
  final double carbsGoal;
  final double fatG;
  final double fatGoal;
  final double size;

  const ActivityRings({
    super.key,
    required this.caloriesProgress,
    required this.proteinProgress,
    required this.carbsProgress,
    required this.fatProgress,
    required this.caloriesConsumed,
    required this.caloriesGoal,
    required this.proteinG,
    required this.proteinGoal,
    required this.carbsG,
    required this.carbsGoal,
    required this.fatG,
    required this.fatGoal,
    this.size = 200,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Rings
        SizedBox(
          width: size,
          height: size,
          child: CustomPaint(
            painter: _ActivityRingsPainter(
              caloriesProgress: caloriesProgress.clamp(0.0, 1.0),
              proteinProgress: proteinProgress.clamp(0.0, 1.0),
              carbsProgress: carbsProgress.clamp(0.0, 1.0),
              fatProgress: fatProgress.clamp(0.0, 1.0),
            ),
            child: Center(
              child: Padding(
                padding: const EdgeInsets.all(20.0), // Add padding to prevent overlap with rings
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    FittedBox(
                      fit: BoxFit.scaleDown,
                      child: Text(
                        '$caloriesConsumed',
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Theme.of(context).colorScheme.primary,
                              fontSize: 28, // Slightly smaller to fit better
                            ),
                        maxLines: 1,
                      ),
                    ),
                    const SizedBox(height: 2),
                    FittedBox(
                      fit: BoxFit.scaleDown,
                      child: Text(
                        'of $caloriesGoal cal',
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                              color: Theme.of(context).colorScheme.onSurfaceVariant,
                              fontSize: 10,
                            ),
                        maxLines: 1,
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
        
        const SizedBox(height: 24),
        
        // Legend
        Wrap(
          spacing: 16,
          runSpacing: 12,
          alignment: WrapAlignment.center,
          children: [
            _LegendItem(
              color: Colors.red,
              label: 'Calories',
              value: '$caloriesConsumed / $caloriesGoal',
              progress: caloriesProgress,
            ),
            _LegendItem(
              color: Colors.blue,
              label: 'Protein',
              value: '${proteinG.toStringAsFixed(0)}g / ${proteinGoal.toStringAsFixed(0)}g',
              progress: proteinProgress,
            ),
            _LegendItem(
              color: Colors.amber,
              label: 'Carbs',
              value: '${carbsG.toStringAsFixed(0)}g / ${carbsGoal.toStringAsFixed(0)}g',
              progress: carbsProgress,
            ),
            _LegendItem(
              color: Colors.purple,
              label: 'Fat',
              value: '${fatG.toStringAsFixed(0)}g / ${fatGoal.toStringAsFixed(0)}g',
              progress: fatProgress,
            ),
          ],
        ),
      ],
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;
  final String value;
  final double progress;

  const _LegendItem({
    required this.color,
    required this.label,
    required this.value,
    required this.progress,
  });

  @override
  Widget build(BuildContext context) {
    final percentage = (progress * 100).clamp(0, 999).toInt();
    
    return Row(
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
        const SizedBox(width: 8),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            Text(
              '$percentage% • $value',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
          ],
        ),
      ],
    );
  }
}

class _ActivityRingsPainter extends CustomPainter {
  final double caloriesProgress;
  final double proteinProgress;
  final double carbsProgress;
  final double fatProgress;

  _ActivityRingsPainter({
    required this.caloriesProgress,
    required this.proteinProgress,
    required this.carbsProgress,
    required this.fatProgress,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final baseRadius = size.width / 2;
    
    // Ring configuration (from outer to inner)
    final rings = [
      _RingConfig(
        progress: caloriesProgress,
        color: Colors.red,
        strokeWidth: 16,
        radius: baseRadius - 10,
      ),
      _RingConfig(
        progress: proteinProgress,
        color: Colors.blue,
        strokeWidth: 14,
        radius: baseRadius - 36,
      ),
      _RingConfig(
        progress: carbsProgress,
        color: Colors.amber,
        strokeWidth: 12,
        radius: baseRadius - 60,
      ),
      _RingConfig(
        progress: fatProgress,
        color: Colors.purple,
        strokeWidth: 10,
        radius: baseRadius - 80,
      ),
    ];

    // Draw each ring
    for (final ring in rings) {
      _drawRing(canvas, center, ring);
    }
  }

  void _drawRing(Canvas canvas, Offset center, _RingConfig config) {
    // Background ring (gray)
    final bgPaint = Paint()
      ..color = Colors.grey.withOpacity(0.2)
      ..strokeWidth = config.strokeWidth
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, config.radius, bgPaint);

    // Progress ring (colored)
    if (config.progress > 0) {
      final progressPaint = Paint()
        ..color = config.color
        ..strokeWidth = config.strokeWidth
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round;

      final startAngle = -math.pi / 2; // Start at top
      final sweepAngle = 2 * math.pi * config.progress;

      canvas.drawArc(
        Rect.fromCircle(center: center, radius: config.radius),
        startAngle,
        sweepAngle,
        false,
        progressPaint,
      );

      // Add glow effect for completed rings
      if (config.progress >= 1.0) {
        final glowPaint = Paint()
          ..color = config.color.withOpacity(0.3)
          ..strokeWidth = config.strokeWidth + 4
          ..style = PaintingStyle.stroke
          ..strokeCap = StrokeCap.round
          ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 3);

        canvas.drawArc(
          Rect.fromCircle(center: center, radius: config.radius),
          startAngle,
          sweepAngle,
          false,
          glowPaint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(_ActivityRingsPainter oldDelegate) {
    return oldDelegate.caloriesProgress != caloriesProgress ||
        oldDelegate.proteinProgress != proteinProgress ||
        oldDelegate.carbsProgress != carbsProgress ||
        oldDelegate.fatProgress != fatProgress;
  }
}

class _RingConfig {
  final double progress;
  final Color color;
  final double strokeWidth;
  final double radius;

  _RingConfig({
    required this.progress,
    required this.color,
    required this.strokeWidth,
    required this.radius,
  });
}

