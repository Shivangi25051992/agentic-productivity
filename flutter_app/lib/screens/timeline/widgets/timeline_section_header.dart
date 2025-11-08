import 'package:flutter/material.dart';

class TimelineSectionHeader extends StatelessWidget {
  final String title;
  final int count;
  final bool isFirst;
  final bool isExpanded;
  final VoidCallback? onTap;

  const TimelineSectionHeader({
    Key? key,
    required this.title,
    required this.count,
    this.isFirst = false,
    this.isExpanded = true,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.only(
          top: isFirst ? 8 : 24,
          bottom: 8,
          left: 16,
          right: 16,
        ),
        color: Colors.grey[50],
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Icon(
                  _getIconForSection(title),
                  size: 20,
                  color: Colors.grey[700],
                ),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                  ),
                ),
              ],
            ),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '$count',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.grey[700],
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Icon(
                  isExpanded ? Icons.expand_less : Icons.expand_more,
                  color: Colors.grey[600],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  IconData _getIconForSection(String title) {
    if (title.contains('Upcoming') || title.contains('Overdue')) {
      return Icons.warning_amber_rounded;
    } else if (title.contains('Today')) {
      return Icons.today;
    } else if (title.contains('Yesterday')) {
      return Icons.history;
    } else {
      return Icons.calendar_today;
    }
  }
}

