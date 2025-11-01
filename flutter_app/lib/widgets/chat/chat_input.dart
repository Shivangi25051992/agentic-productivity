import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

class ChatInput extends StatefulWidget {
  final void Function(String) onSend;
  const ChatInput({super.key, required this.onSend});

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final _ctrl = TextEditingController();
  final _focus = FocusNode();
  late final stt.SpeechToText _speech;
  bool _listening = false;

  @override
  void initState() {
    super.initState();
    _speech = stt.SpeechToText();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    _focus.dispose();
    super.dispose();
  }

  void _submit(){
    final text = _ctrl.text.trim();
    if (text.isEmpty) return;
    _ctrl.clear();
    widget.onSend(text);
  }

  Future<void> _toggleVoice() async {
    if (_listening) {
      _speech.stop();
      setState(() => _listening = false);
      return;
    }
    final status = await Permission.microphone.request();
    if (!status.isGranted) return;
    final available = await _speech.initialize(onStatus: (_) {}, onError: (_) {});
    if (!available) return;
    setState(() => _listening = true);
    await _speech.listen(onResult: (res) {
      setState(() { _ctrl.text = res.recognizedWords; });
    });
  }

  @override
  Widget build(BuildContext context) {
    final canSend = _ctrl.text.trim().isNotEmpty;
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
        child: Row(
          children: [
            IconButton(
              onPressed: _toggleVoice,
              icon: Icon(_listening ? Icons.mic : Icons.mic_none),
              tooltip: 'Voice input',
            ),
            Expanded(
              child: TextField(
                controller: _ctrl,
                focusNode: _focus,
                minLines: 1,
                maxLines: 4,
                textInputAction: TextInputAction.send,
                onChanged: (_) => setState(() {}),
                onSubmitted: (_) => _submit(),
                decoration: const InputDecoration(hintText: 'Type a message...'),
              ),
            ),
            const SizedBox(width: 8),
            InkWell(
              onTap: canSend ? _submit : null,
              customBorder: const CircleBorder(),
              child: Ink(
                decoration: const ShapeDecoration(shape: CircleBorder(), color: Colors.teal),
                child: const Padding(padding: EdgeInsets.all(12), child: Icon(Icons.send, color: Colors.white)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}


