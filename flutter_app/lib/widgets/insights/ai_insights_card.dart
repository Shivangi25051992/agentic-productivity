import 'package:flutter/material.dart';

/// AI-Powered Insights Card
/// Displays intelligent, actionable insights for users
class AIInsightsCard extends StatelessWidget {
  final List<Map<String, dynamic>> insights;
  final String? summary;

  const AIInsightsCard({
    Key? key,
    required this.insights,
    this.summary,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (insights.isEmpty && (summary == null || summary!.isEmpty)) {
      return const SizedBox.shrink();
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Colors.purple.shade50,
              Colors.blue.shade50,
            ],
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.purple.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.lightbulb,
                    color: Colors.purple,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'AI Insights',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.purple.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.auto_awesome,
                        size: 14,
                        color: Colors.purple.shade700,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        'Smart',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: Colors.purple.shade700,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            
            // Summary (if available)
            if (summary != null && summary!.isNotEmpty) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.purple.shade200),
                ),
                child: Row(
                  children: [
                    const Text(
                      '💡',
                      style: TextStyle(fontSize: 20),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        summary!,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          height: 1.4,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            
            // Insights List
            if (insights.isNotEmpty) ...[
              const SizedBox(height: 16),
              ...insights.map((insight) => _buildInsightItem(context, insight)).toList(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInsightItem(BuildContext context, Map<String, dynamic> insight) {
    final type = insight['type'] as String? ?? 'suggestion';
    final priority = insight['priority'] as String? ?? 'medium';
    final title = insight['title'] as String? ?? '';
    final message = insight['message'] as String? ?? '';
    final icon = insight['icon'] as String? ?? '💡';
    final colorName = insight['color'] as String? ?? 'blue';
    final action = insight['action'] as String?;
    final actionLabel = insight['action_label'] as String?;

    // Map color names to actual colors
    final color = _getColor(colorName);
    
    // Map priority to visual weight
    final isHighPriority = priority == 'high';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isHighPriority ? color.withOpacity(0.5) : Colors.grey.shade200,
          width: isHighPriority ? 2 : 1,
        ),
        boxShadow: isHighPriority
            ? [
                BoxShadow(
                  color: color.withOpacity(0.1),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                )
              ]
            : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                icon,
                style: const TextStyle(fontSize: 24),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: color,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      message,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey.shade700,
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          // Action button (if available)
          if (action != null && actionLabel != null) ...[
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  // Handle action
                  _handleAction(context, action);
                },
                icon: Icon(Icons.arrow_forward, size: 16, color: color),
                label: Text(actionLabel),
                style: OutlinedButton.styleFrom(
                  foregroundColor: color,
                  side: BorderSide(color: color),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Color _getColor(String colorName) {
    switch (colorName.toLowerCase()) {
      case 'red':
        return Colors.red;
      case 'green':
        return Colors.green;
      case 'blue':
        return Colors.blue;
      case 'orange':
        return Colors.orange;
      case 'purple':
        return Colors.purple;
      default:
        return Colors.blue;
    }
  }

  void _handleAction(BuildContext context, String action) {
    switch (action) {
      case 'log_meal':
        Navigator.of(context).pushNamed('/chat');
        break;
      case 'log_workout':
        Navigator.of(context).pushNamed('/chat');
        break;
      case 'suggest_protein_foods':
        // Show protein foods dialog
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('High Protein Foods'),
            content: const SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('🍗 Chicken Breast (31g per 100g)'),
                  SizedBox(height: 8),
                  Text('🥚 Eggs (13g per 2 eggs)'),
                  SizedBox(height: 8),
                  Text('🥛 Greek Yogurt (10g per 100g)'),
                  SizedBox(height: 8),
                  Text('🐟 Salmon (25g per 100g)'),
                  SizedBox(height: 8),
                  Text('🥜 Almonds (21g per 100g)'),
                  SizedBox(height: 8),
                  Text('🧀 Paneer (18g per 100g)'),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Close'),
              ),
            ],
          ),
        );
        break;
      default:
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Action: $action')),
        );
    }
  }
}


