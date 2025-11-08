import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/home_variant_provider.dart';

/// Screen to select home screen variant
class HomeScreenStyleSelector extends StatefulWidget {
  const HomeScreenStyleSelector({super.key});

  @override
  State<HomeScreenStyleSelector> createState() => _HomeScreenStyleSelectorState();
}

class _HomeScreenStyleSelectorState extends State<HomeScreenStyleSelector> {
  Future<void> _selectVariant(String variant) async {
    // Update the provider - this will instantly rebuild all listeners
    await context.read<HomeVariantProvider>().setVariant(variant);
    
    if (mounted) {
      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('✅ Switched instantly!'),
          backgroundColor: const Color(0xFF34C759),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          duration: const Duration(seconds: 1),
        ),
      );
      
      // Navigate back to home
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        title: const Text('Home Screen Style'),
        backgroundColor: Colors.white,
        elevation: 0,
        foregroundColor: const Color(0xFF1F2937),
      ),
      body: ListView(
              padding: const EdgeInsets.all(20),
              children: [
                const Text(
                  'Choose Your Style',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1F2937),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Select the home screen design that works best for you. Changes apply instantly!',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 24),
                
                // Variant 1
                _buildVariantCard(
                  variant: 'v1',
                  title: 'Original',
                  subtitle: 'Horizontal swipeable cards',
                  features: [
                    '✓ Swipeable metric cards',
                    '✓ Simple chat navigation',
                    '✓ Quick action buttons',
                  ],
                  icon: '📱',
                ),
                
                const SizedBox(height: 16),
                
                // Variant 2
                _buildVariantCard(
                  variant: 'v2',
                  title: 'Hybrid',
                  subtitle: 'Calorie ring + activity feed',
                  features: [
                    '✓ Bottom sheet chat',
                    '✓ Calorie ring display',
                    '✓ Activity timeline',
                    '✓ Compact metrics',
                  ],
                  icon: '🔥',
                  recommended: true,
                ),
                
                const SizedBox(height: 16),
                
                // Variant 3
                _buildVariantCard(
                  variant: 'v3',
                  title: 'Apple Premium',
                  subtitle: 'Triple rings + glassmorphism',
                  features: [
                    '✓ Hero animation chat',
                    '✓ Triple ring system',
                    '✓ Glassmorphism effects',
                    '✓ Dark theme',
                  ],
                  icon: '✨',
                  premium: true,
                ),
                
                const SizedBox(height: 16),
                
                // Variant 4
                _buildVariantCard(
                  variant: 'v4',
                  title: 'Compact AI',
                  subtitle: 'Inline chat + AI insights carousel',
                  features: [
                    '✓ Compact activity rings',
                    '✓ Inline expandable chat',
                    '✓ Horizontal insights scroll',
                    '✓ Maximum space efficiency',
                  ],
                  icon: '🚀',
                  recommended: true,
                ),
              ],
            ),
    );
  }

  Widget _buildVariantCard({
    required String variant,
    required String title,
    required String subtitle,
    required List<String> features,
    required String icon,
    bool recommended = false,
    bool premium = false,
  }) {
    final currentVariant = context.watch<HomeVariantProvider>().variant;
    final isSelected = currentVariant == variant;

    return GestureDetector(
      onTap: () => _selectVariant(variant),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? const Color(0xFF6366F1) : Colors.grey[200]!,
            width: isSelected ? 2 : 1,
          ),
          boxShadow: [
            if (isSelected)
              BoxShadow(
                color: const Color(0xFF6366F1).withOpacity(0.2),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  icon,
                  style: const TextStyle(fontSize: 32),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            title,
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF1F2937),
                            ),
                          ),
                          if (recommended) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: const Color(0xFF34C759).withOpacity(0.1),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Text(
                                'Recommended',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                  color: Color(0xFF34C759),
                                ),
                              ),
                            ),
                          ],
                          if (premium) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                gradient: const LinearGradient(
                                  colors: [Color(0xFFFFD700), Color(0xFFFFA500)],
                                ),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Text(
                                'Premium',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white,
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
                if (isSelected)
                  Container(
                    width: 32,
                    height: 32,
                    decoration: const BoxDecoration(
                      color: Color(0xFF6366F1),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.check,
                      color: Colors.white,
                      size: 20,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 16),
            ...features.map((feature) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(
                feature,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[700],
                ),
              ),
            )),
          ],
        ),
      ),
    );
  }
}

