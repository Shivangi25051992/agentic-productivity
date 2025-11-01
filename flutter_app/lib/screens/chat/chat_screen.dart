import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:timeago/timeago.dart' as timeago;

import '../../providers/chat_provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/fitness_provider.dart';
import '../../providers/task_provider.dart';
import '../../models/fitness_log.dart';
import '../../models/task.dart';
import '../../services/api_service.dart';
import '../../widgets/chat/chat_input.dart';
import '../../widgets/chat/message_bubble.dart';
import '../../widgets/chat/summary_card.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ScrollController _scroll = ScrollController();
  final List<_ChatItem> _items = <_ChatItem>[];
  bool _isTyping = false;

  @override
  void dispose() {
    _scroll.dispose();
    super.dispose();
  }

  Future<void> _handleSend(String text) async {
    if (text.trim().isEmpty) return;
    
    // Add user message to chat immediately
    setState(() {
      _items.add(_ChatItem.userMessage(text, DateTime.now()));
      _isTyping = true;
    });
    _autoScroll();
    
    final chat = context.read<ChatProvider>();
    final api = ApiService(context.read<AuthProvider>(), onUnauthorized: () => Navigator.of(context).pushReplacementNamed('/login'));
    final result = await chat.sendMessage(text: text, type: 'auto', api: api);
    setState(() { _isTyping = false; });
    if (result == null) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to send. Retry?')));
      return;
    }

    // New schema: { items: [ { category, summary, data }, ... ], message: "AI feedback" }
    final items = (result['items'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    final aiMessage = result['message']?.toString() ?? '';
    
    // Add AI message if present (clarification, confirmation, etc.)
    if (aiMessage.isNotEmpty) {
      setState(() {
        _items.add(_ChatItem.aiMessage(aiMessage, DateTime.now()));
      });
    }
    
    for (final it in items) {
      final category = (it['category'] ?? '').toString();
      final data = (it['data'] ?? const {}).cast<String, dynamic>();
      if (category == 'meal') {
        final mealTitle = data['meal']?.toString() ?? (data['items']?.toString() ?? 'Meal');
        final kcal = int.tryParse('${data['calories'] ?? ''}') ?? 0;
        _items.add(_ChatItem.summaryFitness(
          meal: mealTitle,
          calories: kcal,
          macros: '',
          time: DateTime.now(),
          detailedMacros: data, // Pass the entire data object with all macros
        ));
        // Update provider so dashboard reflects changes
        context.read<FitnessProvider>().add(FitnessLogModel(
          id: UniqueKey().toString(),
          userId: context.read<AuthProvider>().currentUser?.uid ?? 'me',
          type: FitnessLogType.meal,
          content: mealTitle,
          calories: kcal,
          parsedData: data,
          timestamp: DateTime.now(),
        ));
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Meal logged!')));
        }
      } else if (category == 'workout') {
        final title = it['summary']?.toString() ?? 'Workout';
        _items.add(_ChatItem.summaryFitness(
          meal: title,
          calories: int.tryParse('${data['calories'] ?? ''}') ?? 0,
          macros: '',
          time: DateTime.now(),
          detailedMacros: data,
        ));
        context.read<FitnessProvider>().add(FitnessLogModel(
          id: UniqueKey().toString(),
          userId: context.read<AuthProvider>().currentUser?.uid ?? 'me',
          type: FitnessLogType.workout,
          content: title,
          calories: int.tryParse('${data['calories'] ?? ''}') ?? 0,
          parsedData: data,
          timestamp: DateTime.now(),
        ));
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Workout recorded')));
        }
      } else if (category == 'task' || category == 'reminder') {
        final title = data['title']?.toString() ?? it['summary']?.toString() ?? 'Task';
        _items.add(_ChatItem.summaryTask(
          title: title,
          due: DateTime.now().add(const Duration(hours: 2)),
          priority: 'medium',
          status: 'pending',
        ));
        context.read<TaskProvider>().add(TaskModel(
          id: UniqueKey().toString(),
          userId: context.read<AuthProvider>().currentUser?.uid ?? 'me',
          title: title,
          description: '',
          dueDate: null,
          priority: TaskPriority.medium,
          status: TaskStatus.pending,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        ));
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('${category[0].toUpperCase()}${category.substring(1)} added')));
        }
      } else {
        _items.add(_ChatItem.message(role: 'assistant', text: it['summary']?.toString() ?? 'Noted'));
      }
    }
    
    // Add AI conversational feedback message
    if (aiMessage.isNotEmpty) {
      _items.add(_ChatItem.message(role: 'assistant', text: aiMessage));
    }
    
    _autoScroll();
  }

  DateTime? _parseDate(Object? v) {
    if (v is String) { try { return DateTime.parse(v); } catch (_) {} }
    return null;
  }

  Future<void> _refresh() async {
    await Future<void>.delayed(const Duration(milliseconds: 600));
    if (!mounted) return;
    setState(() {});
  }

  void _autoScroll() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scroll.hasClients) return;
      _scroll.animateTo(
        _scroll.position.maxScrollExtent,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOut,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Assistant'),
        automaticallyImplyLeading: false,
        actions: [
          // Logout button
          Consumer<AuthProvider>(
            builder: (context, auth, _) => PopupMenuButton<String>(
              icon: const Icon(Icons.account_circle),
              tooltip: 'Account',
              onSelected: (value) async {
                if (value == 'logout') {
                  final shouldLogout = await showDialog<bool>(
                    context: context,
                    builder: (context) => AlertDialog(
                      title: const Text('Logout'),
                      content: const Text('Are you sure you want to logout?'),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.of(context).pop(false),
                          child: const Text('Cancel'),
                        ),
                        FilledButton(
                          onPressed: () => Navigator.of(context).pop(true),
                          child: const Text('Logout'),
                        ),
                      ],
                    ),
                  );
                  
                  if (shouldLogout == true && context.mounted) {
                    await auth.signOut();
                    if (context.mounted) {
                      Navigator.of(context).pushNamedAndRemoveUntil(
                        '/login',
                        (route) => false,
                      );
                    }
                  }
                }
              },
              itemBuilder: (context) => [
                PopupMenuItem<String>(
                  enabled: false,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        auth.currentUser?.displayName ?? auth.currentUser?.email ?? 'User',
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (auth.currentUser?.email != null)
                        Text(
                          auth.currentUser!.email!,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Theme.of(context).colorScheme.onSurfaceVariant,
                          ),
                        ),
                    ],
                  ),
                ),
                const PopupMenuDivider(),
                const PopupMenuItem<String>(
                  value: 'logout',
                  child: Row(
                    children: [
                      Icon(Icons.logout, size: 20),
                      SizedBox(width: 12),
                      Text('Logout'),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: RefreshIndicator(
              onRefresh: _refresh,
              child: ListView.builder(
                controller: _scroll,
                padding: const EdgeInsets.all(12),
                itemCount: _items.length + (_isTyping ? 1 : 0),
                itemBuilder: (context, i) {
                  if (_isTyping && i == _items.length) {
                    return const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: _TypingIndicator(),
                    );
                  }
                  final item = _items[i];
                  return item.when(
                    message: (role, text, createdAt) => MessageBubble(
                      text: text,
                      isMe: role == 'user',
                      timestamp: timeago.format(createdAt, allowFromNow: true),
                      onDelete: () {
                        setState(() => _items.removeAt(i));
                      },
                    ),
                    task: (title, due, priority, status) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 6.0),
                      child: SummaryCard.task(
                        title: title,
                        dueDate: due,
                        priority: priority,
                        status: status,
                        onEdit: () {},
                        onDelete: () => setState(() => _items.removeAt(i)),
                        onMarkDone: () {},
                      ),
                    ),
                    fitness: (meal, calories, macros, time, detailedMacros) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 6.0),
                      child: SummaryCard.fitness(
                        meal: meal,
                        calories: calories,
                        macros: macros,
                        time: time,
                        detailedMacros: detailedMacros,
                        onEdit: () {},
                        onDelete: () => setState(() => _items.removeAt(i)),
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
          ChatInput(onSend: _handleSend),
        ],
      ),
      // Removed FAB buttons as they block chat input and are not needed
      // Users can type naturally instead
    );
  }
}

class _TypingIndicator extends StatelessWidget {
  const _TypingIndicator();
  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const CircleAvatar(child: Icon(Icons.auto_awesome)),
        const SizedBox(width: 8),
        Expanded(
          child: Container(
            height: 22,
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surfaceVariant,
              borderRadius: BorderRadius.circular(12),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 10),
            alignment: Alignment.centerLeft,
            child: const _Dots(),
          ),
        ),
      ],
    );
  }
}

class _Dots extends StatefulWidget {
  const _Dots();
  @override
  State<_Dots> createState() => _DotsState();
}

class _DotsState extends State<_Dots> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 900))..repeat();
  @override
  void dispose() { _c.dispose(); super.dispose(); }
  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _c,
      builder: (_, __) {
        final v = (t) => (1 + (t * 3).floor() % 3);
        final dots = '.' * v(_c.value).toInt();
        return Text('Typing$dots', style: Theme.of(context).textTheme.labelMedium);
      },
    );
  }
}

class _QuickActions extends StatelessWidget {
  final VoidCallback onAddMeal; final VoidCallback onAddWorkout; final VoidCallback onAddTask;
  const _QuickActions({required this.onAddMeal, required this.onAddWorkout, required this.onAddTask});
  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        FloatingActionButton.extended(
          heroTag: 'qa_meal',
          onPressed: onAddMeal,
          icon: const Icon(Icons.restaurant),
          label: const Text('Add Meal'),
        ),
        const SizedBox(height: 8),
        FloatingActionButton.extended(
          heroTag: 'qa_workout',
          onPressed: onAddWorkout,
          icon: const Icon(Icons.fitness_center),
          label: const Text('Add Workout'),
        ),
        const SizedBox(height: 8),
        FloatingActionButton.extended(
          heroTag: 'qa_task',
          onPressed: onAddTask,
          icon: const Icon(Icons.add_task),
          label: const Text('Add Task'),
        ),
      ],
    );
  }
}

class _ChatItem {
  final String type; // 'message' | 'task' | 'fitness'
  final String? role; // for message
  final String? text; // for message
  final DateTime createdAt;
  // task
  final String? title; final DateTime? due; final String? priority; final String? status;
  // fitness
  final String? meal; final int? calories; final String? macros; final DateTime? time;
  final Map<String, dynamic>? detailedMacros;

  _ChatItem._({required this.type, this.role, this.text, required this.createdAt, this.title, this.due, this.priority, this.status, this.meal, this.calories, this.macros, this.time, this.detailedMacros});

  factory _ChatItem.message({required String role, required String text}) => _ChatItem._(type: 'message', role: role, text: text, createdAt: DateTime.now());
  factory _ChatItem.userMessage(String text, DateTime time) => _ChatItem._(type: 'message', role: 'user', text: text, createdAt: time);
  factory _ChatItem.aiMessage(String text, DateTime time) => _ChatItem._(type: 'message', role: 'assistant', text: text, createdAt: time);
  factory _ChatItem.summaryTask({required String title, required DateTime due, required String priority, required String status}) => _ChatItem._(type: 'task', createdAt: DateTime.now(), title: title, due: due, priority: priority, status: status);
  factory _ChatItem.summaryFitness({required String meal, required int calories, required String macros, required DateTime time, Map<String, dynamic>? detailedMacros}) => _ChatItem._(type: 'fitness', createdAt: DateTime.now(), meal: meal, calories: calories, macros: macros, time: time, detailedMacros: detailedMacros);

  Widget when({
    required Widget Function(String role, String text, DateTime createdAt) message,
    required Widget Function(String title, DateTime due, String priority, String status) task,
    required Widget Function(String meal, int calories, String macros, DateTime time, Map<String, dynamic>? detailedMacros) fitness,
  }) {
    switch (type) {
      case 'message':
        return message(role!, text!, createdAt);
      case 'task':
        return task(title!, due!, priority!, status!);
      default:
        return fitness(meal!, calories!, macros!, time!, detailedMacros);
    }
  }
}


