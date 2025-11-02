import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';
import 'feedback_dialog.dart';

/// Floating feedback button that appears on all screens
/// Allows users to submit feedback from anywhere in the app
class FloatingFeedbackButton extends StatefulWidget {
  final String screenName;
  
  const FloatingFeedbackButton({
    Key? key,
    required this.screenName,
  }) : super(key: key);

  @override
  State<FloatingFeedbackButton> createState() => _FloatingFeedbackButtonState();
}

class _FloatingFeedbackButtonState extends State<FloatingFeedbackButton> {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    return Positioned(
      right: 16,
      bottom: 80, // Above bottom navigation
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        child: _isExpanded ? _buildExpandedMenu() : _buildCollapsedButton(),
      ),
    );
  }

  Widget _buildCollapsedButton() {
    return FloatingActionButton(
      heroTag: 'feedback_button',
      onPressed: () {
        setState(() {
          _isExpanded = true;
        });
      },
      backgroundColor: Colors.deepPurple,
      child: const Icon(Icons.feedback, color: Colors.white),
      tooltip: 'Send Feedback',
    );
  }

  Widget _buildExpandedMenu() {
    return Material(
      elevation: 8,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Close button
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Padding(
                  padding: EdgeInsets.only(left: 8),
                  child: Text(
                    'How can we help?',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close, size: 20),
                  onPressed: () {
                    setState(() {
                      _isExpanded = false;
                    });
                  },
                ),
              ],
            ),
            const Divider(height: 1),
            const SizedBox(height: 8),
            
            // Feedback options
            _buildMenuOption(
              icon: Icons.bug_report,
              label: 'Report Bug',
              color: Colors.red,
              onTap: () => _showFeedbackDialog(context, 'bug'),
            ),
            _buildMenuOption(
              icon: Icons.lightbulb_outline,
              label: 'Suggest Feature',
              color: Colors.orange,
              onTap: () => _showFeedbackDialog(context, 'feature'),
            ),
            _buildMenuOption(
              icon: Icons.design_services,
              label: 'UX Feedback',
              color: Colors.blue,
              onTap: () => _showFeedbackDialog(context, 'ux'),
            ),
            _buildMenuOption(
              icon: Icons.chat_bubble_outline,
              label: 'General Feedback',
              color: Colors.green,
              onTap: () => _showFeedbackDialog(context, 'other'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuOption({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        child: Row(
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(width: 12),
            Text(
              label,
              style: const TextStyle(fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }

  void _showFeedbackDialog(BuildContext context, String type) {
    setState(() {
      _isExpanded = false;
    });
    
    showDialog(
      context: context,
      builder: (context) => FeedbackDialog(
        screenName: widget.screenName,
        feedbackType: type,
      ),
    );
  }
}

/// Wrapper widget to add feedback button to any screen
class WithFeedbackButton extends StatelessWidget {
  final Widget child;
  final String screenName;

  const WithFeedbackButton({
    Key? key,
    required this.child,
    required this.screenName,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        FloatingFeedbackButton(screenName: screenName),
      ],
    );
  }
}


