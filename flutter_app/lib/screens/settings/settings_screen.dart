import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/notification_provider.dart';
import '../../services/notification_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool darkMode = false;

  @override
  Widget build(BuildContext context) {
    final notif = context.watch<NotificationProvider>();
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        children: [
          SwitchListTile(
            value: darkMode,
            onChanged: (v) => setState(() => darkMode = v),
            title: const Text('Dark mode'),
          ),
          const Divider(),
          SwitchListTile(
            value: notif.enabled,
            onChanged: (v) => context.read<NotificationProvider>().toggle(v),
            title: const Text('Enable notifications'),
          ),
          ListTile(
            title: const Text('Do Not Disturb'),
            subtitle: Text('${notif.dndStart?.format(context) ?? '--'} to ${notif.dndEnd?.format(context) ?? '--'}'),
            onTap: () async {
              final start = await showTimePicker(context: context, initialTime: TimeOfDay.now());
              if (!mounted || start == null) return;
              final end = await showTimePicker(context: context, initialTime: TimeOfDay.now());
              if (!mounted || end == null) return;
              context.read<NotificationProvider>().setDnd(start: start, end: end);
            },
          ),
          ListTile(
            title: const Text('Send test notification'),
            onTap: () => NotificationService.instance.showInAppNotification('Test', 'This is a test notification'),
          ),
          ListTile(
            title: const Text('Schedule reminder (10s)'),
            onTap: () => NotificationService.instance.scheduleReminder(
              when: DateTime.now().add(const Duration(seconds: 10)),
              title: 'Reminder',
              body: 'Time to check your tasks!',
            ),
          ),
        ],
      ),
    );
  }
}


