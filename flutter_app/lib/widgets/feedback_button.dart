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
  List<XFile> _screenshots = [];  // Changed to list for multiple images
  bool _isSubmitting = false;
  String _feedbackType = 'bug';
  static const int _maxImages = 5;  // Maximum 5 images

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  Future<void> _addImage() async {
    // Check if we've reached the limit
    if (_screenshots.length >= _maxImages) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Maximum $_maxImages images allowed')),
        );
      }
      return;
    }

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
          _screenshots.add(image);
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to add image: $e')),
        );
      }
    }
  }

  void _removeImage(int index) {
    setState(() {
      _screenshots.removeAt(index);
    });
  }

  Future<void> _submitFeedback() async {
    // Comment is required, screenshot is optional
    if (_commentController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please add a comment (required)')),
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
        'has_screenshot': _screenshots.isNotEmpty,
        'screenshot_count': _screenshots.length,
      };

      // If screenshots exist, calculate total size
      if (_screenshots.isNotEmpty) {
        int totalSize = 0;
        for (var screenshot in _screenshots) {
          final bytes = await screenshot.readAsBytes();
          totalSize += bytes.length;
        }
        feedbackData['screenshot_size'] = totalSize;
        // Note: For production, upload to Cloud Storage instead of base64
      }

      // Submit feedback
      await api.post('/feedback/submit', feedbackData);

      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              '✅ Feedback received! Thank you for helping us improve. '
              'We review all feedback within 24 hours.',
            ),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 4),
            behavior: SnackBarBehavior.floating,
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
              const SizedBox(height: 8),
              // Helper text for feedback types
              Text(
                '🐛 Bug: Something broken | 💡 Suggestion: Improvement idea | ❓ Question: Need help | 👍 Praise: Love it!',
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.grey[600],
                  height: 1.3,
                ),
              ),
              const SizedBox(height: 24),

              // Comment (Required)
              const Text(
                'Comment *',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _commentController,
                style: const TextStyle(
                  color: Colors.black,  // Fix: Make text black instead of grey
                  fontSize: 16,
                ),
                maxLines: null,  // Unlimited lines - collect as much info as possible
                minLines: 4,
                keyboardType: TextInputType.multiline,
                maxLength: null,  // No character limit for test version
                decoration: InputDecoration(
                  hintText: 'Describe the issue or suggestion in detail... (required)\n\nPlease be as specific as possible - include steps to reproduce, expected vs actual behavior, etc.',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  filled: true,
                  fillColor: Colors.grey[100],
                  counterText: '',  // Hide character counter
                ),
              ),
              const SizedBox(height: 24),

              // Screenshots (Multiple)
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Screenshots (Optional)',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    '${_screenshots.length}/$_maxImages',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              
              // Display existing screenshots
              if (_screenshots.isNotEmpty)
                SizedBox(
                  height: 120,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: _screenshots.length,
                    itemBuilder: (context, index) {
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: Stack(
                          children: [
                            ClipRRect(
                              borderRadius: BorderRadius.circular(12),
                              child: Image.file(
                                File(_screenshots[index].path),
                                height: 120,
                                width: 120,
                                fit: BoxFit.cover,
                              ),
                            ),
                            Positioned(
                              top: 4,
                              right: 4,
                              child: Container(
                                decoration: BoxDecoration(
                                  color: Colors.red.shade600,  // Red background for better visibility
                                  shape: BoxShape.circle,
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.black.withOpacity(0.3),
                                      blurRadius: 4,
                                      offset: const Offset(0, 2),
                                    ),
                                  ],
                                ),
                                child: IconButton(
                                  icon: const Icon(Icons.close, size: 18),
                                  style: IconButton.styleFrom(
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.all(4),
                                    minimumSize: const Size(28, 28),
                                  ),
                                  onPressed: () => _removeImage(index),
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              
              if (_screenshots.isNotEmpty) const SizedBox(height: 8),
              
              // Add image button
              OutlinedButton.icon(
                onPressed: _screenshots.length < _maxImages ? _addImage : null,
                icon: const Icon(Icons.add_photo_alternate),
                label: Text(
                  _screenshots.isEmpty 
                    ? 'Add Screenshots (up to $_maxImages)' 
                    : 'Add More (${_maxImages - _screenshots.length} remaining)'
                ),
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

