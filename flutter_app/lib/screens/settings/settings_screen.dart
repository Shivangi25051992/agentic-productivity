import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/notification_provider.dart';
import '../../providers/auth_provider.dart';
import '../../services/notification_service.dart';
import '../../services/api_service.dart';

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
          const Divider(),
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              'Data Management',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.red,
              ),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.delete_forever, color: Colors.red),
            title: const Text(
              'Wipe All My Logs',
              style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
            ),
            subtitle: const Text(
              'Delete all fitness logs, chat history, and tasks. Profile and goals will be preserved.',
              style: TextStyle(fontSize: 12),
            ),
            onTap: () => _showWipeConfirmation(context),
          ),
        ],
      ),
    );
  }
  
  Future<void> _showWipeConfirmation(BuildContext context) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.warning, color: Colors.red),
            SizedBox(width: 8),
            Text('Wipe All Logs?'),
          ],
        ),
        content: const Text(
          'This will permanently delete:\n\n'
          '• All fitness logs (meals, workouts)\n'
          '• All chat history\n'
          '• All tasks\n\n'
          'Your profile and goals will be preserved.\n\n'
          'This action cannot be undone!',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Wipe All Logs'),
          ),
        ],
      ),
    );
    
    if (confirmed == true && mounted) {
      await _wipeAllLogs(context);
    }
  }
  
  Future<void> _wipeAllLogs(BuildContext context) async {
    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: Card(
          child: Padding(
            padding: EdgeInsets.all(24.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 16),
                Text('Wiping all logs...'),
              ],
            ),
          ),
        ),
      ),
    );
    
    try {
      final auth = context.read<AuthProvider>();
      final api = ApiService(auth, onUnauthorized: () {
        Navigator.of(context).pushReplacementNamed('/login');
      });
      
      // Call wipe endpoint
      final response = await api.delete('/user/wipe-logs');
      
      // Close loading dialog
      if (mounted) Navigator.of(context).pop();
      
      // Show result
      if (mounted) {
        final success = response['success'] ?? false;
        final deleted = response['deleted'] ?? {};
        final total = deleted['total'] ?? 0;
        
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: Row(
              children: [
                Icon(
                  success ? Icons.check_circle : Icons.error,
                  color: success ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 8),
                Text(success ? 'Success!' : 'Error'),
              ],
            ),
            content: Text(
              success
                  ? 'Successfully deleted $total items:\n\n'
                    '• ${deleted['fitness_logs'] ?? 0} fitness logs\n'
                    '• ${deleted['chat_messages'] ?? 0} chat messages\n'
                    '• ${deleted['tasks'] ?? 0} tasks\n\n'
                    'Your profile and goals are preserved.'
                  : 'Failed to wipe logs. Please try again.',
            ),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  // Refresh the app
                  if (success) {
                    Navigator.of(context).pushReplacementNamed('/home');
                  }
                },
                child: const Text('OK'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      // Close loading dialog
      if (mounted) Navigator.of(context).pop();
      
      // Show error
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Row(
              children: [
                Icon(Icons.error, color: Colors.red),
                SizedBox(width: 8),
                Text('Error'),
              ],
            ),
            content: Text('Failed to wipe logs: $e'),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('OK'),
              ),
            ],
          ),
        );
      }
    }
  }
}


