import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../models/timeline_activity.dart';

class TimelineItem extends StatelessWidget {
  final TimelineActivity activity;
  final bool isExpanded;
  final VoidCallback onTap;
  final bool isFirst;
  final bool isLast;

  const TimelineItem({
    Key? key,
    required this.activity,
    required this.isExpanded,
    required this.onTap,
    this.isFirst = false,
    this.isLast = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Timeline connector + icon
          _buildTimelineConnector(),
          const SizedBox(width: 12),
          // Glassmorphism Card
          Expanded(
            child: GestureDetector(
              onTap: onTap,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.05),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: _getColor().withOpacity(0.3),
                        width: 1,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: _getColor().withOpacity(0.1),
                          blurRadius: 12,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                activity.title,
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white,
                                ),
                              ),
                            ),
                            Row(
                              children: [
                                Text(
                                  DateFormat('h:mm a').format(activity.timestamp.toLocal()),
                                  style: TextStyle(
                                    fontSize: 13,
                                    color: Colors.white.withOpacity(0.6),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Icon(
                                  isExpanded ? Icons.expand_less : Icons.expand_more,
                                  color: Colors.white.withOpacity(0.6),
                                  size: 20,
                                ),
                              ],
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        // Summary
                        if (!isExpanded && activity.summary.isNotEmpty)
                          Text(
                            activity.summary,
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.white.withOpacity(0.7),
                            ),
                          ),
                        // Expanded details
                        if (isExpanded) _buildExpandedDetails(),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTimelineConnector() {
    return SizedBox(
      width: 40,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Top line
          if (!isFirst)
            Container(
              width: 3,
              height: 24,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.blue.withOpacity(0.3),
                    Colors.blue.withOpacity(0.6),
                  ],
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.blue.withOpacity(0.3),
                    blurRadius: 4,
                  ),
                ],
              ),
            ),
          // Icon
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: _getColor(),
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: _getColor().withOpacity(0.5),
                  blurRadius: 8,
                  spreadRadius: 2,
                ),
              ],
            ),
            child: Icon(
              _getIcon(),
              size: 20,
              color: Colors.white,
            ),
          ),
          // Bottom line
          if (!isLast)
            Container(
              width: 3,
              height: 24,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.blue.withOpacity(0.6),
                    Colors.blue.withOpacity(0.3),
                  ],
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.blue.withOpacity(0.3),
                    blurRadius: 4,
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildExpandedDetails() {
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Type-specific details
          if (activity.type == 'meal') _buildMealDetails(),
          if (activity.type == 'workout') _buildWorkoutDetails(),
          if (activity.type == 'task') _buildTaskDetails(),
          if (activity.type == 'water') _buildWaterDetails(),
          if (activity.type == 'supplement') _buildSupplementDetails(),
        ],
      ),
    );
  }

  Widget _buildMealDetails() {
    final details = activity.details;
    // ✅ DEFENSIVE: Fallback to food_name if items is missing (handles both fast-path and LLM-path)
    final items = details['items'] as List<dynamic>? ?? 
                  (details['food_name'] != null ? [details['food_name']] : []);
    final calories = details['calories'] ?? 0;
    final protein = details['protein_g'] ?? 0;
    final carbs = details['carbs_g'] ?? 0;
    final fat = details['fat_g'] ?? 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (items.isNotEmpty) ...[
          const Text(
            'Items:',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 13,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 4),
          ...items.map((item) => Padding(
                padding: const EdgeInsets.only(left: 8, bottom: 2),
                child: Text(
                  '• $item',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.white.withOpacity(0.8),
                  ),
                ),
              )),
          const SizedBox(height: 8),
        ],
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            _buildDetailChip('$calories cal', Icons.local_fire_department, Colors.orange),
            _buildDetailChip('${protein.toStringAsFixed(1)}g protein', Icons.fitness_center, Colors.blue),
            _buildDetailChip('${carbs.toStringAsFixed(1)}g carbs', Icons.grain, Colors.brown),
            _buildDetailChip('${fat.toStringAsFixed(1)}g fat', Icons.water_drop, Colors.yellow[700]!),
          ],
        ),
      ],
    );
  }

  Widget _buildWorkoutDetails() {
    final details = activity.details;
    final duration = details['duration_minutes'] ?? 0;
    final calories = details['calories'] ?? 0;
    final intensity = details['intensity'] ?? 'moderate';
    final activityType = details['activity_type'] ?? 'workout';

    return Wrap(
      spacing: 8,
      runSpacing: 4,
      children: [
        _buildDetailChip('$duration min', Icons.timer, Colors.blue),
        _buildDetailChip('$calories cal burned', Icons.local_fire_department, Colors.orange),
        _buildDetailChip(intensity, Icons.speed, Colors.purple),
        _buildDetailChip(activityType, Icons.fitness_center, Colors.green),
      ],
    );
  }

  Widget _buildTaskDetails() {
    final details = activity.details;
    final description = details['description'] ?? '';
    final priority = activity.priority ?? 'medium';
    final status = activity.status;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (description.isNotEmpty) ...[
          Text(
            description,
            style: TextStyle(
              fontSize: 13,
              color: Colors.white.withOpacity(0.8),
            ),
          ),
          const SizedBox(height: 8),
        ],
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            _buildDetailChip(priority, Icons.flag, _getPriorityColor(priority)),
            _buildDetailChip(status, Icons.info, _getStatusColor(status)),
            if (activity.dueDate != null)
              _buildDetailChip(
                'Due: ${DateFormat('MMM d, h:mm a').format(activity.dueDate!.toLocal())}',
                Icons.schedule,
                Colors.grey[700]!,
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildWaterDetails() {
    final details = activity.details;
    final amount = details['quantity_ml'] ?? details['amount'] ?? 0;
    final unit = details['water_unit'] ?? 'ml';

    return Wrap(
      spacing: 8,
      runSpacing: 4,
      children: [
        _buildDetailChip('${amount}ml', Icons.water_drop, Colors.cyan),
        if (unit != 'ml') _buildDetailChip(unit, Icons.local_drink, Colors.blue),
      ],
    );
  }

  Widget _buildSupplementDetails() {
    final details = activity.details;
    final name = details['supplement_name'] ?? details['name'] ?? details['item'] ?? '';
    final dosage = details['dosage'] ?? '';
    final supplementType = details['supplement_type'] ?? '';

    return Wrap(
      spacing: 8,
      runSpacing: 4,
      children: [
        if (name.isNotEmpty) _buildDetailChip(name, Icons.medication, Colors.pink),
        if (dosage.isNotEmpty) _buildDetailChip(dosage, Icons.info, Colors.purple),
        if (supplementType.isNotEmpty && supplementType != name)
          _buildDetailChip(supplementType, Icons.category, Colors.deepPurple),
      ],
    );
  }

  Widget _buildDetailChip(String label, IconData icon, Color color) {
    return RepaintBoundary(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: color.withOpacity(0.2),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.4)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 14, color: color),
            const SizedBox(width: 6),
            Text(
              label,
              style: const TextStyle(
                fontSize: 12,
                color: Colors.white,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  IconData _getIcon() {
    switch (activity.type) {
      case 'meal':
        return Icons.restaurant;
      case 'workout':
        return Icons.fitness_center;
      case 'task':
        return Icons.check_circle;
      case 'event':
        return Icons.event;
      case 'water':
        return Icons.water_drop;
      case 'supplement':
        return Icons.medication;
      default:
        return Icons.circle;
    }
  }

  Color _getColor() {
    switch (activity.type) {
      case 'meal':
        return Colors.green;
      case 'workout':
        return Colors.blue;
      case 'task':
        return Colors.orange;
      case 'event':
        return Colors.purple;
      case 'water':
        return Colors.cyan;
      case 'supplement':
        return Colors.pink;
      default:
        return Colors.grey;
    }
  }

  Color _getPriorityColor(String priority) {
    switch (priority.toLowerCase()) {
      case 'high':
        return Colors.red;
      case 'medium':
        return Colors.orange;
      case 'low':
        return Colors.grey;
      default:
        return Colors.grey;
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return Colors.green;
      case 'in_progress':
        return Colors.blue;
      case 'pending':
        return Colors.orange;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}

