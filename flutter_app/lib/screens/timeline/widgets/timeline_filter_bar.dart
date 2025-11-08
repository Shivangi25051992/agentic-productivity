import 'package:flutter/material.dart';

class TimelineFilterBar extends StatelessWidget {
  final Set<String> selectedTypes;
  final Function(String) onToggle;
  final Map<String, int> activityCounts;

  const TimelineFilterBar({
    Key? key,
    required this.selectedTypes,
    required this.onToggle,
    this.activityCounts = const {},
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 60,
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        children: [
          _buildFilterChip(
            context,
            type: 'meal',
            label: 'Meals',
            icon: Icons.restaurant,
            color: Colors.green,
          ),
          const SizedBox(width: 8),
          _buildFilterChip(
            context,
            type: 'workout',
            label: 'Workouts',
            icon: Icons.fitness_center,
            color: Colors.blue,
          ),
          const SizedBox(width: 8),
          _buildFilterChip(
            context,
            type: 'task',
            label: 'Tasks',
            icon: Icons.check_circle,
            color: Colors.orange,
          ),
          const SizedBox(width: 8),
          _buildFilterChip(
            context,
            type: 'event',
            label: 'Events',
            icon: Icons.event,
            color: Colors.purple,
          ),
          const SizedBox(width: 8),
          _buildFilterChip(
            context,
            type: 'water',
            label: 'Water',
            icon: Icons.water_drop,
            color: Colors.cyan,
          ),
          const SizedBox(width: 8),
          _buildFilterChip(
            context,
            type: 'supplement',
            label: 'Supplements',
            icon: Icons.medication,
            color: Colors.pink,
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(
    BuildContext context, {
    required String type,
    required String label,
    required IconData icon,
    required Color color,
  }) {
    final isSelected = selectedTypes.contains(type);
    final count = activityCounts[type] ?? 0;
    
    // Professional color scheme - single teal color
    final primaryColor = const Color(0xFF00897B); // Teal
    final chipColor = isSelected ? primaryColor : Colors.grey[200]!;
    final textColor = isSelected ? Colors.white : Colors.grey[700]!;
    final iconColor = isSelected ? Colors.white : Colors.grey[600]!;

    return FilterChip(
      selected: isSelected,
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 18,
            color: iconColor,
          ),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(color: textColor),
          ),
          if (count > 0) ...[
            const SizedBox(width: 6),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: isSelected ? Colors.white24 : Colors.grey[400],
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                '$count',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: isSelected ? Colors.white : Colors.grey[700],
                ),
              ),
            ),
          ],
        ],
      ),
      selectedColor: chipColor,
      checkmarkColor: Colors.white,
      backgroundColor: chipColor,
      onSelected: (_) => onToggle(type),
      showCheckmark: false,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      elevation: isSelected ? 2 : 0,
    );
  }
}

