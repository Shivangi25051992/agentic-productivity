import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../providers/dashboard_provider.dart';

class ActivityTimeline extends StatelessWidget {
  final List<ActivityItem> activities;

  const ActivityTimeline({
    super.key,
    required this.activities,
  });

  @override
  Widget build(BuildContext context) {
    if (activities.isEmpty) {
      return _buildEmptyState(context);
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: activities.length,
      itemBuilder: (context, index) {
        final activity = activities[index];
        final isLast = index == activities.length - 1;
        return _TimelineItem(
          activity: activity,
          isLast: isLast,
        );
      },
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(32),
      child: Column(
        children: [
          Text(
            '📅',
            style: const TextStyle(fontSize: 48),
          ),
          const SizedBox(height: 16),
          Text(
            'No activity yet today',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Theme.of(context).textTheme.bodySmall?.color,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Start logging meals, workouts, or tasks!',
            style: Theme.of(context).textTheme.bodySmall,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _TimelineItem extends StatelessWidget {
  final ActivityItem activity;
  final bool isLast;

  const _TimelineItem({
    required this.activity,
    required this.isLast,
  });

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Timeline indicator
          Column(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: _getColor(activity.type).withOpacity(0.1),
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: _getColor(activity.type),
                    width: 2,
                  ),
                ),
                child: Center(
                  child: Text(
                    activity.emoji,
                    style: const TextStyle(fontSize: 20),
                  ),
                ),
              ),
              if (!isLast)
                Expanded(
                  child: Container(
                    width: 2,
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    decoration: BoxDecoration(
                      color: Theme.of(context).dividerColor.withOpacity(0.3),
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(width: 16),
          // Content
          Expanded(
            child: Container(
              margin: const EdgeInsets.only(bottom: 16),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: Theme.of(context).dividerColor.withOpacity(0.1),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          activity.title,
                          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                      ),
                      Text(
                        DateFormat('h:mm a').format(activity.timestamp),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Theme.of(context).textTheme.bodySmall?.color,
                            ),
                      ),
                    ],
                  ),
                  if (activity.subtitle != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      activity.subtitle!,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                  if (activity.data != null && activity.type == 'meal') ...[
                    const SizedBox(height: 8),
                    _buildMacroChips(context, activity.data!),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMacroChips(BuildContext context, Map<String, dynamic> data) {
    return Wrap(
      spacing: 8,
      runSpacing: 4,
      children: [
        if (data['protein_g'] != null)
          _buildChip(
            context,
            '💪 ${(data['protein_g'] as num).toStringAsFixed(0)}g',
            Colors.red,
          ),
        if (data['carbs_g'] != null)
          _buildChip(
            context,
            '🌾 ${(data['carbs_g'] as num).toStringAsFixed(0)}g',
            Colors.amber,
          ),
        if (data['fat_g'] != null)
          _buildChip(
            context,
            '🥑 ${(data['fat_g'] as num).toStringAsFixed(0)}g',
            Colors.green,
          ),
      ],
    );
  }

  Widget _buildChip(BuildContext context, String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w500,
            ),
      ),
    );
  }

  Color _getColor(String type) {
    switch (type) {
      case 'meal':
        return Colors.orange;
      case 'workout':
        return Colors.purple;
      case 'water':
        return Colors.blue;
      case 'task':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }
}




