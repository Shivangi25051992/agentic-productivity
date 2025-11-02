import 'package:flutter/material.dart';

class AnalyticsCard extends StatelessWidget {
  final String label; final String value; final IconData icon; final Color? color;
  const AnalyticsCard({super.key, required this.label, required this.value, required this.icon, this.color});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            CircleAvatar(backgroundColor: (color ?? Theme.of(context).colorScheme.primary).withOpacity(.15), child: Icon(icon, color: color ?? Theme.of(context).colorScheme.primary)),
            const SizedBox(width: 12),
            Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(label, style: Theme.of(context).textTheme.labelLarge),
              const SizedBox(height: 4),
              Text(value, style: Theme.of(context).textTheme.headlineSmall),
            ])
          ],
        ),
      ),
    );
  }
}







