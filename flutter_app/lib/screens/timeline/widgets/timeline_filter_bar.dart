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
    final selectedCount = selectedTypes.length;
    final totalCount = activityCounts.values.fold(0, (sum, count) => sum + count);
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0A0A),
        border: Border(
          bottom: BorderSide(
            color: Colors.white.withOpacity(0.1),
            width: 1,
          ),
        ),
      ),
      child: Row(
        children: [
          // Filter button with count
          GestureDetector(
            onTap: () => _showFilterModal(context),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Colors.blue.withOpacity(0.3),
                    Colors.purple.withOpacity(0.3),
                  ],
                ),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: Colors.blue.withOpacity(0.5),
                  width: 1,
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(
                    Icons.filter_list,
                    color: Colors.white,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    selectedCount == 6 ? 'All' : 'Filter ($selectedCount)',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 12),
          // Active filters (compact chips)
          Expanded(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  if (selectedTypes.contains('meal'))
                    _buildCompactChip('Meals', Icons.restaurant, Colors.green, activityCounts['meal'] ?? 0),
                  if (selectedTypes.contains('workout'))
                    _buildCompactChip('Workouts', Icons.fitness_center, Colors.blue, activityCounts['workout'] ?? 0),
                  if (selectedTypes.contains('task'))
                    _buildCompactChip('Tasks', Icons.check_circle, Colors.orange, activityCounts['task'] ?? 0),
                  if (selectedTypes.contains('event'))
                    _buildCompactChip('Events', Icons.event, Colors.purple, activityCounts['event'] ?? 0),
                  if (selectedTypes.contains('water'))
                    _buildCompactChip('Water', Icons.water_drop, Colors.cyan, activityCounts['water'] ?? 0),
                  if (selectedTypes.contains('supplement'))
                    _buildCompactChip('Supps', Icons.medication, Colors.pink, activityCounts['supplement'] ?? 0),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCompactChip(String label, IconData icon, Color color, int count) {
    return Container(
      margin: const EdgeInsets.only(right: 8),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: color.withOpacity(0.4),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 4),
          Text(
            '$count',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  void _showFilterModal(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        decoration: BoxDecoration(
          color: const Color(0xFF1A1A1A),
          borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
          border: Border.all(
            color: Colors.blue.withOpacity(0.3),
            width: 1,
          ),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Filter Activities',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                GestureDetector(
                  onTap: () => Navigator.pop(context),
                  child: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.1),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.close,
                      color: Colors.white70,
                      size: 20,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                _buildFilterChip(context, type: 'meal', label: 'Meals', icon: Icons.restaurant, color: Colors.green),
                _buildFilterChip(context, type: 'workout', label: 'Workouts', icon: Icons.fitness_center, color: Colors.blue),
                _buildFilterChip(context, type: 'task', label: 'Tasks', icon: Icons.check_circle, color: Colors.orange),
                _buildFilterChip(context, type: 'event', label: 'Events', icon: Icons.event, color: Colors.purple),
                _buildFilterChip(context, type: 'water', label: 'Water', icon: Icons.water_drop, color: Colors.cyan),
                _buildFilterChip(context, type: 'supplement', label: 'Supplements', icon: Icons.medication, color: Colors.pink),
              ],
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: GestureDetector(
                    onTap: () {
                      // Select all
                      for (var type in ['meal', 'workout', 'task', 'event', 'water', 'supplement']) {
                        if (!selectedTypes.contains(type)) {
                          onToggle(type);
                        }
                      }
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: Colors.white.withOpacity(0.2),
                          width: 1,
                        ),
                      ),
                      child: const Center(
                        child: Text(
                          'Select All',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: GestureDetector(
                    onTap: () {
                      // Clear all
                      for (var type in List.from(selectedTypes)) {
                        onToggle(type);
                      }
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      decoration: BoxDecoration(
                        color: Colors.red.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: Colors.red.withOpacity(0.4),
                          width: 1,
                        ),
                      ),
                      child: const Center(
                        child: Text(
                          'Clear All',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
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

    return GestureDetector(
      onTap: () => onToggle(type),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? color.withOpacity(0.2) : Colors.white.withOpacity(0.05),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? color.withOpacity(0.5) : Colors.white.withOpacity(0.2),
            width: 1,
          ),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: color.withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ]
              : null,
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 18,
              color: isSelected ? color : Colors.white60,
            ),
            const SizedBox(width: 8),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? Colors.white : Colors.white70,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                fontSize: 14,
              ),
            ),
            if (count > 0) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: isSelected ? color : Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '$count',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: isSelected ? Colors.white : Colors.white70,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

