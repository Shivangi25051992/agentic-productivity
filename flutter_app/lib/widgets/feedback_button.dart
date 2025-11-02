import 'package:flutter/material.dart';
import 'dart:typed_data';
import 'dart:ui' as ui;
import 'dart:io';
import 'package:flutter/rendering.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import '../providers/auth_provider.dart';
import 'package:provider/provider.dart';

/// Floating feedback button that appears on all screens
class FeedbackButton extends StatelessWidget {
  const FeedbackButton({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Positioned(
      right: 16,
      bottom: 80,
      child: FloatingActionButton(
        heroTag: 'feedback',
        backgroundColor: Colors.orange,
        child: const Icon(Icons.feedback, color: Colors.white),
        onPressed: () => _showFeedbackDialog(context),
      ),
    );
  }

  void _showFeedbackDialog(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => const FeedbackDialog(),
    );
  }
}

/// Feedback dialog with screenshot and comment
class FeedbackDialog extends StatefulWidget {
  const FeedbackDialog({Key? key}) : super(key: key);

  @override
  State<FeedbackDialog> createState() => _FeedbackDialogState();
}

class _FeedbackDialogState extends State<FeedbackDialog> {
  final _commentController = TextEditingController();
  final _picker = ImagePicker();
  XFile? _screenshot;
  bool _isSubmitting = false;
  String _feedbackType = 'bug';

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  Future<void> _takeScreenshot() async {
    try {
      // Use image picker to select from gallery or take photo
      final XFile? image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );
      
      if (image != null) {
        setState(() {
          _screenshot = image;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to capture screenshot: $e')),
        );
      }
    }
  }

  Future<void> _submitFeedback() async {
    if (_commentController.text.trim().isEmpty && _screenshot == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please add a comment or screenshot')),
      );
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      final auth = context.read<AuthProvider>();
      final api = ApiService(auth, onUnauthorized: () {
        Navigator.of(context).pushReplacementNamed('/login');
      });

      // Prepare feedback data
      final feedbackData = {
        'type': _feedbackType,
        'comment': _commentController.text.trim(),
        'screen': ModalRoute.of(context)?.settings.name ?? 'unknown',
        'timestamp': DateTime.now().toIso8601String(),
        'has_screenshot': _screenshot != null,
      };

      // If screenshot exists, convert to base64
      if (_screenshot != null) {
        final bytes = await _screenshot!.readAsBytes();
        feedbackData['screenshot_size'] = bytes.length;
        // Note: For production, upload to Cloud Storage instead of base64
      }

      // Submit feedback
      await api.post('/feedback/submit', feedbackData);

      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Feedback submitted! Thank you!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to submit feedback: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
      ),
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  const Icon(Icons.feedback, color: Colors.orange, size: 28),
                  const SizedBox(width: 12),
                  const Text(
                    'Send Feedback',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Feedback Type
              const Text(
                'Type',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: [
                  ChoiceChip(
                    label: const Text('🐛 Bug'),
                    selected: _feedbackType == 'bug',
                    onSelected: (selected) {
                      if (selected) setState(() => _feedbackType = 'bug');
                    },
                  ),
                  ChoiceChip(
                    label: const Text('💡 Suggestion'),
                    selected: _feedbackType == 'suggestion',
                    onSelected: (selected) {
                      if (selected) setState(() => _feedbackType = 'suggestion');
                    },
                  ),
                  ChoiceChip(
                    label: const Text('❓ Question'),
                    selected: _feedbackType == 'question',
                    onSelected: (selected) {
                      if (selected) setState(() => _feedbackType = 'question');
                    },
                  ),
                  ChoiceChip(
                    label: const Text('👍 Praise'),
                    selected: _feedbackType == 'praise',
                    onSelected: (selected) {
                      if (selected) setState(() => _feedbackType = 'praise');
                    },
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Comment
              const Text(
                'Comment',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _commentController,
                maxLines: 4,
                decoration: InputDecoration(
                  hintText: 'Describe the issue or suggestion...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  filled: true,
                  fillColor: Colors.grey[100],
                ),
              ),
              const SizedBox(height: 24),

              // Screenshot
              const Text(
                'Screenshot (Optional)',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              
              if (_screenshot != null)
                Stack(
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Image.file(
                        File(_screenshot!.path),
                        height: 200,
                        width: double.infinity,
                        fit: BoxFit.cover,
                      ),
                    ),
                    Positioned(
                      top: 8,
                      right: 8,
                      child: IconButton(
                        icon: const Icon(Icons.close, color: Colors.white),
                        style: IconButton.styleFrom(
                          backgroundColor: Colors.black54,
                        ),
                        onPressed: () {
                          setState(() {
                            _screenshot = null;
                          });
                        },
                      ),
                    ),
                  ],
                )
              else
                OutlinedButton.icon(
                  onPressed: _takeScreenshot,
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Add Screenshot'),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size(double.infinity, 50),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              
              const SizedBox(height: 24),

              // Submit Button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _isSubmitting ? null : _submitFeedback,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _isSubmitting
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Text(
                          'Submit Feedback',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

