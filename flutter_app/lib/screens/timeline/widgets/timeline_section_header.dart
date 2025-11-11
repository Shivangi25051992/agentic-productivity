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
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: EdgeInsets.only(
          top: isFirst ? 8 : 24,
          bottom: 8,
          left: 16,
          right: 16,
        ),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.03),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: Colors.white.withOpacity(0.1),
            width: 1,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Icon(
                  _getIconForSection(title),
                  size: 20,
                  color: Colors.white70,
                ),
                const SizedBox(width: 12),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: Colors.blue.withOpacity(0.3),
                      width: 1,
                    ),
                  ),
                  child: Text(
                    '$count',
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Icon(
                  isExpanded ? Icons.expand_less : Icons.expand_more,
                  color: Colors.white60,
                  size: 20,
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

