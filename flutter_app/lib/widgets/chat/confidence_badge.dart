import 'package:flutter/material.dart';

/// 🧠 Phase 2: Confidence Badge Widget
/// 
/// Displays AI confidence score as a visual badge with color-coded levels
/// Tap to show detailed confidence breakdown
class ConfidenceBadge extends StatelessWidget {
  final double score; // 0.0 - 1.0
  final String level; // "very_high", "high", "medium", "low", "very_low"
  final VoidCallback? onTap;

  const ConfidenceBadge({
    Key? key,
    required this.score,
    required this.level,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = _getColors();
    final icon = _getIcon();
    final percentage = (score * 100).round();

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: colors['background'],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: colors['border']!,
            width: 1,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 14,
              color: colors['text'],
            ),
            const SizedBox(width: 4),
            Text(
              '$percentage%',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: colors['text'],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Map<String, Color> _getColors() {
    // High confidence: Green
    if (score >= 0.9) {
      return {
        'background': const Color(0xFFD1FAE5),
        'border': const Color(0xFF10B981),
        'text': const Color(0xFF047857),
      };
    }
    // Medium-high confidence: Light green
    else if (score >= 0.8) {
      return {
        'background': const Color(0xFFF0FDF4),
        'border': const Color(0xFF22C55E),
        'text': const Color(0xFF15803D),
      };
    }
    // Medium confidence: Yellow
    else if (score >= 0.7) {
      return {
        'background': const Color(0xFFFEF3C7),
        'border': const Color(0xFFF59E0B),
        'text': const Color(0xFFB45309),
      };
    }
    // Low confidence: Orange
    else if (score >= 0.5) {
      return {
        'background': const Color(0xFFFFEDD5),
        'border': const Color(0xFFF97316),
        'text': const Color(0xFFC2410C),
      };
    }
    // Very low confidence: Red
    else {
      return {
        'background': const Color(0xFFFEE2E2),
        'border': const Color(0xFFEF4444),
        'text': const Color(0xFFDC2626),
      };
    }
  }

  IconData _getIcon() {
    if (score >= 0.9) {
      return Icons.check_circle;
    } else if (score >= 0.8) {
      return Icons.check_circle_outline;
    } else if (score >= 0.7) {
      return Icons.info;
    } else if (score >= 0.5) {
      return Icons.warning_amber_rounded;
    } else {
      return Icons.help_outline;
    }
  }
}

