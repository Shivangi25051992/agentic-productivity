import 'package:flutter/material.dart';

/// 🧠 Phase 2: Feedback Buttons Widget
/// 🎨 UX FIX: Shows badge if feedback already given
/// 
/// Allows users to rate AI responses (helpful/not helpful)
/// Feeds into Phase 3 continuous learning
class FeedbackButtons extends StatefulWidget {
  final String messageId;
  final Function(String messageId, String rating, List<String> corrections, String? comment)? onFeedbackSubmit;
  
  // 🎨 UX FIX: Feedback state from backend
  final bool feedbackGiven;
  final String? feedbackRating;

  const FeedbackButtons({
    Key? key,
    required this.messageId,
    this.onFeedbackSubmit,
    // 🎨 UX FIX
    this.feedbackGiven = false,
    this.feedbackRating,
  }) : super(key: key);

  @override
  State<FeedbackButtons> createState() => _FeedbackButtonsState();
}

class _FeedbackButtonsState extends State<FeedbackButtons> {
  String? userFeedback; // 'positive' | 'negative' | null
  final TextEditingController _correctionController = TextEditingController();
  final Map<String, bool> _corrections = {
    'food': false,
    'quantity': false,
    'calories': false,
    'timing': false,
    'other': false,
  };
  
  @override
  void dispose() {
    _correctionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // 🎨 UX FIX: If feedback already given (from backend), show badge
    if (widget.feedbackGiven) {
      return _buildFeedbackBadge(widget.feedbackRating);
    }
    
    // If feedback was just given in this session, show confirmation
    if (userFeedback != null) {
      return _buildFeedbackGiven();
    }

    return Container(
      margin: const EdgeInsets.only(top: 8),
      child: Row(
        children: [
          Text(
            'Was this helpful?',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(width: 12),
          _buildFeedbackButton(
            icon: Icons.thumb_up_outlined,
            activeIcon: Icons.thumb_up,
            isActive: userFeedback == 'positive',
            onTap: _handlePositiveFeedback,
          ),
          const SizedBox(width: 8),
          _buildFeedbackButton(
            icon: Icons.thumb_down_outlined,
            activeIcon: Icons.thumb_down,
            isActive: userFeedback == 'negative',
            onTap: _handleNegativeFeedback,
          ),
        ],
      ),
    );
  }

  Widget _buildFeedbackButton({
    required IconData icon,
    required IconData activeIcon,
    required bool isActive,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.all(6),
        decoration: BoxDecoration(
          color: isActive ? const Color(0xFFE0E7FF) : Colors.transparent,
          shape: BoxShape.circle,
        ),
        child: Icon(
          isActive ? activeIcon : icon,
          size: 18,
          color: isActive ? const Color(0xFF3B82F6) : Colors.grey[600],
        ),
      ),
    );
  }

  // 🎨 UX FIX: Badge for feedback that was already given (from backend)
  Widget _buildFeedbackBadge(String? rating) {
    final isHelpful = rating == 'helpful';
    final icon = isHelpful ? Icons.thumb_up : Icons.thumb_down;
    final label = isHelpful ? 'Helpful' : 'Not helpful';
    final color = isHelpful ? Colors.green : Colors.orange;
    
    return Container(
      margin: const EdgeInsets.only(top: 8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 14,
            color: color[600],
          ),
          const SizedBox(width: 6),
          Text(
            '✓ $label',
            style: TextStyle(
              fontSize: 12,
              color: color[700],
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeedbackGiven() {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      child: Row(
        children: [
          Icon(
            Icons.check_circle,
            size: 14,
            color: Colors.green[600],
          ),
          const SizedBox(width: 6),
          Text(
            'Thanks for the feedback!',
            style: TextStyle(
              fontSize: 12,
              color: Colors.green[700],
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  void _handlePositiveFeedback() {
    setState(() {
      userFeedback = 'positive';
    });
    
    // ✅ LOG: Capture feedback
    debugPrint('📊 [FEEDBACK CAPTURED] Positive feedback for message: ${widget.messageId}');

    // ✅ Call parent callback with data
    widget.onFeedbackSubmit?.call(widget.messageId, 'helpful', [], null);
  }

  void _handleNegativeFeedback() {
    setState(() {
      userFeedback = 'negative';
    });

    // Show correction dialog
    _showCorrectionDialog();
  }

  void _showCorrectionDialog() {
    showDialog(
      context: context,
      builder: (context) => _CorrectionDialog(
        messageId: widget.messageId,
        onSubmit: widget.onFeedbackSubmit,
      ),
    );
  }
}

/// Separate StatefulWidget for the correction dialog
/// This ensures setState works correctly for checkbox interactions
class _CorrectionDialog extends StatefulWidget {
  final String messageId;
  final Function(String messageId, String rating, List<String> corrections, String? comment)? onSubmit;

  const _CorrectionDialog({
    required this.messageId,
    this.onSubmit,
  });

  @override
  State<_CorrectionDialog> createState() => _CorrectionDialogState();
}

class _CorrectionDialogState extends State<_CorrectionDialog> {
  final TextEditingController _correctionController = TextEditingController();
  final Map<String, bool> _corrections = {
    'food': false,
    'quantity': false,
    'calories': false,
    'timing': false,
    'other': false,
  };

  @override
  void dispose() {
    _correctionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: const [
          Icon(Icons.feedback_outlined, color: Color(0xFF3B82F6)),
          SizedBox(width: 8),
          Text('Help AI Learn'),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'What was wrong?',
              style: TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 12),
            _buildCorrectionOption('Wrong food item', 'food'),
            _buildCorrectionOption('Wrong quantity', 'quantity'),
            _buildCorrectionOption('Wrong calories', 'calories'),
            _buildCorrectionOption('Wrong meal timing', 'timing'),
            _buildCorrectionOption('Other', 'other'),
            const SizedBox(height: 16),
            TextField(
              controller: _correctionController,
              decoration: const InputDecoration(
                labelText: 'Tell us more (optional)',
                border: OutlineInputBorder(),
                hintText: 'What should it have been?',
              ),
              maxLines: 2,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            // ✅ LOG: Capture negative feedback with corrections
            final selectedCorrections = _corrections.entries
                .where((e) => e.value)
                .map((e) => e.key)
                .toList();
            final comment = _correctionController.text.isNotEmpty ? _correctionController.text : null;
            
            debugPrint('📊 [FEEDBACK CAPTURED] Negative feedback for message: ${widget.messageId}');
            debugPrint('   Corrections selected: $selectedCorrections');
            debugPrint('   Comment: $comment');
            
            Navigator.pop(context);
            
            // ✅ Call parent callback with data
            widget.onSubmit?.call(widget.messageId, 'not_helpful', selectedCorrections, comment);
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF3B82F6),
          ),
          child: const Text('Submit'),
        ),
      ],
    );
  }

  Widget _buildCorrectionOption(String label, String value) {
    return CheckboxListTile(
      title: Text(label),
      value: _corrections[value] ?? false,
      dense: true,
      contentPadding: EdgeInsets.zero,
      onChanged: (val) {
        setState(() {
          _corrections[value] = val ?? false;
        });
      },
    );
  }
}

