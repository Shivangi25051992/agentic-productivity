import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:provider/provider.dart';

import '../../providers/task_provider.dart';
import '../../providers/fitness_provider.dart';
import '../chat/chat_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  late final TabController _tabs = TabController(length: 3, vsync: this);
  @override
  void dispose() { _tabs.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    final tasks = context.watch<TaskProvider>().tasks;
    final logs = context.watch<FitnessProvider>().logs;
    final completed = tasks.where((t) => t.status.name == 'completed').length;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        bottom: TabBar(controller: _tabs, tabs: const [Tab(text: 'Tasks'), Tab(text: 'Fitness'), Tab(text: 'Analytics')]),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ChatScreen())),
        child: const Icon(Icons.chat_bubble_outline),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: Row(
              children: [
                _Stat(label: 'Completed', value: '$completed'),
                const SizedBox(width: 8),
                _Stat(label: 'Calories', value: logs.fold<int>(0, (a, b) => a + (b.calories ?? 0)).toString()),
                const SizedBox(width: 8),
                _Stat(label: 'Logs', value: '${logs.length}'),
              ],
            ),
          ),
          Expanded(
            child: TabBarView(
              controller: _tabs,
              children: [
                _TasksTab(),
                _FitnessTab(),
                _AnalyticsTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  final String label; final String value; const _Stat({required this.label, required this.value});
  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        decoration: BoxDecoration(color: Theme.of(context).colorScheme.surface, borderRadius: BorderRadius.circular(12), boxShadow: const [BoxShadow(blurRadius: 12, color: Colors.black12)]),
        padding: const EdgeInsets.all(12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: Theme.of(context).textTheme.labelLarge),
          const SizedBox(height: 4),
          Text(value, style: Theme.of(context).textTheme.headlineSmall),
        ]),
      ),
    );
  }
}

class _TasksTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final taskProv = context.watch<TaskProvider>();
    final tasks = taskProv.tasks;
    return RefreshIndicator(
      onRefresh: () async {},
      child: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: tasks.length,
        itemBuilder: (_, i) {
          final t = tasks[i];
          return Dismissible(
            key: ValueKey(t.id),
            background: Container(color: Colors.red, alignment: Alignment.centerLeft, padding: const EdgeInsets.only(left: 16), child: const Icon(Icons.delete, color: Colors.white)),
            secondaryBackground: Container(color: Colors.blue, alignment: Alignment.centerRight, padding: const EdgeInsets.only(right: 16), child: const Icon(Icons.edit, color: Colors.white)),
            onDismissed: (d) => taskProv.removeById(t.id),
            child: Card(
              elevation: 0,
              child: ListTile(
                leading: Checkbox(value: t.status.name == 'completed', onChanged: (_) => taskProv.toggleComplete(t.id)),
                title: Text(t.title),
                subtitle: Row(children: [
                  _Badge(label: t.priority.name),
                  const SizedBox(width: 6),
                  if (t.dueDate != null) _Badge(label: 'Due ${t.dueDate!.toLocal().toString().substring(0,10)}'),
                  const SizedBox(width: 6),
                  _Badge(label: t.status.name),
                ]),
              ),
            ),
          );
        },
      ),
    );
  }
}

class _Badge extends StatelessWidget {
  final String label; const _Badge({required this.label});
  @override
  Widget build(BuildContext context) {
    return Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4), decoration: BoxDecoration(color: Theme.of(context).colorScheme.surfaceVariant, borderRadius: BorderRadius.circular(999)), child: Text(label, style: Theme.of(context).textTheme.labelSmall));
  }
}

class _FitnessTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final fitnessProv = context.watch<FitnessProvider>();
    final logs = fitnessProv.logs;
    final total = logs.fold<int>(0, (a, b) => a + (b.calories ?? 0));
    const goal = 2000;
    final pct = (total / goal).clamp(0.0, 1.0);
    return RefreshIndicator(
      onRefresh: () async {},
      child: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          Card(
            elevation: 0,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('Calorie Goal'),
                const SizedBox(height: 8),
                LinearProgressIndicator(value: pct.toDouble(), minHeight: 12),
                const SizedBox(height: 8),
                Text('$total / $goal kcal'),
              ]),
            ),
          ),
          const SizedBox(height: 8),
          ...logs.map((l) => Card(
                elevation: 0,
                child: ListTile(
                  title: Text(l.type.name == 'meal' ? 'Meal' : 'Workout'),
                  subtitle: Text(l.content),
                  trailing: Text('${l.calories ?? 0} kcal'),
                ),
              )),
        ],
      ),
    );
  }
}

class _AnalyticsTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        SizedBox(
          height: 180,
          child: LineChart(LineChartData(lineBarsData: [
            LineChartBarData(isCurved: true, spots: const [FlSpot(0, 1), FlSpot(1, 3), FlSpot(2, 2), FlSpot(3, 5)], color: Colors.teal),
          ])),
        ),
        const SizedBox(height: 12),
        SizedBox(
          height: 180,
          child: BarChart(BarChartData(barGroups: [
            for (int i = 0; i < 7; i++) BarChartGroupData(x: i, barRods: [BarChartRodData(toY: (i + 1) * 1.0, color: Colors.orange)])
          ])),
        ),
      ],
    );
  }
}


