import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

/// Expandable meal card that shows summary and can expand to show details
/// Used on home page for quick meal overview and actions
class ExpandableMealCard extends StatefulWidget {
  final String mealType;
  final List<dynamic> activities;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;
  final Function(String)? onMove;

  const ExpandableMealCard({
    Key? key,
    required this.mealType,
    required this.activities,
    this.onEdit,
    this.onDelete,
    this.onMove,
  }) : super(key: key);

  @override
  State<ExpandableMealCard> createState() => _ExpandableMealCardState();
}

class _ExpandableMealCardState extends State<ExpandableMealCard>
    with SingleTickerProviderStateMixin {
  bool _isExpanded = false;
  late AnimationController _animationController;
  late Animation<double> _expandAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _expandAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _toggleExpand() {
    setState(() {
      _isExpanded = !_isExpanded;
      if (_isExpanded) {
        _animationController.forward();
      } else {
        _animationController.reverse();
      }
    });
  }

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
    // Convert to local time if it's in UTC
    final localTime = dateTime.isUtc ? dateTime.toLocal() : dateTime;
    return DateFormat('h:mm a').format(localTime);
  }

  @override
  Widget build(BuildContext context) {
    // Calculate totals
    int totalCalories = 0;
    double totalProtein = 0;
    double totalCarbs = 0;
    double totalFat = 0;

    for (final activity in widget.activities) {
      final data = activity.data ?? {};
      totalCalories += (data['calories'] as num?)?.toInt() ?? 0;
      totalProtein += (data['protein_g'] as num?)?.toDouble() ?? 0;
      totalCarbs += (data['carbs_g'] as num?)?.toDouble() ?? 0;
      totalFat += (data['fat_g'] as num?)?.toDouble() ?? 0;
    }

    final hasItems = widget.activities.isNotEmpty;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          // Header (always visible)
          InkWell(
            onTap: hasItems ? _toggleExpand : null,
            borderRadius: BorderRadius.circular(16),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  // Meal icon
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: Theme.of(context).primaryColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Center(
                      child: Text(
                        _getMealIcon(widget.mealType),
                        style: const TextStyle(fontSize: 24),
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  
                  // Meal info
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(
                              _getMealLabel(widget.mealType),
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            if (hasItems) ...[
                              const SizedBox(width: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 2,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.blue.shade100,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Text(
                                  '${widget.activities.length} item${widget.activities.length > 1 ? 's' : ''}',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.blue.shade700,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          ],
                        ),
                        const SizedBox(height: 4),
                        if (hasItems)
                          Text(
                            '$totalCalories kcal • ${totalProtein.toStringAsFixed(0)}g protein',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey.shade600,
                            ),
                          )
                        else
                          Text(
                            'No items logged',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey.shade400,
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                      ],
                    ),
                  ),
                  
                  // Expand icon
                  if (hasItems)
                    RotationTransition(
                      turns: Tween(begin: 0.0, end: 0.5).animate(_expandAnimation),
                      child: Icon(
                        Icons.expand_more,
                        color: Colors.grey.shade600,
                      ),
                    ),
                ],
              ),
            ),
          ),

          // Expanded content
          if (hasItems)
            SizeTransition(
              sizeFactor: _expandAnimation,
              child: Column(
                children: [
                  const Divider(height: 1),
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Food items list
                        ...widget.activities.asMap().entries.map((entry) {
                          final index = entry.key;
                          final activity = entry.value;
                          final data = activity.data ?? {};
                          final description = data['description'] as String? ?? 'Unknown food';
                          final calories = (data['calories'] as num?)?.toInt() ?? 0;
                          final protein = (data['protein_g'] as num?)?.toDouble() ?? 0;
                          final carbs = (data['carbs_g'] as num?)?.toDouble() ?? 0;
                          final fat = (data['fat_g'] as num?)?.toDouble() ?? 0;
                          final timestamp = activity.timestamp;

                          return Container(
                            margin: EdgeInsets.only(
                              bottom: index < widget.activities.length - 1 ? 12 : 0,
                            ),
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.grey.shade50,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                color: Colors.grey.shade200,
                              ),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                // Food name and time
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        description,
                                        style: const TextStyle(
                                          fontSize: 15,
                                          fontWeight: FontWeight.w600,
                                        ),
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
                                const SizedBox(height: 8),
                                
                                // Macros chips
                                Wrap(
                                  spacing: 8,
                                  runSpacing: 4,
                                  children: [
                                    _buildMacroChip('🔥 $calories kcal', Colors.orange),
                                    _buildMacroChip('💪 ${protein.toStringAsFixed(1)}g', Colors.red),
                                    _buildMacroChip('🌾 ${carbs.toStringAsFixed(1)}g', Colors.blue),
                                    _buildMacroChip('🥑 ${fat.toStringAsFixed(1)}g', Colors.purple),
                                  ],
                                ),
                              ],
                            ),
                          );
                        }).toList(),

                        const SizedBox(height: 16),

                        // Action buttons
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            _buildActionButton(
                              context,
                              icon: Icons.edit_outlined,
                              label: 'Edit',
                              onTap: widget.onEdit,
                            ),
                            _buildActionButton(
                              context,
                              icon: Icons.swap_horiz,
                              label: 'Move',
                              onTap: () => _showMoveDialog(context),
                            ),
                            _buildActionButton(
                              context,
                              icon: Icons.delete_outline,
                              label: 'Delete',
                              color: Colors.red,
                              onTap: () => _showDeleteDialog(context),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
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

  Widget _buildActionButton(
    BuildContext context, {
    required IconData icon,
    required String label,
    Color? color,
    VoidCallback? onTap,
  }) {
    final buttonColor = color ?? Theme.of(context).primaryColor;
    
    return InkWell(
      onTap: onTap ?? () {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$label coming soon!')),
        );
      },
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Column(
          children: [
            Icon(icon, color: buttonColor, size: 24),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: buttonColor,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showMoveDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Move to Different Meal'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildMealTypeOption(context, 'breakfast', '🌅 Breakfast'),
            _buildMealTypeOption(context, 'lunch', '🌞 Lunch'),
            _buildMealTypeOption(context, 'snack', '🍎 Snack'),
            _buildMealTypeOption(context, 'dinner', '🌙 Dinner'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );
  }

  Widget _buildMealTypeOption(BuildContext context, String type, String label) {
    final isCurrentType = type == widget.mealType;
    
    return ListTile(
      leading: Text(label.split(' ')[0], style: const TextStyle(fontSize: 24)),
      title: Text(label.split(' ')[1]),
      enabled: !isCurrentType,
      trailing: isCurrentType ? const Icon(Icons.check, color: Colors.green) : null,
      onTap: isCurrentType
          ? null
          : () {
              Navigator.of(context).pop();
              if (widget.onMove != null) {
                widget.onMove!(type);
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Moved to $label')),
                );
              }
            },
    );
  }

  void _showDeleteDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Meal?'),
        content: Text(
          'Are you sure you want to delete this ${_getMealLabel(widget.mealType).toLowerCase()}?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              if (widget.onDelete != null) {
                widget.onDelete!();
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Delete coming soon!')),
                );
              }
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}
