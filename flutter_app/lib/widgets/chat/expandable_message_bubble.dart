import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:provider/provider.dart';
import '../../services/api_service.dart';
import 'confidence_badge.dart';
import 'explanation_sheet.dart';
import 'alternative_picker.dart';
import 'feedback_buttons.dart';

/// ✨ Expandable Chat Bubble - Shows summary + suggestion by default,
/// with expandable details on demand (nutrition, progress, insights)
/// 🧠 Phase 2: Now includes confidence score, explanations, alternatives, and feedback
class ExpandableMessageBubble extends StatefulWidget {
  final String summary;
  final String suggestion;
  final Map<String, dynamic>? details;
  final String? timestamp;
  
  // 🧠 PHASE 2: Explainable AI fields
  final double? confidenceScore;
  final String? confidenceLevel;
  final Map<String, dynamic>? confidenceFactors;
  final Map<String, dynamic>? explanation;
  final List<Map<String, dynamic>>? alternatives;
  final String? messageId;
  
  // 🎨 UX FIX: Feedback state
  final bool feedbackGiven;
  final String? feedbackRating;

  const ExpandableMessageBubble({
    super.key,
    required this.summary,
    required this.suggestion,
    this.details,
    this.timestamp,
    // 🧠 PHASE 2 fields
    this.confidenceScore,
    this.confidenceLevel,
    this.confidenceFactors,
    this.explanation,
    this.alternatives,
    this.messageId,
    // 🎨 UX FIX fields
    this.feedbackGiven = false,
    this.feedbackRating,
  });

  @override
  State<ExpandableMessageBubble> createState() => _ExpandableMessageBubbleState();
}

class _ExpandableMessageBubbleState extends State<ExpandableMessageBubble>
    with SingleTickerProviderStateMixin {
  bool _isExpanded = false;
  late AnimationController _animationController;
  late Animation<double> _animation;
  
  // 🔀 Alternative selection state
  bool _alternativeSelected = false;
  Map<String, dynamic>? _selectedAlternative;
  String? _updatedSummary;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    _animation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );
    _loadExpandPreference();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _loadExpandPreference() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      // Default to collapsed (false) for better UX - user can expand if needed
      final shouldExpand = prefs.getBool('chat_expand_preference') ?? false;
      if (shouldExpand && mounted) {
        setState(() {
          _isExpanded = true;
          _animationController.value = 1.0;
        });
      }
      // Note: If shouldExpand is false (default), cards remain collapsed
    } catch (e) {
      // Ignore errors loading preferences
      debugPrint('Error loading expand preference: $e');
    }
  }

  Future<void> _toggleExpanded() async {
    setState(() {
      _isExpanded = !_isExpanded;
    });

    if (_isExpanded) {
      _animationController.forward();
    } else {
      _animationController.reverse();
    }

    // Save preference
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('chat_expand_preference', _isExpanded);
    } catch (e) {
      debugPrint('Error saving expand preference: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        CircleAvatar(
          child: Icon(Icons.auto_awesome, color: isDark ? null : Colors.white),
        ),
        const SizedBox(width: 8),
        Flexible(
          child: Container(
            margin: const EdgeInsets.symmetric(vertical: 4),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: theme.colorScheme.surface,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
                bottomRight: Radius.circular(12),
              ),
              boxShadow: const [
                BoxShadow(
                  blurRadius: 12,
                  color: Colors.black12,
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ✨ ALWAYS VISIBLE: Summary + 🧠 PHASE 2: Confidence + "Why?" button
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(child: _buildSummary(theme)),
                    // 🧠 Confidence badge
                    if (widget.confidenceScore != null && widget.confidenceLevel != null) ...[
                      const SizedBox(width: 8),
                      ConfidenceBadge(
                        score: widget.confidenceScore!,
                        level: widget.confidenceLevel!,
                        onTap: widget.explanation != null 
                            ? () => _showExplanation(context)
                            : null,
                      ),
                    ],
                    // 🧠 "Why?" button
                    if (widget.explanation != null) ...[
                      const SizedBox(width: 4),
                      InkWell(
                        onTap: () => _showExplanation(context),
                        borderRadius: BorderRadius.circular(12),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.grey[100],
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Text(
                            'Why?',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFF6B7280),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                
                const SizedBox(height: 12),
                
                // ✨ ALWAYS VISIBLE: Suggestion
                _buildSuggestion(theme),
                
                // 🧠 PHASE 2: Alternative picker (only show if NOT selected AND no feedback given)
                // 🎨 UX FIX: Hide alternatives once user gives feedback (thumbs up/down)
                if (!_alternativeSelected && 
                    widget.alternatives != null && 
                    widget.alternatives!.isNotEmpty && 
                    !widget.feedbackGiven) ...[
                  AlternativePicker(
                    alternatives: widget.alternatives!,
                    onSelect: (index, alternative) async {
                      debugPrint('🔀 [ALTERNATIVE] Selected $index: ${alternative['interpretation']}');
                      
                      // ✅ Check if this is a user correction (index = -1)
                      final isUserCorrection = index == -1 || 
                                               (alternative['data'] as Map?)? ['user_correction'] == true;
                      
                      // ✅ Send selection to backend
                      try {
                        final apiService = Provider.of<ApiService>(context, listen: false);
                        
                        if (isUserCorrection) {
                          // 📝 User provided custom correction - send as feedback
                          final correctedText = alternative['data']?['corrected_text'] as String? ?? 
                                                alternative['interpretation'] as String? ?? '';
                          
                          debugPrint('📡 [CORRECTION] Calling API: POST /chat/feedback with correction');
                          await apiService.post('/chat/feedback', {
                            'message_id': widget.messageId,
                            'rating': 'not_helpful',
                            'corrections': [correctedText],
                            'comment': 'User provided alternative interpretation',
                          });
                          
                          debugPrint('✅ [CORRECTION] Feedback sent successfully');
                          
                          // Hide picker and show simpler message
                          if (mounted) {
                            setState(() {
                              _alternativeSelected = true;
                              _selectedAlternative = alternative;
                            });
                          }
                        } else {
                          // 🔀 User selected one of the AI alternatives
                          debugPrint('📡 [ALTERNATIVE] Calling API: POST /chat/select-alternative');
                          final response = await apiService.post('/chat/select-alternative', {
                            'message_id': widget.messageId,
                            'selected_index': index,
                            'selected_alternative': alternative,
                            'rejected_primary': null,
                          });
                          
                          debugPrint('✅ [ALTERNATIVE] API Success: ${response['feedback_id']}');
                          
                          // ✅ UPDATE STATE: Hide picker, update summary, collapse card
                          if (mounted) {
                            setState(() {
                              _alternativeSelected = true;
                              _selectedAlternative = alternative;
                              
                              // Build new summary from selected alternative
                              final interpretation = alternative['interpretation'] as String? ?? 'Item';
                              final calories = alternative['data']?['calories'] ?? 0;
                              _updatedSummary = '$interpretation logged! ${calories.round()} kcal';
                              
                              // Collapse card
                              _isExpanded = false;
                              _animationController.reverse();
                            });
                            
                            // Show success message
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Updated! Thanks for the feedback.'),
                                backgroundColor: Color(0xFF10B981),
                                duration: Duration(seconds: 2),
                              ),
                            );
                          }
                        }
                      } catch (e, stackTrace) {
                        debugPrint('❌ [ALTERNATIVE] API Error: $e');
                        debugPrint('❌ [ALTERNATIVE] Stack trace: $stackTrace');
                        
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Failed to save selection. Please try again.'),
                              backgroundColor: Colors.red,
                              duration: Duration(seconds: 3),
                            ),
                          );
                        }
                      }
                    },
                  ),
                ],
                
                // ✨ EXPANDABLE: Details
                if (widget.details != null) ...[
                  const SizedBox(height: 12),
                  _buildExpandButton(theme),
                  _buildExpandableDetails(theme),
                ],
                
                // Timestamp
                if (widget.timestamp != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    widget.timestamp!,
                    style: TextStyle(
                      fontSize: 11,
                      color: theme.colorScheme.onSurface.withOpacity(0.6),
                    ),
                  ),
                ],
                
                // 🧠 PHASE 2: Feedback buttons / 🎨 UX FIX: Badge if feedback given
                if (widget.messageId != null) ...[
                  FeedbackButtons(
                    messageId: widget.messageId!,
                    onFeedbackSubmit: _handleFeedbackSubmit,
                    // 🎨 UX FIX: Pass feedback state
                    feedbackGiven: widget.feedbackGiven,
                    feedbackRating: widget.feedbackRating,
                  ),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSummary(ThemeData theme) {
    // ✅ Show updated summary if alternative was selected
    final summaryText = _updatedSummary ?? widget.summary;
    
    return Text(
      summaryText,
      style: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.bold,
        color: theme.colorScheme.onSurface,
      ),
    );
  }

  Widget _buildSuggestion(ThemeData theme) {
    final isDark = theme.brightness == Brightness.dark;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? theme.colorScheme.primaryContainer : Colors.blue.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(
            Icons.lightbulb_outline,
            size: 18,
            color: isDark ? theme.colorScheme.onPrimaryContainer : Colors.blue.shade700,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              widget.suggestion,
              style: TextStyle(
                fontSize: 14,
                color: isDark ? theme.colorScheme.onPrimaryContainer : Colors.blue.shade900,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildExpandButton(ThemeData theme) {
    return InkWell(
      onTap: _toggleExpanded,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              _isExpanded ? "Show less" : "More details",
              style: TextStyle(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
            const SizedBox(width: 4),
            AnimatedRotation(
              turns: _isExpanded ? 0.5 : 0,
              duration: const Duration(milliseconds: 300),
              child: Icon(
                Icons.keyboard_arrow_down,
                color: theme.colorScheme.primary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildExpandableDetails(ThemeData theme) {
    return SizeTransition(
      sizeFactor: _animation,
      child: FadeTransition(
        opacity: _animation,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 12),
            if (widget.details?['nutrition'] != null)
              _buildNutritionCard(theme),
            const SizedBox(height: 12),
            if (widget.details?['progress'] != null)
              _buildProgressCard(theme),
            if (widget.details?['insights'] != null) ...[
              const SizedBox(height: 12),
              _buildInsightsCard(theme),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildNutritionCard(ThemeData theme) {
    final nutrition = widget.details!['nutrition'] as Map<String, dynamic>;
    final isDark = theme.brightness == Brightness.dark;
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? theme.colorScheme.surfaceContainerHighest : Colors.grey.shade100,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "📊 Nutrition Breakdown",
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
          ),
          const SizedBox(height: 8),
          _buildNutritionRow("Calories", "${nutrition['calories'] ?? 0} kcal", theme),
          _buildNutritionRow("Protein", "${nutrition['protein_g'] ?? 0}g", theme),
          _buildNutritionRow("Carbs", "${nutrition['carbs_g'] ?? 0}g", theme),
          _buildNutritionRow("Fat", "${nutrition['fat_g'] ?? 0}g", theme),
        ],
      ),
    );
  }

  Widget _buildNutritionRow(String label, String value, ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              color: theme.colorScheme.onSurface.withOpacity(0.7),
              fontSize: 13,
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.w500,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProgressCard(ThemeData theme) {
    final progress = widget.details!['progress'] as Map<String, dynamic>;
    final progressPct = ((progress['progress_percent'] ?? 0) as num) / 100;
    final isDark = theme.brightness == Brightness.dark;
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? Colors.green.shade900.withOpacity(0.3) : Colors.green.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "📈 Today's Progress",
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: progressPct.clamp(0.0, 1.0),
              backgroundColor: isDark ? Colors.grey.shade700 : Colors.grey.shade300,
              color: Colors.green,
              minHeight: 8,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "${progress['daily_calories'] ?? 0} / ${progress['daily_goal'] ?? 2000} kcal "
            "(${progress['remaining'] ?? 0} remaining)",
            style: TextStyle(
              fontSize: 12,
              color: theme.colorScheme.onSurface.withOpacity(0.7),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInsightsCard(ThemeData theme) {
    final insights = widget.details!['insights'] as String;
    final isDark = theme.brightness == Brightness.dark;
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? Colors.purple.shade900.withOpacity(0.3) : Colors.purple.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "💡 Insights",
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
          ),
          const SizedBox(height: 8),
          Text(
            insights,
            style: TextStyle(
              fontSize: 13,
              color: theme.colorScheme.onSurface.withOpacity(0.8),
            ),
          ),
        ],
      ),
    );
  }

  // 💬 FEEDBACK: Handle feedback submission
  Future<void> _handleFeedbackSubmit(
    String messageId,
    String rating,
    List<String> corrections,
    String? comment,
  ) async {
    debugPrint('📊 [FEEDBACK] Submitting: rating=$rating, corrections=$corrections, comment=$comment');
    
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      
      debugPrint('📡 [FEEDBACK] Calling API: POST /chat/feedback');
      final response = await apiService.post('/chat/feedback', {
        'message_id': messageId,
        'rating': rating,
        'corrections': corrections,
        'comment': comment,
      });
      
      debugPrint('✅ [FEEDBACK] API Success: ${response['feedback_id']}');
      
      // Show success message
      if (mounted) {
        final message = response['message'] ?? 
                       (rating == 'helpful' 
                         ? 'Thank you for your feedback!' 
                         : 'Feedback received. AI will learn from this!');
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(message),
            backgroundColor: rating == 'helpful' ? const Color(0xFF10B981) : const Color(0xFF3B82F6),
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } catch (e, stackTrace) {
      debugPrint('❌ [FEEDBACK] API Error: $e');
      debugPrint('❌ [FEEDBACK] Stack trace: $stackTrace');
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Failed to save feedback. Please try again.'),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 3),
          ),
        );
      }
    }
  }

  // 🧠 PHASE 2: Show explanation sheet
  void _showExplanation(BuildContext context) {
    if (widget.explanation != null) {
      ExplanationSheet.show(
        context,
        explanation: widget.explanation!,
        confidenceFactors: widget.confidenceFactors,
        confidenceScore: widget.confidenceScore,
      );
    }
  }
}

