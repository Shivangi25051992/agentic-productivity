import 'package:flutter/material.dart';

import '../models/message.dart';
import '../services/api_service.dart';

class ChatProvider extends ChangeNotifier {
  final List<ChatMessage> _messages = [];
  List<ChatMessage> get messages => List.unmodifiable(_messages);

  bool isLoading = false;
  String? errorMessage;

  Future<Map<String, dynamic>?> sendMessage({
    required String text,
    required String type,
    required ApiService api,
    String? clientGeneratedId, // 🔑 Pass to backend
  }) async {
    if (isLoading) return null;
    isLoading = true;
    errorMessage = null;
    _messages.add(ChatMessage(id: UniqueKey().toString(), text: text, isUser: true, timestamp: DateTime.now()));
    notifyListeners();
    try {
      final result = await api.sendChatMessage(text, type, clientGeneratedId: clientGeneratedId);
      final replyText = (result['message'] as String?) ?? 'Okay.';
      _messages.add(ChatMessage(
        id: UniqueKey().toString(),
        text: replyText,
        isUser: false,
        timestamp: DateTime.now(),
        metadata: result,
        // ✨ NEW: Parse expandable fields from API response
        summary: result['summary'] as String?,
        suggestion: result['suggestion'] as String?,
        details: (result['details'] as Map?)?.cast<String, dynamic>(),
        expandable: (result['expandable'] as bool?) ?? false,
      ));
      return result;
    } catch (e) {
      errorMessage = e.toString();
      return null;
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}


