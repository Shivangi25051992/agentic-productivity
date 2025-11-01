import 'package:flutter/material.dart';

class MessageBubble extends StatelessWidget {
  final String text;
  final bool isMe;
  final String? timestamp;
  final VoidCallback? onDelete;
  const MessageBubble({super.key, required this.text, required this.isMe, this.timestamp, this.onDelete});

  @override
  Widget build(BuildContext context) {
    final bg = isMe ? Theme.of(context).colorScheme.primary : Theme.of(context).colorScheme.surface;
    final fg = isMe ? Colors.white : Theme.of(context).colorScheme.onSurface;
    final align = isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start;
    final radius = BorderRadius.only(
      topLeft: const Radius.circular(12),
      topRight: const Radius.circular(12),
      bottomLeft: Radius.circular(isMe ? 12 : 0),
      bottomRight: Radius.circular(isMe ? 0 : 12),
    );

    final avatar = CircleAvatar(child: Icon(isMe ? Icons.person : Icons.auto_awesome, color: isMe ? Colors.white : null));

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: isMe ? MainAxisAlignment.end : MainAxisAlignment.start,
      children: [
        if (!isMe) avatar,
        if (!isMe) const SizedBox(width: 8),
        Flexible(
          child: GestureDetector(
            onLongPress: onDelete,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              margin: const EdgeInsets.symmetric(vertical: 4),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(color: bg, borderRadius: radius, boxShadow: const [BoxShadow(blurRadius: 12, color: Colors.black12)]),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(text, style: TextStyle(color: fg)),
                  if (timestamp != null) ...[
                    const SizedBox(height: 4),
                    Text(timestamp!, style: TextStyle(color: fg.withOpacity(.8), fontSize: 11)),
                  ],
                ],
              ),
            ),
          ),
        ),
        if (isMe) const SizedBox(width: 8),
        if (isMe) avatar,
      ],
    );
  }
}


