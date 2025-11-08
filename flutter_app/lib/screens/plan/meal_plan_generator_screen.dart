import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/api_service.dart';
import '../../services/meal_planning_api_service.dart';
import '../../utils/constants.dart';

/// AI Meal Plan Generator Screen
/// Beautiful form to collect user preferences and generate meal plans
class MealPlanGeneratorScreen extends StatefulWidget {
  const MealPlanGeneratorScreen({Key? key}) : super(key: key);

  @override
  State<MealPlanGeneratorScreen> createState() => _MealPlanGeneratorScreenState();
}

class _MealPlanGeneratorScreenState extends State<MealPlanGeneratorScreen> {
  final _formKey = GlobalKey<FormState>();
  
  // Form state
  int _dailyCalories = 2000;
  int _dailyProtein = 150;
  int _numPeople = 1;
  String _prepTimePreference = 'medium';
  final List<String> _selectedDietaryPreferences = [];
  
  // UI state
  bool _isGenerating = false;
  int _loadingMessageIndex = 0;
  Timer? _loadingMessageTimer;
  int _existingPlanCount = 0;
  bool _isLoadingPlanCount = true;
  
  // Exciting loading messages with Yuvi
  final List<Map<String, dynamic>> _loadingMessages = [
    {'icon': '🤖', 'text': '${AppConstants.aiName} is analyzing your preferences...'},
    {'icon': '🧠', 'text': '${AppConstants.aiName} is crafting your plan...'},
    {'icon': '🥗', 'text': '${AppConstants.aiName} is selecting ingredients...'},
    {'icon': '💪', 'text': '${AppConstants.aiName} is calculating protein...'},
    {'icon': '🔥', 'text': '${AppConstants.aiName} is balancing calories...'},
    {'icon': '📊', 'text': '${AppConstants.aiName} is optimizing macros...'},
    {'icon': '🍳', 'text': '${AppConstants.aiName} is creating breakfasts...'},
    {'icon': '🥙', 'text': '${AppConstants.aiName} is planning lunches...'},
    {'icon': '🍛', 'text': '${AppConstants.aiName} is designing dinners...'},
    {'icon': '🍎', 'text': '${AppConstants.aiName} is adding healthy snacks...'},
    {'icon': '🌟', 'text': '${AppConstants.aiName} is ensuring variety...'},
    {'icon': '✨', 'text': 'Almost there! ${AppConstants.aiName} is finalizing...'},
  ];
  
  @override
  void initState() {
    super.initState();
    _loadPlanCount();
  }
  
  Future<void> _loadPlanCount() async {
    try {
      final apiService = context.read<ApiService>();
      final mealPlanningApi = MealPlanningApiService(apiService);
      final plans = await mealPlanningApi.getMealPlans(limit: 20, activeOnly: false);
      
      // Count plans for current week
      final now = DateTime.now();
      final monday = now.subtract(Duration(days: now.weekday - 1));
      final weekStart = DateTime(monday.year, monday.month, monday.day);
      
      final weekPlans = plans.where((plan) {
        final planWeekStart = DateTime.parse(plan['week_start_date'] as String);
        return planWeekStart.isAtSameMomentAs(weekStart) || 
               (planWeekStart.year == weekStart.year && 
                planWeekStart.month == weekStart.month && 
                planWeekStart.day == weekStart.day);
      }).toList();
      
      setState(() {
        _existingPlanCount = weekPlans.length;
        _isLoadingPlanCount = false;
      });
      
      print('📊 [GENERATOR] Found $_existingPlanCount plans for current week');
    } catch (e) {
      print('⚠️ [GENERATOR] Error loading plan count: $e');
      setState(() {
        _isLoadingPlanCount = false;
      });
    }
  }
  
  // Options
  final List<Map<String, dynamic>> _dietaryOptions = [
    {'id': 'vegetarian', 'label': 'Vegetarian', 'icon': Icons.eco, 'color': Color(0xFF10B981)},
    {'id': 'vegan', 'label': 'Vegan', 'icon': Icons.spa, 'color': Color(0xFF059669)},
    {'id': 'gluten_free', 'label': 'Gluten-Free', 'icon': Icons.grain, 'color': Color(0xFFF59E0B)},
    {'id': 'dairy_free', 'label': 'Dairy-Free', 'icon': Icons.no_food, 'color': Color(0xFFEF4444)},
    {'id': 'keto', 'label': 'Keto', 'icon': Icons.fitness_center, 'color': Color(0xFF8B5CF6)},
    {'id': 'paleo', 'label': 'Paleo', 'icon': Icons.nature, 'color': Color(0xFF6366F1)},
    {'id': 'low_carb', 'label': 'Low Carb', 'icon': Icons.trending_down, 'color': Color(0xFF06B6D4)},
    {'id': 'high_protein', 'label': 'High Protein', 'icon': Icons.egg, 'color': Color(0xFFEC4899)},
  ];
  
  final List<Map<String, String>> _prepTimeOptions = [
    {'value': 'quick', 'label': '< 20 min', 'desc': 'Quick & Easy'},
    {'value': 'medium', 'label': '20-40 min', 'desc': 'Moderate'},
    {'value': 'long', 'label': '> 40 min', 'desc': 'Elaborate'},
  ];

  @override
  void dispose() {
    _loadingMessageTimer?.cancel();
    super.dispose();
  }

  void _startLoadingMessages() {
    _loadingMessageIndex = 0;
    _loadingMessageTimer?.cancel();
    _loadingMessageTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      if (mounted && _isGenerating) {
        setState(() {
          _loadingMessageIndex = (_loadingMessageIndex + 1) % _loadingMessages.length;
        });
      }
    });
  }

  void _stopLoadingMessages() {
    _loadingMessageTimer?.cancel();
    _loadingMessageTimer = null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFDFCF9),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFF1F2937)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Generate Meal Plan',
          style: TextStyle(
            color: Color(0xFF1F2937),
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                _buildHeader(),
                
                const SizedBox(height: 32),
                
                // Dietary Preferences
                _buildDietaryPreferences(),
                
                const SizedBox(height: 32),
                
                // Nutrition Goals
                _buildNutritionGoals(),
                
                const SizedBox(height: 32),
                
                // Prep Time Preference
                _buildPrepTimePreference(),
                
                const SizedBox(height: 32),
                
                // Number of People
                _buildNumPeople(),
                
                const SizedBox(height: 40),
                
                // Generate Button
                _buildGenerateButton(),
                
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF6366F1).withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(
              Icons.auto_awesome,
              color: Colors.white,
              size: 32,
            ),
          ),
          const SizedBox(width: 16),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'AI-Powered',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Colors.white70,
                    letterSpacing: 0.5,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'Personalized Meal Plan',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDietaryPreferences() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Dietary Preferences',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Color(0xFF1F2937),
          ),
        ),
        const SizedBox(height: 4),
        const Text(
          'Select all that apply',
          style: TextStyle(
            fontSize: 14,
            color: Color(0xFF6B7280),
          ),
        ),
        const SizedBox(height: 16),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: _dietaryOptions.map((option) {
            final isSelected = _selectedDietaryPreferences.contains(option['id']);
            return GestureDetector(
              onTap: () {
                setState(() {
                  if (isSelected) {
                    _selectedDietaryPreferences.remove(option['id']);
                  } else {
                    _selectedDietaryPreferences.add(option['id'] as String);
                  }
                });
              },
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: isSelected ? option['color'] as Color : Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: isSelected 
                        ? option['color'] as Color 
                        : const Color(0xFFE5E7EB),
                    width: 2,
                  ),
                  boxShadow: isSelected
                      ? [
                          BoxShadow(
                            color: (option['color'] as Color).withOpacity(0.3),
                            blurRadius: 12,
                            offset: const Offset(0, 4),
                          ),
                        ]
                      : [],
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      option['icon'] as IconData,
                      color: isSelected ? Colors.white : option['color'] as Color,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      option['label'] as String,
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: isSelected ? Colors.white : const Color(0xFF1F2937),
                      ),
                    ),
                  ],
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildNutritionGoals() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Daily Nutrition Goals',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937),
            ),
          ),
          const SizedBox(height: 24),
          
          // Calories
          _buildSlider(
            label: 'Calories',
            value: _dailyCalories.toDouble(),
            min: 1200,
            max: 4000,
            divisions: 56,
            icon: Icons.local_fire_department,
            color: const Color(0xFFF59E0B),
            unit: 'cal',
            onChanged: (value) => setState(() => _dailyCalories = value.toInt()),
          ),
          
          const SizedBox(height: 24),
          
          // Protein
          _buildSlider(
            label: 'Protein',
            value: _dailyProtein.toDouble(),
            min: 50,
            max: 300,
            divisions: 50,
            icon: Icons.fitness_center,
            color: const Color(0xFF10B981),
            unit: 'g',
            onChanged: (value) => setState(() => _dailyProtein = value.toInt()),
          ),
        ],
      ),
    );
  }

  Widget _buildSlider({
    required String label,
    required double value,
    required double min,
    required double max,
    required int divisions,
    required IconData icon,
    required Color color,
    required String unit,
    required ValueChanged<double> onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 20),
                const SizedBox(width: 8),
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF1F2937),
                  ),
                ),
              ],
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                '${value.toInt()} $unit',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        SliderTheme(
          data: SliderThemeData(
            activeTrackColor: color,
            inactiveTrackColor: color.withOpacity(0.2),
            thumbColor: color,
            overlayColor: color.withOpacity(0.2),
            trackHeight: 6,
          ),
          child: Slider(
            value: value,
            min: min,
            max: max,
            divisions: divisions,
            onChanged: onChanged,
          ),
        ),
      ],
    );
  }

  Widget _buildPrepTimePreference() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Prep Time Preference',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Color(0xFF1F2937),
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: _prepTimeOptions.map((option) {
            final isSelected = _prepTimePreference == option['value'];
            return Expanded(
              child: GestureDetector(
                onTap: () => setState(() => _prepTimePreference = option['value']!),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  margin: const EdgeInsets.symmetric(horizontal: 4),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: isSelected
                        ? const LinearGradient(
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                            colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
                          )
                        : null,
                    color: isSelected ? null : Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: isSelected ? Colors.transparent : const Color(0xFFE5E7EB),
                      width: 2,
                    ),
                    boxShadow: isSelected
                        ? [
                            BoxShadow(
                              color: const Color(0xFF6366F1).withOpacity(0.3),
                              blurRadius: 12,
                              offset: const Offset(0, 4),
                            ),
                          ]
                        : [],
                  ),
                  child: Column(
                    children: [
                      Text(
                        option['label']!,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: isSelected ? Colors.white : const Color(0xFF1F2937),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        option['desc']!,
                        style: TextStyle(
                          fontSize: 12,
                          color: isSelected ? Colors.white70 : const Color(0xFF6B7280),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildNumPeople() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          const Icon(Icons.people, color: Color(0xFF6366F1), size: 24),
          const SizedBox(width: 12),
          const Expanded(
            child: Text(
              'Number of People',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Color(0xFF1F2937),
              ),
            ),
          ),
          IconButton(
            onPressed: _numPeople > 1 
                ? () => setState(() => _numPeople--) 
                : null,
            icon: const Icon(Icons.remove_circle_outline),
            color: const Color(0xFF6366F1),
            iconSize: 28,
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
          ),
          const SizedBox(width: 8),
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: const Color(0xFF6366F1).withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Center(
              child: Text(
                '$_numPeople',
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF6366F1),
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            onPressed: _numPeople < 10 
                ? () => setState(() => _numPeople++) 
                : null,
            icon: const Icon(Icons.add_circle_outline),
            color: const Color(0xFF6366F1),
            iconSize: 28,
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
          ),
        ],
      ),
    );
  }

  Widget _buildGenerateButton() {
    // Smart button: Show upgrade if user has 3+ plans
    final bool hasReachedLimit = _existingPlanCount >= 3;
    
    return Column(
      children: [
        // Show plan count info
        if (!_isLoadingPlanCount && _existingPlanCount > 0)
          Container(
            padding: const EdgeInsets.all(12),
            margin: const EdgeInsets.only(bottom: 16),
            decoration: BoxDecoration(
              color: hasReachedLimit 
                  ? const Color(0xFFF59E0B).withOpacity(0.1)
                  : const Color(0xFF10B981).withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: hasReachedLimit 
                    ? const Color(0xFFF59E0B).withOpacity(0.3)
                    : const Color(0xFF10B981).withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  hasReachedLimit ? Icons.info_outline : Icons.check_circle_outline,
                  color: hasReachedLimit ? const Color(0xFFF59E0B) : const Color(0xFF10B981),
                  size: 20,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    hasReachedLimit
                        ? 'You\'ve generated $_existingPlanCount plans this week (Free tier: 3/3)'
                        : 'You\'ve generated $_existingPlanCount/3 plans this week',
                    style: TextStyle(
                      fontSize: 13,
                      color: hasReachedLimit ? const Color(0xFFF59E0B) : const Color(0xFF10B981),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),
        
        if (_isGenerating)
          Container(
            padding: const EdgeInsets.all(16),
            margin: const EdgeInsets.only(bottom: 16),
            decoration: BoxDecoration(
              color: const Color(0xFF6366F1).withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: const Color(0xFF6366F1).withOpacity(0.3),
                width: 1,
              ),
            ),
            child: const Row(
              children: [
                Icon(
                  Icons.info_outline,
                  color: Color(0xFF6366F1),
                  size: 20,
                ),
                SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Creating your personalized meal plan... This may take up to 2 minutes. Please don\'t close this screen.',
                    style: TextStyle(
                      fontSize: 13,
                      color: Color(0xFF6366F1),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        SizedBox(
          width: double.infinity,
          height: 60,
          child: ElevatedButton(
        onPressed: (_isGenerating || _isLoadingPlanCount) 
            ? null 
            : (hasReachedLimit ? _showPremiumUpgradeDialog : _generateMealPlan),
        style: ElevatedButton.styleFrom(
          backgroundColor: hasReachedLimit ? const Color(0xFFF59E0B) : const Color(0xFF6366F1),
          foregroundColor: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          shadowColor: (hasReachedLimit ? const Color(0xFFF59E0B) : const Color(0xFF6366F1)).withOpacity(0.3),
        ),
        child: _isLoadingPlanCount
            ? const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      color: Colors.white,
                      strokeWidth: 2,
                    ),
                  ),
                  SizedBox(width: 12),
                  Text('Loading...', style: TextStyle(fontSize: 16)),
                ],
              )
            : _isGenerating
            ? Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      color: Colors.white,
                      strokeWidth: 2,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Flexible(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          _loadingMessages[_loadingMessageIndex]['icon']!,
                          style: const TextStyle(fontSize: 20),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _loadingMessages[_loadingMessageIndex]['text']!,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                          textAlign: TextAlign.center,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ],
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(hasReachedLimit ? Icons.rocket_launch : Icons.auto_awesome, size: 24),
                  const SizedBox(width: 12),
                  Text(
                    hasReachedLimit ? 'Upgrade to Premium' : 'Generate Meal Plan',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
          ),
        ),
      ],
    );
  }

  /// Show premium upgrade dialog when free tier limit is reached
  void _showPremiumUpgradeDialog() {
    showDialog(
      context: context,
      barrierDismissible: true,
      builder: (BuildContext context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFFFFF7ED), // Warm orange tint
                  Color(0xFFFEF3C7), // Warm yellow tint
                ],
              ),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Crown icon
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF59E0B),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFFF59E0B).withOpacity(0.3),
                        blurRadius: 20,
                        spreadRadius: 5,
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.workspace_premium,
                    size: 48,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 24),
                
                // Title
                const Text(
                  'You\'ve Reached Your Limit! 🎉',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1F2937),
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                
                // Subtitle
                const Text(
                  'You\'ve generated 3 meal plans this week',
                  style: TextStyle(
                    fontSize: 16,
                    color: Color(0xFF6B7280),
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                
                // Benefits
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: const Color(0xFFF59E0B).withOpacity(0.3),
                      width: 2,
                    ),
                  ),
                  child: Column(
                    children: [
                      _buildBenefit('✨', 'Unlimited meal plans'),
                      const SizedBox(height: 12),
                      _buildBenefit('🎯', 'Advanced customization'),
                      const SizedBox(height: 12),
                      _buildBenefit('📊', 'Detailed nutrition insights'),
                      const SizedBox(height: 12),
                      _buildBenefit('🔄', 'Weekly plan variations'),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                
                // Upgrade button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(context);
                      // TODO: Navigate to premium upgrade page
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Premium upgrade coming soon! 🚀'),
                          backgroundColor: Color(0xFFF59E0B),
                          duration: Duration(seconds: 3),
                        ),
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFF59E0B),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 0,
                    ),
                    child: const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.rocket_launch, size: 24),
                        SizedBox(width: 12),
                        Text(
                          'Upgrade to Premium',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                
                // Maybe later button
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text(
                    'Maybe Later',
                    style: TextStyle(
                      fontSize: 16,
                      color: Color(0xFF6B7280),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  /// Build a benefit row for the premium dialog
  Widget _buildBenefit(String icon, String text) {
    return Row(
      children: [
        Text(
          icon,
          style: const TextStyle(fontSize: 20),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w500,
              color: Color(0xFF1F2937),
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _generateMealPlan() async {
    print('🟢 [MEAL PLAN GENERATOR] _generateMealPlan called');
    
    if (!_formKey.currentState!.validate()) {
      print('⚠️ [MEAL PLAN GENERATOR] Form validation failed');
      return;
    }
    
    print('✅ [MEAL PLAN GENERATOR] Form validated');
    setState(() => _isGenerating = true);
    _startLoadingMessages();
    
    try {
      print('🟢 [MEAL PLAN GENERATOR] Getting ApiService from context...');
      final apiService = context.read<ApiService>();
      print('✅ [MEAL PLAN GENERATOR] Got ApiService');
      
      print('🟢 [MEAL PLAN GENERATOR] Creating MealPlanningApiService...');
      final mealPlanningApi = MealPlanningApiService(apiService);
      print('✅ [MEAL PLAN GENERATOR] Created MealPlanningApiService');
      
      // Get start of current week (Monday)
      final now = DateTime.now();
      final monday = now.subtract(Duration(days: now.weekday - 1));
      final weekStartDate = DateTime(monday.year, monday.month, monday.day).toIso8601String().split('T')[0];
      
      print('🟢 [MEAL PLAN GENERATOR] Calling generateMealPlan API...');
      print('   Week Start: $weekStartDate');
      print('   Dietary Prefs: $_selectedDietaryPreferences');
      print('   Calories: $_dailyCalories');
      print('   Protein: $_dailyProtein');
      print('   People: $_numPeople');
      print('   Prep Time: $_prepTimePreference');
      
      // Generate meal plan
      final plan = await mealPlanningApi.generateMealPlan(
        weekStartDate: weekStartDate,
        dietaryPreferences: _selectedDietaryPreferences.isNotEmpty 
            ? _selectedDietaryPreferences 
            : null,
        dailyCalorieTarget: _dailyCalories,
        dailyProteinTarget: _dailyProtein,
        numPeople: _numPeople,
        prepTimePreference: _prepTimePreference,
      );
      
      print('✅ [MEAL PLAN GENERATOR] API call successful! Plan ID: ${plan['id']}');
      
      if (mounted) {
        _stopLoadingMessages();
        setState(() => _isGenerating = false);
        
        // Reload plan count to update button
        await _loadPlanCount();
        
        // Show success message with Yuvi
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(AppConstants.aiPlanReady),  // "Yuvi generated your plan! 🎉"
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 2),
          ),
        );
        
        // Navigate back and refresh
        Navigator.pop(context, true); // true = refresh needed
      }
    } catch (e, stackTrace) {
      print('❌ [MEAL PLAN GENERATOR] Error: $e');
      print('❌ [MEAL PLAN GENERATOR] Stack trace: $stackTrace');
      
      if (mounted) {
        _stopLoadingMessages();
        setState(() => _isGenerating = false);
        
        // Check if this is a free tier limit error (403)
        final errorString = e.toString().toLowerCase();
        if (errorString.contains('403') || errorString.contains('limit reached') || errorString.contains('maximum')) {
          _showPremiumUpgradeDialog();
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to generate meal plan: $e'),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 5),
            ),
          );
        }
      }
    }
  }
}

