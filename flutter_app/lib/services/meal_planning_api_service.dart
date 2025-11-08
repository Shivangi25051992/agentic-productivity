import 'api_service.dart';

/// Meal Planning API Service
/// Handles all meal planning-related API calls
class MealPlanningApiService {
  final ApiService _api;

  MealPlanningApiService(this._api);

  // ========================================================================
  // RECIPES
  // ========================================================================

  /// Create a new recipe
  Future<Map<String, dynamic>> createRecipe(Map<String, dynamic> recipe) async {
    try {
      final response = await _api.post('/meal-planning/recipes', recipe);
      print('✅ Created recipe: ${response['id']}');
      return response;
    } catch (e) {
      print('❌ Error creating recipe: $e');
      rethrow;
    }
  }

  /// Get recipe by ID
  Future<Map<String, dynamic>> getRecipe(String recipeId) async {
    try {
      return await _api.get('/meal-planning/recipes/$recipeId');
    } catch (e) {
      print('❌ Error getting recipe: $e');
      rethrow;
    }
  }

  /// Search recipes
  Future<List<Map<String, dynamic>>> searchRecipes({
    String? query,
    String? category,
    String? cuisine,
    int? maxPrepTime,
    int? maxCalories,
    int? minProtein,
    List<String>? tags,
    int limit = 10,
  }) async {
    try {
      final response = await _api.post('/meal-planning/recipes/search', {
        'query': query,
        'category': category,
        'cuisine': cuisine,
        'max_prep_time': maxPrepTime,
        'max_calories': maxCalories,
        'min_protein': minProtein,
        'tags': tags,
        'limit': limit,
      });
      
      // Handle both direct list and wrapped response
      if (response is List) {
        final list = response as List;
        return list.map((e) => e as Map<String, dynamic>).toList();
      } else if (response is Map && response.containsKey('data')) {
        final data = response['data'];
        if (data is List) {
          return data.map((e) => e as Map<String, dynamic>).toList();
        }
      }
      return [];
    } catch (e) {
      print('❌ Error searching recipes: $e');
      return [];
    }
  }

  // ========================================================================
  // MEAL PLANS
  // ========================================================================

  /// Generate a meal plan with AI
  Future<Map<String, dynamic>> generateMealPlan({
    required String weekStartDate,
    List<String>? dietaryPreferences,
    int? dailyCalorieTarget,
    int? dailyProteinTarget,
    int numPeople = 1,
    String? prepTimePreference,
  }) async {
    print('🟡 [MEAL PLANNING API SERVICE] generateMealPlan called');
    print('   week_start_date: $weekStartDate');
    print('   dietary_preferences: $dietaryPreferences');
    print('   daily_calorie_target: $dailyCalorieTarget');
    print('   daily_protein_target: $dailyProteinTarget');
    print('   num_people: $numPeople');
    print('   prep_time_preference: $prepTimePreference');
    
    try {
      print('🟡 [MEAL PLANNING API SERVICE] Calling _api.post...');
      final response = await _api.post('/meal-planning/plans/generate', {
        'week_start_date': weekStartDate,
        'dietary_preferences': dietaryPreferences ?? [], // ✅ Send empty list instead of null
        'daily_calorie_target': dailyCalorieTarget,
        'daily_protein_target': dailyProteinTarget,
        'num_people': numPeople,
        'prep_time_preference': prepTimePreference,
      });
      print('✅ [MEAL PLANNING API SERVICE] Generated meal plan: ${response['id']}');
      return response;
    } catch (e, stackTrace) {
      print('❌ [MEAL PLANNING API SERVICE] Error generating meal plan: $e');
      print('❌ [MEAL PLANNING API SERVICE] Stack trace: $stackTrace');
      rethrow;
    }
  }

  /// Get user's meal plans
  Future<List<Map<String, dynamic>>> getMealPlans({
    int limit = 10,
    bool activeOnly = true,
  }) async {
    try {
      print('🔍 [API] Calling getMealPlans: limit=$limit, activeOnly=$activeOnly');
      final response = await _api.get(
        '/meal-planning/plans?limit=$limit&active_only=$activeOnly',
      );
      
      print('🔍 [API] Response type: ${response.runtimeType}');
      print('🔍 [API] Response: $response');
      
      // Handle both direct list and wrapped response
      if (response is List) {
        print('✅ [API] Response is List, converting...');
        final list = response as List;
        final result = list.map((e) {
          if (e is Map) {
            return Map<String, dynamic>.from(e);
          } else {
            print('⚠️ [API] Item is not a Map: ${e.runtimeType}');
            return <String, dynamic>{};
          }
        }).toList();
        print('✅ [API] Returning ${result.length} plans');
        return result;
      } else if (response is Map && response.containsKey('data')) {
        print('✅ [API] Response is Map with data key');
        final data = response['data'];
        if (data is List) {
          final result = data.map((e) {
            if (e is Map) {
              return Map<String, dynamic>.from(e);
            } else {
              return <String, dynamic>{};
            }
          }).toList();
          print('✅ [API] Returning ${result.length} plans from data');
          return result;
        }
      }
      print('⚠️ [API] Unexpected response format, returning empty list');
      return [];
    } catch (e, stackTrace) {
      print('❌ Error getting meal plans: $e');
      print('Stack trace: $stackTrace');
      return [];
    }
  }

  /// Get current week's meal plan
  Future<Map<String, dynamic>?> getCurrentWeekPlan() async {
    try {
      final response = await _api.get('/meal-planning/plans/current');
      if (response.isEmpty) return null;
      return response;
    } catch (e) {
      print('❌ Error getting current week plan: $e');
      return null;
    }
  }

  /// Get specific meal plan
  Future<Map<String, dynamic>> getMealPlan(String planId) async {
    try {
      return await _api.get('/meal-planning/plans/$planId');
    } catch (e) {
      print('❌ Error getting meal plan: $e');
      rethrow;
    }
  }

  /// Add meal to plan
  Future<Map<String, dynamic>> addMealToPlan({
    required String planId,
    required String day,
    required String mealType,
    required String recipeId,
    int servings = 1,
  }) async {
    try {
      return await _api.post('/meal-planning/plans/$planId/meals', {
        'day': day,
        'meal_type': mealType,
        'recipe_id': recipeId,
        'servings': servings,
      });
    } catch (e) {
      print('❌ Error adding meal to plan: $e');
      rethrow;
    }
  }

  /// Remove meal from plan
  Future<Map<String, dynamic>> removeMealFromPlan({
    required String planId,
    required String day,
    required String mealType,
  }) async {
    try {
      return await _api.delete('/meal-planning/plans/$planId/meals/$day/$mealType');
    } catch (e) {
      print('❌ Error removing meal from plan: $e');
      rethrow;
    }
  }

  /// Get meal plan analytics
  Future<Map<String, dynamic>> getMealPlanAnalytics(String planId) async {
    try {
      return await _api.get('/meal-planning/plans/$planId/analytics');
    } catch (e) {
      print('❌ Error getting meal plan analytics: $e');
      rethrow;
    }
  }

  // ========================================================================
  // SUGGESTIONS
  // ========================================================================

  /// Get daily meal suggestions
  Future<List<Map<String, dynamic>>> getDailySuggestions({
    String? targetDate,
    int remainingCalories = 1500,
    int remainingProtein = 100,
  }) async {
    try {
      final response = await _api.get(
        '/meal-planning/suggestions/daily?'
        'target_date=${targetDate ?? DateTime.now().toIso8601String().split('T')[0]}&'
        'remaining_calories=$remainingCalories&'
        'remaining_protein=$remainingProtein',
      );
      
      // Handle both direct list and wrapped response
      if (response is List) {
        final list = response as List;
        return list.map((e) => e as Map<String, dynamic>).toList();
      } else if (response is Map && response.containsKey('data')) {
        final data = response['data'];
        if (data is List) {
          return data.map((e) => e as Map<String, dynamic>).toList();
        }
      }
      return [];
    } catch (e) {
      print('❌ Error getting daily suggestions: $e');
      return [];
    }
  }

  // ========================================================================
  // GROCERY LISTS
  // ========================================================================

  /// Generate grocery list from meal plan
  Future<Map<String, dynamic>> generateGroceryList(String planId) async {
    try {
      final response = await _api.post('/meal-planning/grocery-lists/generate/$planId', {});
      print('✅ Generated grocery list: ${response['id']}');
      return response;
    } catch (e) {
      print('❌ Error generating grocery list: $e');
      rethrow;
    }
  }

  /// Get grocery list
  Future<Map<String, dynamic>> getGroceryList(String listId) async {
    try {
      return await _api.get('/meal-planning/grocery-lists/$listId');
    } catch (e) {
      print('❌ Error getting grocery list: $e');
      rethrow;
    }
  }

  /// Check/uncheck grocery item
  Future<Map<String, dynamic>> checkGroceryItem({
    required String listId,
    required String itemName,
    bool checked = true,
  }) async {
    try {
      return await _api.put(
        '/meal-planning/grocery-lists/$listId/items/$itemName/check?checked=$checked',
        {},
      );
    } catch (e) {
      print('❌ Error checking grocery item: $e');
      rethrow;
    }
  }
}

