import 'package:flutter/material.dart';

/// 🧠 Phase 2: Alternative Picker Widget
/// 
/// Shows 2-3 alternative interpretations when AI confidence is low
/// Allows user to select the correct one
class AlternativePicker extends StatefulWidget {
  final List<Map<String, dynamic>> alternatives;
  final int? initialSelectedIndex;
  final Function(int index, Map<String, dynamic> alternative)? onSelect;

  const AlternativePicker({
    Key? key,
    required this.alternatives,
    this.initialSelectedIndex = 0,
    this.onSelect,
  }) : super(key: key);

  @override
  State<AlternativePicker> createState() => _AlternativePickerState();
}

class _AlternativePickerState extends State<AlternativePicker> {
  late int selectedIndex;
  bool isConfirming = false;

  @override
  void initState() {
    super.initState();
    selectedIndex = widget.initialSelectedIndex ?? 0;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFFEF3C7),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFFF59E0B),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Icon(
                Icons.help_outline,
                size: 20,
                color: Colors.orange[800],
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'I\'m not 100% sure. Did you mean:',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Colors.orange[900],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Alternatives list
          ...List.generate(widget.alternatives.length, (index) {
            final alternative = widget.alternatives[index];
            return _buildAlternativeOption(index, alternative);
          }),

          const SizedBox(height: 16),

          // Action buttons
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: isConfirming ? null : _handleSomethingElse,
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF6B7280),
                    side: const BorderSide(color: Color(0xFFD1D5DB)),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text(
                    'Something else',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  onPressed: isConfirming ? null : _handleConfirm,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFF59E0B),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: isConfirming
                      ? const SizedBox(
                          height: 16,
                          width: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Text(
                          'Confirm',
                          style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                        ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAlternativeOption(int index, Map<String, dynamic> alternative) {
    final isSelected = index == selectedIndex;
    final interpretation = alternative['interpretation'] as String? ?? 'Option ${index + 1}';
    final confidence = alternative['confidence'] as num? ?? 0.0;
    final explanation = alternative['explanation'] as String? ?? '';
    final data = alternative['data'] as Map<String, dynamic>? ?? {};
    final calories = (data['calories'] as num?)?.round() ?? 0;

    return GestureDetector(
      onTap: () {
        setState(() {
          selectedIndex = index;
        });
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? const Color(0xFFF59E0B) : const Color(0xFFE5E7EB),
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            // Radio button
            Container(
              width: 20,
              height: 20,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: isSelected ? const Color(0xFFF59E0B) : const Color(0xFFD1D5DB),
                  width: 2,
                ),
              ),
              child: isSelected
                  ? Center(
                      child: Container(
                        width: 10,
                        height: 10,
                        decoration: const BoxDecoration(
                          shape: BoxShape.circle,
                          color: Color(0xFFF59E0B),
                        ),
                      ),
                    )
                  : null,
            ),
            const SizedBox(width: 12),

            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          interpretation,
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                            color: const Color(0xFF1F2937),
                          ),
                        ),
                      ),
                      if (calories > 0) ...[
                        Text(
                          '$calories kcal',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: Colors.orange[700],
                          ),
                        ),
                      ],
                    ],
                  ),
                  if (explanation.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(
                      explanation,
                      style: const TextStyle(
                        fontSize: 13,
                        color: Color(0xFF6B7280),
                        height: 1.4,
                      ),
                    ),
                  ],
                  const SizedBox(height: 4),
                  Text(
                    '${(confidence * 100).round()}% confidence',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _handleConfirm() {
    if (widget.onSelect != null) {
      setState(() {
        isConfirming = true;
      });

      final selected = widget.alternatives[selectedIndex];
      
      // ✅ LOG: Capture alternative selection
      debugPrint('📊 [ALTERNATIVE SELECTED] Index: $selectedIndex');
      debugPrint('   Interpretation: ${selected['interpretation']}');
      debugPrint('   Confidence: ${selected['confidence']}');
      debugPrint('   Data: ${selected['data']}');
      
      widget.onSelect!(selectedIndex, selected);

      // Show success feedback
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: const [
              Icon(Icons.check_circle, color: Colors.white, size: 20),
              SizedBox(width: 8),
              Text('Updated! Thanks for the feedback.'),
            ],
          ),
          backgroundColor: const Color(0xFF10B981),
          behavior: SnackBarBehavior.floating,
          duration: const Duration(seconds: 2),
        ),
      );
      
      // ✅ FIX: Reset loading state after 500ms
      Future.delayed(const Duration(milliseconds: 500), () {
        if (mounted) {
          setState(() {
            isConfirming = false;
          });
        }
      });
    }
  }

  void _handleSomethingElse() {
    // Show text input dialog for user to provide correct input
    final TextEditingController controller = TextEditingController();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('What did you mean?'),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(
            hintText: 'e.g., 150g grilled chicken',
            border: OutlineInputBorder(),
          ),
          onSubmitted: (value) {
            if (value.trim().isNotEmpty) {
              Navigator.pop(context);
              _submitCorrection(value.trim());
            }
          },
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final correction = controller.text.trim();
              if (correction.isNotEmpty) {
                Navigator.pop(context);
                _submitCorrection(correction);
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF14B8A6),
            ),
            child: const Text('Submit'),
          ),
        ],
      ),
    );
  }
  
  void _submitCorrection(String correction) {
    debugPrint('📝 [CORRECTION] User provided: $correction');
    
    // Trigger onSelect with null to indicate "something else" was chosen
    // The parent widget should handle hiding the picker and sending feedback
    if (widget.onSelect != null) {
      // Create a special alternative object to indicate user correction
      final correctionAlternative = {
        'interpretation': correction,
        'confidence': 1.0, // User's input is 100% what they meant
        'explanation': 'User-provided correction',
        'data': {'user_correction': true, 'corrected_text': correction},
      };
      
      widget.onSelect!(-1, correctionAlternative); // Use -1 to indicate custom input
    }
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Row(
          children: [
            Icon(Icons.check_circle, color: Colors.white, size: 20),
            SizedBox(width: 8),
            Text('Thanks! AI will learn from this.'),
          ],
        ),
        backgroundColor: Color(0xFF3B82F6),
        behavior: SnackBarBehavior.floating,
        duration: Duration(seconds: 2),
      ),
    );
  }
}

