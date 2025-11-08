import 'package:flutter/material.dart';

/// 🧠 Phase 2: Explanation Sheet Widget
/// 
/// Bottom sheet showing detailed AI reasoning, data sources, assumptions
class ExplanationSheet extends StatelessWidget {
  final Map<String, dynamic> explanation;
  final Map<String, dynamic>? confidenceFactors;
  final double? confidenceScore;

  const ExplanationSheet({
    Key? key,
    required this.explanation,
    this.confidenceFactors,
    this.confidenceScore,
  }) : super(key: key);

  static void show(
    BuildContext context, {
    required Map<String, dynamic> explanation,
    Map<String, dynamic>? confidenceFactors,
    double? confidenceScore,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => ExplanationSheet(
        explanation: explanation,
        confidenceFactors: confidenceFactors,
        confidenceScore: confidenceScore,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.8,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Handle bar
          Container(
            margin: const EdgeInsets.symmetric(vertical: 12),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          // Header
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 0, 20, 16),
            child: Row(
              children: [
                const Icon(Icons.psychology, size: 24, color: Color(0xFF3B82F6)),
                const SizedBox(width: 8),
                const Text(
                  'How AI Understood This',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),

          const Divider(height: 1),

          // Content
          Flexible(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Reasoning
                  if (explanation['reasoning'] != null) ...[
                    _buildSection(
                      title: 'Step-by-Step Reasoning',
                      icon: Icons.format_list_numbered,
                      child: Text(
                        explanation['reasoning'] as String,
                        style: const TextStyle(
                          fontSize: 14,
                          height: 1.6,
                          color: Color(0xFF374151),
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],

                  // Data Sources
                  if (explanation['data_sources'] != null) ...[
                    _buildSection(
                      title: 'Data Sources',
                      icon: Icons.source,
                      child: _buildBulletList(
                        List<String>.from(explanation['data_sources']),
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],

                  // Assumptions
                  if (explanation['assumptions'] != null) ...[
                    _buildSection(
                      title: 'Assumptions Made',
                      icon: Icons.lightbulb_outline,
                      child: _buildBulletList(
                        List<String>.from(explanation['assumptions']),
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],

                  // Why This Classification
                  if (explanation['why_this_classification'] != null) ...[
                    _buildSection(
                      title: 'Why This Classification',
                      icon: Icons.label,
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF3F4F6),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          explanation['why_this_classification'] as String,
                          style: const TextStyle(
                            fontSize: 14,
                            height: 1.5,
                            color: Color(0xFF374151),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],

                  // Confidence Factors
                  if (confidenceFactors != null && confidenceFactors!.isNotEmpty) ...[
                    _buildSection(
                      title: 'Confidence Factors',
                      icon: Icons.analytics,
                      child: Column(
                        children: confidenceFactors!.entries
                            .where((e) => e.value != null)
                            .map((entry) => _buildConfidenceBar(
                                  label: _formatFactorName(entry.key),
                                  value: (entry.value as num).toDouble(),
                                ))
                            .toList(),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),

          // Close button
          Padding(
            padding: const EdgeInsets.all(20),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => Navigator.pop(context),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF3B82F6),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'Got it',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSection({
    required String title,
    required IconData icon,
    required Widget child,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 18, color: const Color(0xFF6B7280)),
            const SizedBox(width: 8),
            Text(
              title,
              style: const TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: Color(0xFF1F2937),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        child,
      ],
    );
  }

  Widget _buildBulletList(List<String> items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: items.map((item) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 6),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '• ',
                style: TextStyle(
                  fontSize: 14,
                  color: Color(0xFF6B7280),
                ),
              ),
              Expanded(
                child: Text(
                  item,
                  style: const TextStyle(
                    fontSize: 14,
                    height: 1.5,
                    color: Color(0xFF374151),
                  ),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildConfidenceBar({
    required String label,
    required double value,
  }) {
    final percentage = (value * 100).round();
    final color = value >= 0.8
        ? const Color(0xFF10B981)
        : value >= 0.6
            ? const Color(0xFFF59E0B)
            : const Color(0xFFEF4444);

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 13,
                  color: Color(0xFF6B7280),
                ),
              ),
              Text(
                '$percentage%',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: value,
              minHeight: 6,
              backgroundColor: const Color(0xFFE5E7EB),
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
          ),
        ],
      ),
    );
  }

  String _formatFactorName(String key) {
    // Convert snake_case to Title Case
    return key
        .replaceAll('_', ' ')
        .split(' ')
        .map((word) => word[0].toUpperCase() + word.substring(1))
        .join(' ');
  }
}

