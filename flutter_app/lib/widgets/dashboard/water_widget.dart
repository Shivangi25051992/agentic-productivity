import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';

/// Water Tracking Widget
/// Shows daily water intake with visual glass indicators
class WaterWidget extends StatefulWidget {
  const WaterWidget({Key? key}) : super(key: key);

  @override
  State<WaterWidget> createState() => _WaterWidgetState();
}

class _WaterWidgetState extends State<WaterWidget> {
  int _waterMl = 0;
  int _waterGoal = 2000; // Default 2L goal
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadWaterData();
  }

  Future<void> _loadWaterData() async {
    if (!mounted) return;
    
    setState(() => _isLoading = true);
    
    try {
      final auth = context.read<AuthProvider>();
      final api = ApiService(auth);
      
      // Fetch today's water logs
      final now = DateTime.now();
      final startOfDay = DateTime(now.year, now.month, now.day);
      final endOfDay = startOfDay.add(const Duration(days: 1));
      
      final response = await api.get('/timeline?types=water&start_date=${startOfDay.toIso8601String()}&end_date=${endOfDay.toIso8601String()}&limit=100');
      
      if (response['activities'] != null) {
        int totalMl = 0;
        for (var activity in response['activities']) {
          final details = activity['details'] as Map<String, dynamic>?;
          if (details != null) {
            totalMl += (details['quantity_ml'] as num?)?.toInt() ?? 0;
          }
        }
        
        if (mounted) {
          setState(() {
            _waterMl = totalMl;
            _isLoading = false;
          });
        }
      }
    } catch (e) {
      print('Error loading water data: $e');
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _quickAddWater(int ml) async {
    try {
      final auth = context.read<AuthProvider>();
      final api = ApiService(auth);
      
      await api.post('/timeline/water', {
        'quantity_ml': ml,
        'timestamp': DateTime.now().toIso8601String(),
      });
      
      // Optimistic update
      setState(() {
        _waterMl += ml;
      });
      
      // Show success feedback
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('💧 Added ${ml}ml water!'),
            duration: const Duration(seconds: 1),
            backgroundColor: Colors.cyan,
          ),
        );
      }
      
      // Reload to sync with server
      await _loadWaterData();
    } catch (e) {
      print('Error adding water: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Failed to add water. Please try again.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final glasses = (_waterMl / 250).ceil(); // 1 glass = 250ml
    final goalGlasses = (_waterGoal / 250).ceil();
    final progress = _waterGoal > 0 ? (_waterMl / _waterGoal).clamp(0.0, 1.0) : 0.0;
    final percentage = (progress * 100).toInt();

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.cyan.shade50,
              Colors.blue.shade50,
            ],
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with Quick-Add Icon
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.cyan,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.water_drop, color: Colors.white, size: 20),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'Water Intake',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                if (_isLoading)
                  const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                // Quick-Add Button
                if (!_isLoading)
                  IconButton(
                    icon: Icon(Icons.add_circle, color: Colors.cyan.shade700, size: 28),
                    onPressed: () {
                      // Quick add 250ml (1 glass)
                      _quickAddWater(250);
                    },
                    tooltip: 'Quick add 1 glass (250ml)',
                  ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Progress
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '$glasses',
                  style: TextStyle(
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                    color: Colors.cyan.shade700,
                  ),
                ),
                const SizedBox(width: 4),
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Text(
                    '/ $goalGlasses glasses',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[600],
                    ),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 4),
            
            Text(
              '${_waterMl}ml / ${_waterGoal}ml',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Progress Bar
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: progress,
                minHeight: 8,
                backgroundColor: Colors.grey[200],
                valueColor: AlwaysStoppedAnimation<Color>(Colors.cyan),
              ),
            ),
            
            const SizedBox(height: 8),
            
            // Percentage
            Text(
              '$percentage% of daily goal',
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Visual Glasses
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: List.generate(
                goalGlasses,
                (index) => Icon(
                  index < glasses ? Icons.water_drop : Icons.water_drop_outlined,
                  color: index < glasses ? Colors.cyan : Colors.grey[300],
                  size: 24,
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Motivational Message
            if (percentage >= 100)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.check_circle, color: Colors.green.shade700, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Great hydration! 💧',
                        style: TextStyle(
                          color: Colors.green.shade700,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              )
            else if (percentage >= 50)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.trending_up, color: Colors.blue.shade700, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Keep going! You\'re halfway there 💪',
                        style: TextStyle(
                          color: Colors.blue.shade700,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              )
            else
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, color: Colors.orange.shade700, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Stay hydrated throughout the day 💧',
                        style: TextStyle(
                          color: Colors.orange.shade700,
                          fontWeight: FontWeight.w600,
                        ),
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
}


