import 'package:flutter/material.dart';

class SummaryCard extends StatelessWidget {
  final Widget child;
  const SummaryCard({super.key, required this.child});

  factory SummaryCard.task({
    required String title,
    required DateTime dueDate,
    required String priority,
    required String status,
    VoidCallback? onEdit,
    VoidCallback? onDelete,
    VoidCallback? onMarkDone,
  }) {
    return SummaryCard(
      child: _TaskSummary(
        title: title,
        dueDate: dueDate,
        priority: priority,
        status: status,
        onEdit: onEdit,
        onDelete: onDelete,
        onMarkDone: onMarkDone,
      ),
    );
  }

  factory SummaryCard.fitness({
    required String meal,
    required int calories,
    required String macros,
    required DateTime time,
    Map<String, dynamic>? detailedMacros,
    VoidCallback? onEdit,
    VoidCallback? onDelete,
  }) {
    return SummaryCard(
      child: _FitnessSummary(
        meal: meal,
        calories: calories,
        macros: macros,
        time: time,
        detailedMacros: detailedMacros,
        onEdit: onEdit,
        onDelete: onDelete,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(padding: const EdgeInsets.all(16.0), child: child),
    );
  }
}

class _TaskSummary extends StatelessWidget {
  final String title; final DateTime dueDate; final String priority; final String status;
  final VoidCallback? onEdit; final VoidCallback? onDelete; final VoidCallback? onMarkDone;
  const _TaskSummary({required this.title, required this.dueDate, required this.priority, required this.status, this.onEdit, this.onDelete, this.onMarkDone});

  @override
  Widget build(BuildContext context) {
    final color = Colors.blue;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(children: [
          Container(width: 8, height: 8, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
          const SizedBox(width: 8),
          Text('Task', style: Theme.of(context).textTheme.labelLarge),
        ]),
        const SizedBox(height: 8),
        Text(title, style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 6),
        Wrap(spacing: 8, runSpacing: 8, children: [
          _Chip(label: 'Due ${dueDate.toLocal().toString().substring(0,16)}'),
          _Chip(label: 'Priority $priority'),
          _Chip(label: status),
        ]),
        const SizedBox(height: 10),
        Row(children: [
          TextButton.icon(onPressed: onEdit, icon: const Icon(Icons.edit), label: const Text('Edit')),
          const SizedBox(width: 8),
          TextButton.icon(onPressed: onMarkDone, icon: const Icon(Icons.check_circle), label: const Text('Mark Done')),
          const Spacer(),
          IconButton(onPressed: onDelete, icon: const Icon(Icons.delete_outline)),
        ]),
      ],
    );
  }
}

class _FitnessSummary extends StatelessWidget {
  final String meal;
  final int calories;
  final String macros;
  final DateTime time;
  final Map<String, dynamic>? detailedMacros;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;
  
  const _FitnessSummary({
    required this.meal,
    required this.calories,
    required this.macros,
    required this.time,
    this.detailedMacros,
    this.onEdit,
    this.onDelete,
  });
  
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    
    // Extract detailed macros if available
    final protein = detailedMacros?['protein_g'] ?? 0;
    final carbs = detailedMacros?['carbs_g'] ?? 0;
    final fat = detailedMacros?['fat_g'] ?? 0;
    final fiber = detailedMacros?['fiber_g'];
    final sugar = detailedMacros?['sugar_g'];
    
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            colorScheme.primaryContainer.withOpacity(0.3),
            colorScheme.secondaryContainer.withOpacity(0.2),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: colorScheme.primary.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with emoji and category
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text('🍽️', style: TextStyle(fontSize: 20)),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Meal Logged',
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: colorScheme.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      meal,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              // Calories badge
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.orange.withOpacity(0.5)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.local_fire_department, size: 16, color: Colors.orange),
                    const SizedBox(width: 4),
                    Text(
                      '$calories',
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.orange.shade700,
                      ),
                    ),
                    Text(
                      ' kcal',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: Colors.orange.shade700,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Macro breakdown with visual bars
          if (protein > 0 || carbs > 0 || fat > 0) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: colorScheme.surface.withOpacity(0.8),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  _MacroBar(
                    label: 'Protein',
                    value: protein.toDouble(),
                    unit: 'g',
                    color: Colors.blue,
                    icon: Icons.fitness_center,
                  ),
                  const SizedBox(height: 8),
                  _MacroBar(
                    label: 'Carbs',
                    value: carbs.toDouble(),
                    unit: 'g',
                    color: Colors.amber,
                    icon: Icons.grain,
                  ),
                  const SizedBox(height: 8),
                  _MacroBar(
                    label: 'Fat',
                    value: fat.toDouble(),
                    unit: 'g',
                    color: Colors.purple,
                    icon: Icons.water_drop,
                  ),
                  if (fiber != null && fiber > 0) ...[
                    const SizedBox(height: 8),
                    _MacroBar(
                      label: 'Fiber',
                      value: fiber.toDouble(),
                      unit: 'g',
                      color: Colors.green,
                      icon: Icons.spa,
                      isSecondary: true,
                    ),
                  ],
                  if (sugar != null && sugar > 0) ...[
                    const SizedBox(height: 8),
                    _MacroBar(
                      label: 'Sugar',
                      value: sugar.toDouble(),
                      unit: 'g',
                      color: Colors.pink,
                      icon: Icons.cake,
                      isSecondary: true,
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 12),
          ],
          
          // Time and actions
          Row(
            children: [
              Icon(Icons.access_time, size: 14, color: colorScheme.onSurfaceVariant),
              const SizedBox(width: 4),
              Text(
                _formatTime(time),
                style: theme.textTheme.labelSmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
              const Spacer(),
              TextButton.icon(
                onPressed: onEdit,
                icon: const Icon(Icons.edit, size: 16),
                label: const Text('Edit'),
                style: TextButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                ),
              ),
              IconButton(
                onPressed: onDelete,
                icon: const Icon(Icons.delete_outline, size: 20),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  String _formatTime(DateTime dt) {
    final now = DateTime.now();
    final diff = now.difference(dt);
    
    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }
}

class _MacroBar extends StatelessWidget {
  final String label;
  final double value;
  final String unit;
  final Color color;
  final IconData icon;
  final bool isSecondary;
  
  const _MacroBar({
    required this.label,
    required this.value,
    required this.unit,
    required this.color,
    required this.icon,
    this.isSecondary = false,
  });
  
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Row(
      children: [
        Icon(icon, size: isSecondary ? 14 : 16, color: color),
        const SizedBox(width: 8),
        SizedBox(
          width: 50,
          child: Text(
            label,
            style: theme.textTheme.labelSmall?.copyWith(
              fontWeight: isSecondary ? FontWeight.normal : FontWeight.bold,
            ),
          ),
        ),
        Expanded(
          child: Container(
            height: isSecondary ? 4 : 6,
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(3),
            ),
            child: FractionallySizedBox(
              alignment: Alignment.centerLeft,
              widthFactor: (value / 100).clamp(0.0, 1.0),
              child: Container(
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(3),
                ),
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        SizedBox(
          width: 40,
          child: Text(
            '${value.toStringAsFixed(0)}$unit',
            style: theme.textTheme.labelSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: color,
            ),
            textAlign: TextAlign.right,
          ),
        ),
      ],
    );
  }
}

class _Chip extends StatelessWidget {
  final String label; const _Chip({required this.label});
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceVariant,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(label, style: Theme.of(context).textTheme.labelMedium),
    );
  }
}


