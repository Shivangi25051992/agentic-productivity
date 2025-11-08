import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/api_service.dart';
import '../../services/meal_planning_api_service.dart';
import '../../providers/auth_provider.dart';
import 'meal_plan_generator_screen.dart';
import 'grocery_list_screen.dart';
import 'recipe_detail_screen.dart';

/// Beautiful Meal Planning UI
/// Inspired by: Notion, Mealime, Eat This Much
class MealPlanningTab extends StatefulWidget {
  MealPlanningTab({Key? key}) : super(key: key);

  @override
  State<MealPlanningTab> createState() => _MealPlanningTabState();
}

class _MealPlanningTabState extends State<MealPlanningTab> {
  int _selectedDay = DateTime.now().weekday - 1; // 0 = Monday
  
  final List<String> _days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  final List<String> _fullDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  
  // API Service
  MealPlanningApiService? _mealPlanningApi;
  
  // State
  bool _isLoading = false;
  String? _currentPlanId;
  Map<String, List<Map<String, dynamic>>> _weekMeals = {};
  Map<String, int> _dailyTotals = {}; // calories and protein per day
  
  // Plan selection state (for switching between multiple plans)
  List<Map<String, dynamic>> _allPlans = [];
  String? _selectedPlanId;
  
  // Mock data - fallback if no API
  final Map<String, List<Map<String, dynamic>>> _mockMeals = {
    'Monday': [
      {
        'type': 'Breakfast',
        'name': 'Protein Smoothie Bowl',
        'calories': 350,
        'protein': 30,
        'time': '8:00 AM',
        'icon': Icons.breakfast_dining,
        'color': Color(0xFFF59E0B),
      },
      {
        'type': 'Lunch',
        'name': 'Grilled Chicken Salad',
        'calories': 450,
        'protein': 40,
        'time': '1:00 PM',
        'icon': Icons.lunch_dining,
        'color': Color(0xFF10B981),
      },
      {
        'type': 'Dinner',
        'name': 'Salmon with Vegetables',
        'calories': 550,
        'protein': 45,
        'time': '7:00 PM',
        'icon': Icons.dinner_dining,
        'color': Color(0xFF6366F1),
      },
    ],
  };

  @override
  void initState() {
    super.initState();
    
    // Initialize API service and load meal plan
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeApiService();
    });
  }
  
  void _initializeApiService() {
    try {
      // Get AuthProvider and create ApiService directly
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final apiService = ApiService(authProvider);
      _mealPlanningApi = MealPlanningApiService(apiService);
      _loadCurrentWeekPlan();
    } catch (e) {
      print('⚠️ [MEAL PLANNING] Could not initialize API service: $e');
      // Continue with mock data - this is OK for local development
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  /// Load current week's meal plan from backend
  Future<void> _loadCurrentWeekPlan() async {
    if (_mealPlanningApi == null || !mounted) return;
    
    setState(() {
      _isLoading = true;
      _weekMeals = {}; // ✅ FIX: Clear old data first
      _dailyTotals = {};
      _currentPlanId = null;
    });
    
    try {
      final plan = await _mealPlanningApi!.getCurrentWeekPlan();
      
      if (plan != null && mounted) {
        final parsedMeals = _parseMealPlanData(plan);
        final calculatedTotals = _calculateDailyTotals(plan);
        
        setState(() {
          _currentPlanId = plan['id'] as String?;
          _weekMeals = parsedMeals;
          _dailyTotals = calculatedTotals;
          _isLoading = false;
        });
        
        print('✅ [MEAL PLANNING] Loaded meal plan: $_currentPlanId');
        print('✅ [MEAL PLANNING] Days with meals: ${parsedMeals.keys.toList()}');
        print('✅ [MEAL PLANNING] Total meals: ${parsedMeals.values.fold(0, (sum, list) => sum + list.length)}');
        
        // ✨ NEW: Also load all plans for switching (non-blocking)
        print('🎯 [MEAL PLANNING] About to call _loadAllWeekPlans()...');
        _loadAllWeekPlans();
        print('🎯 [MEAL PLANNING] Called _loadAllWeekPlans()!');
      } else {
        // No plan exists, show empty state
        setState(() {
          _isLoading = false;
          _weekMeals = {};
          _dailyTotals = {};
        });
        print('ℹ️ [MEAL PLANNING] No active meal plan found');
      }
    } catch (e) {
      print('❌ [MEAL PLANNING] Error loading meal plan: $e');
      setState(() {
        _isLoading = false;
        _weekMeals = {};
        _dailyTotals = {};
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Could not load meal plan: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// Load ALL meal plans for current week (for plan switching)
  Future<void> _loadAllWeekPlans() async {
    print('🔍 [PLAN SELECTION] _loadAllWeekPlans called');
    
    if (_mealPlanningApi == null) {
      print('⚠️ [PLAN SELECTION] API is null, skipping');
      return;
    }
    
    if (!mounted) {
      print('⚠️ [PLAN SELECTION] Widget not mounted, skipping');
      return;
    }
    
    try {
      print('📡 [PLAN SELECTION] Fetching all plans from API...');
      // Get all plans (not just active)
      final plans = await _mealPlanningApi!.getMealPlans(
        limit: 10,
        activeOnly: false,
      );
      
      print('📡 [PLAN SELECTION] API returned ${plans.length} plans');
      
      if (!mounted) return;
      
      // Filter to current week only
      final now = DateTime.now();
      final monday = now.subtract(Duration(days: now.weekday - 1));
      final weekStart = DateTime(monday.year, monday.month, monday.day);
      
      print('📅 [PLAN SELECTION] Current week start: $weekStart');
      
      final currentWeekPlans = plans.where((plan) {
        try {
          final planStart = DateTime.parse(plan['week_start_date'] as String);
          print('   📋 Plan ${plan['id']}: week_start=$planStart');
          final matches = planStart.year == weekStart.year &&
                 planStart.month == weekStart.month &&
                 planStart.day == weekStart.day;
          print('      Match: $matches');
          return matches;
        } catch (e) {
          print('   ❌ Error parsing plan date: $e');
          return false;
        }
      }).toList();
      
      print('✅ [PLAN SELECTION] Filtered to ${currentWeekPlans.length} plans for current week');
      
      setState(() {
        _allPlans = currentWeekPlans;
        
        // Set selected plan (prefer active, or first one)
        if (currentWeekPlans.isNotEmpty) {
          final activePlan = currentWeekPlans.firstWhere(
            (p) => p['is_active'] == true,
            orElse: () => currentWeekPlans.first,
          );
          _selectedPlanId = activePlan['id'] as String?;
          print('✅ [PLAN SELECTION] Selected plan: $_selectedPlanId');
        }
      });
      
      print('📋 [PLAN SELECTION] Final: ${_allPlans.length} plans loaded');
    } catch (e) {
      print('❌ [PLAN SELECTION] Error loading all plans: $e');
      print('   Stack trace: ${StackTrace.current}');
      // Fallback: Keep existing behavior
      _allPlans = [];
    }
  }

  /// Helper: Get day name from date string
  String _getDayNameFromDate(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      final dayIndex = date.weekday - 1; // Monday = 0
      return _fullDays[dayIndex];
    } catch (e) {
      print('❌ [MEAL PLANNING] Error parsing date: $dateStr');
      return 'Monday'; // Default fallback
    }
  }

  /// Parse meal plan data from API response
  Map<String, List<Map<String, dynamic>>> _parseMealPlanData(Map<String, dynamic> plan) {
    final Map<String, List<Map<String, dynamic>>> parsed = {};
    
    try {
      print('🔍 [PARSE] Starting _parseMealPlanData...');
      
      // Backend returns meals as a List, not a Map
      final mealsData = plan['meals'];
      print('🔍 [PARSE] meals data type: ${mealsData.runtimeType}');
      print('🔍 [PARSE] meals count: ${mealsData is List ? mealsData.length : 'N/A'}');
      
      // If meals is empty or null, return empty map
      if (mealsData == null || (mealsData is List && mealsData.isEmpty)) {
        print('❌ [PARSE] No meals in plan');
        return {};
      }
      
      // If meals is a List (new format), convert to Map by day
      if (mealsData is List) {
        print('🔍 [PARSE] Processing ${mealsData.length} meals...');
        
        for (int i = 0; i < mealsData.length; i++) {
          final meal = mealsData[i];
          
          if (meal is! Map<String, dynamic>) {
            print('⚠️ [PARSE] Meal $i is not a Map, skipping');
            continue;
          }
          
          // Try to get day name from 'day' field first, then from 'date' field
          String? dayName;
          
          // Check if meal has 'day' field (e.g., "monday", "tuesday")
          final dayField = meal['day'] as String?;
          print('🔍 [PARSE] Meal $i: day field = "$dayField"');
          
          if (dayField != null) {
            dayName = _capitalizeFirst(dayField);
            print('🔍 [PARSE] Meal $i: capitalized day = "$dayName"');
          } else {
            // Fallback to 'date' field
            final date = meal['date'] as String?;
            if (date != null) {
              dayName = _getDayNameFromDate(date);
              print('🔍 [PARSE] Meal $i: day from date = "$dayName"');
            }
          }
          
          // Skip if we couldn't determine the day
          if (dayName == null) {
            print('⚠️ [PARSE] Meal $i: No day or date, skipping: ${meal['recipe_name']}');
            continue;
          }
          
          final mealType = meal['meal_type'] as String? ?? 'breakfast';
          final recipeName = meal['recipe_name'] as String? ?? 'Unnamed Meal';
          
          print('✅ [PARSE] Meal $i: Adding "$recipeName" to $dayName');
          
          parsed.putIfAbsent(dayName, () => []);
          parsed[dayName]!.add({
            'type': _capitalizeFirst(mealType),
            'name': recipeName,
            'calories': meal['calories'] as int? ?? 0,
            'protein': meal['protein'] as int? ?? 0,
            'time': '12:00 PM', // Default time
            'icon': _getMealIcon(mealType),
            'color': _getMealColor(mealType),
            'recipe_id': meal['recipe_id'] as String?,
            'servings': meal['servings'] as int? ?? 1,
            'date': meal['date'] as String?,
          });
        }
        
        print('✅ [PARSE] FINAL RESULT: ${parsed.length} days with meals');
        for (final day in parsed.keys) {
          print('   ✅ $day: ${parsed[day]!.length} meals');
        }
        
        return parsed;
      }
      
      // If meals is a Map (old format), use it directly
      final meals = mealsData as Map<String, dynamic>?;
      if (meals == null) return {};
      
      for (final day in _fullDays) {
        final dayMeals = meals[day] as Map<String, dynamic>?;
        if (dayMeals == null) continue;
        
        final List<Map<String, dynamic>> parsedDayMeals = [];
        
        // Parse each meal type (breakfast, lunch, dinner, snacks)
        for (final mealType in ['breakfast', 'lunch', 'dinner', 'snacks']) {
          final meal = dayMeals[mealType] as Map<String, dynamic>?;
          if (meal == null) continue;
          
          final recipe = meal['recipe'] as Map<String, dynamic>?;
          if (recipe == null) continue;
          
          parsedDayMeals.add({
            'type': _capitalizeFirst(mealType),
            'name': recipe['name'] as String? ?? 'Unnamed Meal',
            'calories': recipe['calories'] as int? ?? 0,
            'protein': recipe['protein'] as int? ?? 0,
            'time': meal['scheduled_time'] as String? ?? '12:00 PM',
            'icon': _getMealIcon(mealType),
            'color': _getMealColor(mealType),
            'recipe_id': recipe['id'] as String?,
            'servings': meal['servings'] as int? ?? 1,
          });
        }
        
        if (parsedDayMeals.isNotEmpty) {
          parsed[day] = parsedDayMeals;
        }
      }
    } catch (e) {
      print('❌ [MEAL PLANNING] Error parsing meal plan data: $e');
    }
    
    return parsed;
  }

  /// Calculate daily totals for calories and protein
  Map<String, int> _calculateDailyTotals(Map<String, dynamic> plan) {
    final Map<String, int> totals = {};
    
    try {
      final mealsData = plan['meals'];
      
      // If meals is a List (new format)
      if (mealsData is List) {
        // Group by day and calculate totals
        for (final day in _fullDays) {
          int dayCalories = 0;
          int dayProtein = 0;
          int dayFat = 0;
          
          for (final meal in mealsData) {
            if (meal is! Map<String, dynamic>) continue;
            
            // Try to get day name from 'day' field first, then from 'date' field
            String? dayName;
            
            final dayField = meal['day'] as String?;
            if (dayField != null) {
              dayName = _capitalizeFirst(dayField);
            } else {
              final date = meal['date'] as String?;
              if (date != null) {
                dayName = _getDayNameFromDate(date);
              }
            }
            
            if (dayName != day) continue;
            
            // Use calories, protein, and fat directly from meal (backend enriches them)
            dayCalories += (meal['calories'] as int? ?? 0);
            dayProtein += (meal['protein'] as int? ?? 0);
            dayFat += ((meal['fat_g'] as num?)?.toInt() ?? 0);
          }
          
          totals['${day}_calories'] = dayCalories;
          totals['${day}_protein'] = dayProtein;
          totals['${day}_fat'] = dayFat;
        }
        return totals;
      }
      
      // If meals is a Map (old format)
      final meals = mealsData as Map<String, dynamic>?;
      if (meals == null) return {};
      
      for (final day in _fullDays) {
        final dayMeals = meals[day] as Map<String, dynamic>?;
        if (dayMeals == null) continue;
        
        int dayCalories = 0;
        int dayProtein = 0;
        int dayFat = 0;
        
        for (final mealType in ['breakfast', 'lunch', 'dinner', 'snacks']) {
          final meal = dayMeals[mealType] as Map<String, dynamic>?;
          if (meal == null) continue;
          
          final recipe = meal['recipe'] as Map<String, dynamic>?;
          if (recipe == null) continue;
          
          dayCalories += (recipe['calories'] as int? ?? 0);
          dayProtein += (recipe['protein'] as int? ?? 0);
          dayFat += ((recipe['fat_g'] as num?)?.toInt() ?? 0);
        }
        
        totals['${day}_calories'] = dayCalories;
        totals['${day}_protein'] = dayProtein;
        totals['${day}_fat'] = dayFat;
      }
    } catch (e) {
      print('❌ [MEAL PLANNING] Error calculating daily totals: $e');
    }
    
    return totals;
  }

  /// Helper: Capitalize first letter
  String _capitalizeFirst(String text) {
    if (text.isEmpty) return text;
    return text[0].toUpperCase() + text.substring(1);
  }

  /// Helper: Get meal icon
  IconData _getMealIcon(String mealType) {
    switch (mealType.toLowerCase()) {
      case 'breakfast':
        return Icons.breakfast_dining;
      case 'lunch':
        return Icons.lunch_dining;
      case 'dinner':
        return Icons.dinner_dining;
      case 'snacks':
        return Icons.cookie;
      default:
        return Icons.restaurant;
    }
  }

  /// Helper: Get meal color
  Color _getMealColor(String mealType) {
    switch (mealType.toLowerCase()) {
      case 'breakfast':
        return const Color(0xFFF59E0B);
      case 'lunch':
        return const Color(0xFF10B981);
      case 'dinner':
        return const Color(0xFF6366F1);
      case 'snacks':
        return const Color(0xFFEC4899);
      default:
        return const Color(0xFF6B7280);
    }
  }

  /// Show AI meal plan generator dialog
  Future<void> _showGeneratePlanDialog() async {
    print('🔵 [MEAL PLANNING TAB] _showGeneratePlanDialog called');
    try {
      print('🔵 [MEAL PLANNING TAB] Getting AuthProvider...');
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      print('✅ [MEAL PLANNING TAB] Got AuthProvider: ${authProvider.isAuthenticated}');
      
      print('🔵 [MEAL PLANNING TAB] Creating ApiService...');
      final apiService = ApiService(authProvider);
      print('✅ [MEAL PLANNING TAB] Created ApiService');
      
      print('🔵 [MEAL PLANNING TAB] Navigating to MealPlanGeneratorScreen...');
      final result = await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) {
            print('🔵 [MEAL PLANNING TAB] Building MealPlanGeneratorScreen with Provider...');
            return Provider<ApiService>.value(
              value: apiService,
              child: const MealPlanGeneratorScreen(),
            );
          },
        ),
      );
      
      print('🔵 [MEAL PLANNING TAB] Navigation returned with result: $result');
      
      // If result is true, refresh the meal plan
      if (result == true && mounted) {
        print('✅ [MEAL PLANNING TAB] Refreshing meal plan...');
        // Force reload and clear cache
        setState(() {
          _weekMeals = {};
          _dailyTotals = {};
          _currentPlanId = null;
        });
        await _loadCurrentWeekPlan();
        
        // Show success feedback
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('✅ Meal plan loaded! Swipe through days to see all meals.'),
              backgroundColor: Colors.green,
              duration: Duration(seconds: 3),
            ),
          );
        }
      }
    } catch (e, stackTrace) {
      print('❌ [MEAL PLANNING TAB] Error showing generator: $e');
      print('❌ [MEAL PLANNING TAB] Stack trace: $stackTrace');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Could not open meal plan generator: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  /// Show grocery list screen
  void _showGroceryList() {
    if (_currentPlanId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please generate a meal plan first'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }
    
    try {
      // Get AuthProvider and create ApiService
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final apiService = ApiService(authProvider);
      
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => Provider<ApiService>.value(
            value: apiService,
            child: GroceryListScreen(planId: _currentPlanId!),
          ),
        ),
      );
    } catch (e) {
      print('❌ [MEAL PLANNING] Error showing grocery list: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Could not open grocery list: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ✨ NEW: Plan Selector (only shows if multiple plans)
            _buildPlanSelector(),
            
            // Week Selector
            _buildWeekSelector(),
            
            const SizedBox(height: 24),
            
            // Daily Summary Card
            _buildDailySummaryCard(),
            
            const SizedBox(height: 24),
            
            // Meals List
            _buildMealsList(),
            
            const SizedBox(height: 24),
            
            // Quick Actions
            _buildQuickActions(),
          ],
        ),
      ),
    );
  }

  /// Plan selector widget (only shows if multiple plans exist)
  Widget _buildPlanSelector() {
    // Hide if only 1 or 0 plans (zero regression!)
    if (_allPlans.length <= 1) {
      return SizedBox.shrink();
    }
    
    final selectedPlan = _allPlans.firstWhere(
      (p) => p['id'] == _selectedPlanId,
      orElse: () => _allPlans.first,
    );
    
    final dietaryPrefs = (selectedPlan['dietary_preferences'] as List?)
        ?.map((p) => p.toString().replaceAll('DietaryTag.', '').replaceAll('_', ' '))
        .join(', ') ?? 'Balanced';
    
    final mealCount = (selectedPlan['meals'] as List?)?.length ?? 0;
    
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Color(0xFFE5E7EB)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: Color(0xFF6366F1).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              Icons.restaurant_menu,
              color: Color(0xFF6366F1),
              size: 20,
            ),
          ),
          SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  dietaryPrefs,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF1F2937),
                  ),
                ),
                SizedBox(height: 2),
                Text(
                  '${_allPlans.length} plans • $mealCount meals',
                  style: TextStyle(
                    fontSize: 12,
                    color: Color(0xFF6B7280),
                  ),
                ),
              ],
            ),
          ),
          TextButton(
            onPressed: _showPlanSwitcher,
            style: TextButton.styleFrom(
              foregroundColor: Color(0xFF6366F1),
              padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Switch',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                SizedBox(width: 4),
                Icon(Icons.swap_horiz, size: 16),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Show bottom sheet to switch between plans
  void _showPlanSwitcher() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        minChildSize: 0.4,
        maxChildSize: 0.9,
        expand: false,
        builder: (context, scrollController) => Container(
          padding: EdgeInsets.fromLTRB(24, 24, 24, 0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  Icon(Icons.restaurant_menu, color: Color(0xFF6366F1)),
                  SizedBox(width: 12),
                  Text(
                    'Choose Your Meal Plan',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1F2937),
                    ),
                  ),
                ],
              ),
              SizedBox(height: 8),
              Text(
                'You have ${_allPlans.length} plans for this week',
                style: TextStyle(
                  fontSize: 14,
                  color: Color(0xFF6B7280),
                ),
              ),
              SizedBox(height: 16),
              
              // Scrollable list of plans
              Expanded(
                child: ListView.builder(
                  controller: scrollController,
                  itemCount: _allPlans.length,
                  itemBuilder: (context, index) {
                    final plan = _allPlans[index];
                    return _buildPlanCard(plan, index + 1);
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Build a plan card for the switcher
  Widget _buildPlanCard(Map<String, dynamic> plan, int planNumber) {
    final isSelected = plan['id'] == _selectedPlanId;
    final dietaryPrefs = (plan['dietary_preferences'] as List?)
        ?.map((p) => p.toString().replaceAll('DietaryTag.', '').replaceAll('_', ' '))
        .join(', ') ?? 'Balanced';
    final mealCount = (plan['meals'] as List?)?.length ?? 0;
    
    return GestureDetector(
      onTap: () {
        _switchToPlan(plan['id'] as String);
        Navigator.pop(context);
      },
      child: Container(
        margin: EdgeInsets.only(bottom: 8),
        padding: EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected ? Color(0xFF6366F1).withOpacity(0.1) : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? Color(0xFF6366F1) : Color(0xFFE5E7EB),
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: Color(0xFF6366F1).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                Icons.restaurant_menu,
                color: Color(0xFF6366F1),
              ),
            ),
            SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        'Plan $planNumber',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF1F2937),
                        ),
                      ),
                      if (isSelected) ...[
                        SizedBox(width: 8),
                        Container(
                          padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: Color(0xFF10B981),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            'Active',
                            style: TextStyle(
                              fontSize: 10,
                              color: Colors.white,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                  SizedBox(height: 4),
                  Text(
                    dietaryPrefs,
                    style: TextStyle(
                      fontSize: 13,
                      color: Color(0xFF6B7280),
                    ),
                  ),
                  Text(
                    '$mealCount meals',
                    style: TextStyle(
                      fontSize: 12,
                      color: Color(0xFF9CA3AF),
                    ),
                  ),
                ],
              ),
            ),
            if (isSelected)
              Icon(
                Icons.check_circle,
                color: Color(0xFF10B981),
                size: 24,
              ),
          ],
        ),
      ),
    );
  }

  /// Switch to a different plan
  void _switchToPlan(String planId) {
    print('🔄 [PLAN SELECTION] Switching to plan: $planId');
    
    final plan = _allPlans.firstWhere(
      (p) => p['id'] == planId,
      orElse: () => _allPlans.first,
    );
    
    print('🔄 [PLAN SELECTION] Found plan: ${plan['id']}');
    print('🔄 [PLAN SELECTION] Plan has ${plan['meals']?.length ?? 0} meals');
    
    final parsedMeals = _parseMealPlanData(plan);
    final calculatedTotals = _calculateDailyTotals(plan);
    
    print('🔄 [PLAN SELECTION] Parsed meals for days: ${parsedMeals.keys.toList()}');
    print('🔄 [PLAN SELECTION] Total meals: ${parsedMeals.values.fold(0, (sum, list) => sum + list.length)}');
    
    setState(() {
      _selectedPlanId = planId;
      _currentPlanId = planId;
      _weekMeals = parsedMeals;
      _dailyTotals = calculatedTotals;
    });
    
    print('✅ [PLAN SELECTION] Switched to plan: $planId');
    print('✅ [PLAN SELECTION] Current state: $_currentPlanId, meals: ${_weekMeals.keys.length} days');
  }

  Widget _buildWeekSelector() {
    return Container(
      height: 90,
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
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
        itemCount: _days.length,
        itemBuilder: (context, index) {
          final isSelected = _selectedDay == index;
          final isToday = DateTime.now().weekday - 1 == index;
          
          return GestureDetector(
            onTap: () {
              setState(() {
                _selectedDay = index;
              });
            },
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              width: 70,
              margin: const EdgeInsets.symmetric(horizontal: 4),
              decoration: BoxDecoration(
                gradient: isSelected
                    ? const LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
                      )
                    : null,
                color: isSelected ? null : const Color(0xFFF9FAFB),
                borderRadius: BorderRadius.circular(16),
                border: isToday && !isSelected
                    ? Border.all(color: const Color(0xFF6366F1), width: 2)
                    : null,
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    _days[index],
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: isSelected
                          ? Colors.white
                          : isToday
                              ? const Color(0xFF6366F1)
                              : const Color(0xFF6B7280),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    width: 6,
                    height: 6,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: isSelected
                          ? Colors.white
                          : isToday
                              ? const Color(0xFF6366F1)
                              : Colors.transparent,
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildDailySummaryCard() {
    // Get data from loaded plan or use defaults
    final selectedDayName = _fullDays[_selectedDay];
    final totalCalories = _dailyTotals['${selectedDayName}_calories'] ?? 0;
    final totalProtein = _dailyTotals['${selectedDayName}_protein'] ?? 0;
    final totalFat = _dailyTotals['${selectedDayName}_fat'] ?? 0;
    final targetCalories = 2000; // TODO: Get from user profile
    final targetProtein = 150; // TODO: Get from user profile
    final targetFat = 65; // TODO: Get from user profile (~30% of 2000 cal)
    
    final dayMeals = _weekMeals[selectedDayName] ?? [];
    final mealCount = dayMeals.length;
    
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                _fullDays[_selectedDay],
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '$mealCount meal${mealCount != 1 ? 's' : ''}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(
                child: _buildNutrientProgress(
                  'Calories',
                  totalCalories,
                  targetCalories,
                  Icons.local_fire_department,
                  const Color(0xFFF59E0B),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildNutrientProgress(
                  'Protein',
                  totalProtein,
                  targetProtein,
                  Icons.fitness_center,
                  const Color(0xFF10B981),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildNutrientProgress(
                  'Fat',
                  totalFat,
                  targetFat,
                  Icons.water_drop,
                  const Color(0xFF8B5CF6),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildNutrientProgress(
    String label,
    int current,
    int target,
    IconData icon,
    Color color,
  ) {
    final progress = (current / target).clamp(0.0, 1.0);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: Colors.white, size: 16),
            const SizedBox(width: 6),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          '$current / $target',
          style: const TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: progress,
            backgroundColor: Colors.white.withOpacity(0.2),
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 6,
          ),
        ),
      ],
    );
  }

  Widget _buildMealsList() {
    // Always use loaded data, never fall back to mock
    final selectedDayName = _fullDays[_selectedDay];
    final dayMeals = _weekMeals[selectedDayName] ?? [];
    
    print('🔍 [MEAL PLANNING] Building meals for: $selectedDayName');
    print('🔍 [MEAL PLANNING] Found ${dayMeals.length} meals');
    
    if (_isLoading) {
      return _buildLoadingState();
    }
    
    if (dayMeals.isEmpty) {
      return _buildEmptyState();
    }
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Today\'s Meals',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Color(0xFF1F2937),
          ),
        ),
        const SizedBox(height: 16),
        ...dayMeals.map((meal) => _buildMealCard(meal)),
      ],
    );
  }

  Widget _buildMealCard(Map<String, dynamic> meal) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
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
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(20),
          onTap: () {
            // Navigate to recipe detail
            final recipeId = meal['recipe_id'] as String?;
            if (recipeId != null) {
              try {
                // Get AuthProvider and create ApiService
                final authProvider = Provider.of<AuthProvider>(context, listen: false);
                final apiService = ApiService(authProvider);
                
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => Provider<ApiService>.value(
                      value: apiService,
                      child: RecipeDetailScreen(
                        recipeId: recipeId,
                        recipeName: meal['name'] as String?,
                      ),
                    ),
                  ),
                );
              } catch (e) {
                print('❌ [MEAL PLANNING] Error showing recipe: $e');
              }
            }
          },
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                // Icon
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    color: (meal['color'] as Color).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Icon(
                    meal['icon'] as IconData,
                    color: meal['color'] as Color,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 16),
                
                // Content
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        meal['type'] as String,
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: meal['color'] as Color,
                          letterSpacing: 0.5,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        meal['name'] as String,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1F2937),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          _buildMealStat(
                            Icons.local_fire_department,
                            '${meal['calories']} cal',
                            const Color(0xFFF59E0B),
                          ),
                          const SizedBox(width: 16),
                          _buildMealStat(
                            Icons.fitness_center,
                            '${meal['protein']}g',
                            const Color(0xFF10B981),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                
                // Time
                Column(
                  children: [
                    const Icon(
                      Icons.access_time,
                      size: 16,
                      color: Color(0xFF9CA3AF),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      meal['time'] as String,
                      style: const TextStyle(
                        fontSize: 12,
                        color: Color(0xFF6B7280),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMealStat(IconData icon, String text, Color color) {
    return Row(
      children: [
        Icon(icon, size: 14, color: color),
        const SizedBox(width: 4),
        Text(
          text,
          style: const TextStyle(
            fontSize: 12,
            color: Color(0xFF6B7280),
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildLoadingState() {
    return Container(
      padding: const EdgeInsets.all(40),
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
      child: const Center(
        child: Column(
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text(
              'Loading meal plan...',
              style: TextStyle(
                fontSize: 14,
                color: Color(0xFF6B7280),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(40),
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
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: const Color(0xFF6366F1).withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.restaurant_menu,
              size: 40,
              color: Color(0xFF6366F1),
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'No meals planned',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937),
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Generate a meal plan with AI to get started',
            style: TextStyle(
              fontSize: 14,
              color: Color(0xFF6B7280),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Quick Actions',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Color(0xFF1F2937),
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildActionButton(
                'Generate Plan',
                Icons.auto_awesome,
                const Color(0xFF6366F1),
                _showGeneratePlanDialog,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildActionButton(
                'Grocery List',
                Icons.shopping_cart,
                const Color(0xFF10B981),
                _showGroceryList,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildActionButton(
    String label,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.3), width: 2),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              label,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

