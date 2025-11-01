import 'package:flutter/material.dart';

class FitnessDashboardScreen extends StatelessWidget {
  const FitnessDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Fitness Dashboard')),
      body: GridView.count(
        padding: const EdgeInsets.all(16),
        crossAxisCount: MediaQuery.of(context).size.width > 700 ? 3 : 2,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        children: const [
          _KpiCard(title: 'Calories Today', value: '1,850'),
          _KpiCard(title: 'Workouts This Week', value: '3'),
          _KpiCard(title: 'Avg Response Time', value: '120ms'),
        ],
      ),
    );
  }
}

class _KpiCard extends StatelessWidget {
  final String title; final String value;
  const _KpiCard({required this.title, required this.value});
  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium),
            const Spacer(),
            Text(value, style: Theme.of(context).textTheme.headlineMedium),
          ],
        ),
      ),
    );
  }
}






