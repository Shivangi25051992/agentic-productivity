import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/api_service.dart';
import '../../services/meal_planning_api_service.dart';

/// Grocery List Screen
/// Smart categorized grocery list with check-off functionality
class GroceryListScreen extends StatefulWidget {
  final String planId;
  
  const GroceryListScreen({
    Key? key,
    required this.planId,
  }) : super(key: key);

  @override
  State<GroceryListScreen> createState() => _GroceryListScreenState();
}

class _GroceryListScreenState extends State<GroceryListScreen> {
  bool _isLoading = true;
  bool _isGenerating = false;
  String? _listId;
  Map<String, List<Map<String, dynamic>>> _categorizedItems = {};
  Set<String> _checkedItems = {};
  
  @override
  void initState() {
    super.initState();
    _loadOrGenerateGroceryList();
  }

  Future<void> _loadOrGenerateGroceryList() async {
    setState(() => _isLoading = true);
    
    try {
      final apiService = context.read<ApiService>();
      final mealPlanningApi = MealPlanningApiService(apiService);
      
      // Generate grocery list from meal plan
      setState(() => _isGenerating = true);
      final list = await mealPlanningApi.generateGroceryList(widget.planId);
      setState(() => _isGenerating = false);
      
      if (mounted) {
        setState(() {
          _listId = list['id'] as String?;
          _categorizedItems = _parseGroceryList(list);
          _isLoading = false;
        });
        
        print('✅ [GROCERY LIST] Loaded list: $_listId');
      }
    } catch (e) {
      print('❌ [GROCERY LIST] Error: $e');
      
      if (mounted) {
        setState(() {
          _isLoading = false;
          _isGenerating = false;
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to load grocery list: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Map<String, List<Map<String, dynamic>>> _parseGroceryList(Map<String, dynamic> list) {
    final Map<String, List<Map<String, dynamic>>> categorized = {};
    
    try {
      final items = list['items'] as Map<String, dynamic>?;
      if (items == null) return {};
      
      items.forEach((category, categoryItems) {
        if (categoryItems is List) {
          categorized[category] = List<Map<String, dynamic>>.from(
            categoryItems.map((item) => {
              'name': item['name'] as String? ?? '',
              'quantity': item['quantity'] as String? ?? '',
              'unit': item['unit'] as String? ?? '',
              'checked': item['checked'] as bool? ?? false,
            }),
          );
          
          // Track checked items
          for (final item in categorized[category]!) {
            if (item['checked'] == true) {
              _checkedItems.add(item['name'] as String);
            }
          }
        }
      });
    } catch (e) {
      print('❌ [GROCERY LIST] Error parsing list: $e');
    }
    
    return categorized;
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
          'Grocery List',
          style: TextStyle(
            color: Color(0xFF1F2937),
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.share, color: Color(0xFF6366F1)),
            onPressed: _shareList,
          ),
        ],
      ),
      body: _isLoading
          ? _buildLoadingState()
          : _categorizedItems.isEmpty
              ? _buildEmptyState()
              : _buildGroceryList(),
    );
  }

  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 16),
          Text(
            _isGenerating ? 'Generating grocery list...' : 'Loading...',
            style: const TextStyle(
              fontSize: 16,
              color: Color(0xFF6B7280),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: const Color(0xFF10B981).withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.shopping_cart,
                size: 50,
                color: Color(0xFF10B981),
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'No items in list',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1F2937),
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Generate a meal plan to create a grocery list',
              style: TextStyle(
                fontSize: 14,
                color: Color(0xFF6B7280),
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGroceryList() {
    final totalItems = _categorizedItems.values.fold<int>(
      0, 
      (sum, items) => sum + items.length,
    );
    final checkedCount = _checkedItems.length;
    final progress = totalItems > 0 ? checkedCount / totalItems : 0.0;
    
    return Column(
      children: [
        // Progress Card
        _buildProgressCard(checkedCount, totalItems, progress),
        
        // Categorized Items
        Expanded(
          child: ListView.builder(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.all(24),
            itemCount: _categorizedItems.length,
            itemBuilder: (context, index) {
              final category = _categorizedItems.keys.elementAt(index);
              final items = _categorizedItems[category]!;
              return _buildCategorySection(category, items);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildProgressCard(int checked, int total, double progress) {
    return Container(
      margin: const EdgeInsets.all(24),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF10B981), Color(0xFF059669)],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF10B981).withOpacity(0.3),
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
              const Text(
                'Shopping Progress',
                style: TextStyle(
                  fontSize: 18,
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
                  '$checked / $total',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: progress,
              backgroundColor: Colors.white.withOpacity(0.2),
              valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
              minHeight: 8,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            progress >= 1.0 
                ? '🎉 All done! Ready to cook!' 
                : '${(progress * 100).toInt()}% complete',
            style: const TextStyle(
              fontSize: 14,
              color: Colors.white70,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategorySection(String category, List<Map<String, dynamic>> items) {
    final categoryCheckedCount = items.where((item) => 
      _checkedItems.contains(item['name'] as String)
    ).length;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 24),
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
          // Category Header
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: _getCategoryColor(category).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(
                        _getCategoryIcon(category),
                        color: _getCategoryColor(category),
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      _capitalizeCategory(category),
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1F2937),
                      ),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getCategoryColor(category).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '$categoryCheckedCount/${items.length}',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: _getCategoryColor(category),
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          const Divider(height: 1),
          
          // Items
          ...items.asMap().entries.map((entry) {
            final index = entry.key;
            final item = entry.value;
            final isLast = index == items.length - 1;
            return _buildGroceryItem(item, isLast);
          }),
        ],
      ),
    );
  }

  Widget _buildGroceryItem(Map<String, dynamic> item, bool isLast) {
    final itemName = item['name'] as String;
    final isChecked = _checkedItems.contains(itemName);
    final quantity = item['quantity'] as String;
    final unit = item['unit'] as String;
    
    return Container(
      decoration: BoxDecoration(
        border: isLast ? null : Border(
          bottom: BorderSide(
            color: const Color(0xFFF3F4F6),
            width: 1,
          ),
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => _toggleItem(itemName),
          borderRadius: isLast 
              ? const BorderRadius.only(
                  bottomLeft: Radius.circular(20),
                  bottomRight: Radius.circular(20),
                )
              : null,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            child: Row(
              children: [
                // Checkbox
                GestureDetector(
                  onTap: () => _toggleItem(itemName),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      color: isChecked ? const Color(0xFF10B981) : Colors.transparent,
                      border: Border.all(
                        color: isChecked ? const Color(0xFF10B981) : const Color(0xFFD1D5DB),
                        width: 2,
                      ),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: isChecked
                        ? const Icon(
                            Icons.check,
                            color: Colors.white,
                            size: 16,
                          )
                        : null,
                  ),
                ),
                
                const SizedBox(width: 16),
                
                // Item details
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        itemName,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: isChecked 
                              ? const Color(0xFF9CA3AF) 
                              : const Color(0xFF1F2937),
                          decoration: isChecked 
                              ? TextDecoration.lineThrough 
                              : null,
                        ),
                      ),
                      if (quantity.isNotEmpty || unit.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(top: 4),
                          child: Text(
                            '$quantity $unit'.trim(),
                            style: TextStyle(
                              fontSize: 14,
                              color: isChecked 
                                  ? const Color(0xFFD1D5DB) 
                                  : const Color(0xFF6B7280),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _toggleItem(String itemName) async {
    setState(() {
      if (_checkedItems.contains(itemName)) {
        _checkedItems.remove(itemName);
      } else {
        _checkedItems.add(itemName);
      }
    });
    
    // Update backend
    if (_listId != null) {
      try {
        final apiService = context.read<ApiService>();
        final mealPlanningApi = MealPlanningApiService(apiService);
        
        await mealPlanningApi.checkGroceryItem(
          listId: _listId!,
          itemName: itemName,
          checked: _checkedItems.contains(itemName),
        );
      } catch (e) {
        print('❌ [GROCERY LIST] Error updating item: $e');
      }
    }
  }

  void _shareList() {
    // TODO: Implement share functionality
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Share functionality - Coming soon!'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  String _capitalizeCategory(String category) {
    return category.split('_').map((word) => 
      word[0].toUpperCase() + word.substring(1)
    ).join(' ');
  }

  IconData _getCategoryIcon(String category) {
    switch (category.toLowerCase()) {
      case 'produce':
        return Icons.eco;
      case 'meat':
      case 'protein':
        return Icons.set_meal;
      case 'dairy':
        return Icons.egg;
      case 'grains':
      case 'bakery':
        return Icons.bakery_dining;
      case 'pantry':
      case 'canned':
        return Icons.inventory_2;
      case 'frozen':
        return Icons.ac_unit;
      case 'beverages':
        return Icons.local_drink;
      case 'snacks':
        return Icons.cookie;
      case 'condiments':
      case 'spices':
        return Icons.restaurant;
      default:
        return Icons.shopping_basket;
    }
  }

  Color _getCategoryColor(String category) {
    switch (category.toLowerCase()) {
      case 'produce':
        return const Color(0xFF10B981);
      case 'meat':
      case 'protein':
        return const Color(0xFFEF4444);
      case 'dairy':
        return const Color(0xFFF59E0B);
      case 'grains':
      case 'bakery':
        return const Color(0xFFF97316);
      case 'pantry':
      case 'canned':
        return const Color(0xFF8B5CF6);
      case 'frozen':
        return const Color(0xFF06B6D4);
      case 'beverages':
        return const Color(0xFF3B82F6);
      case 'snacks':
        return const Color(0xFFEC4899);
      case 'condiments':
      case 'spices':
        return const Color(0xFF6366F1);
      default:
        return const Color(0xFF6B7280);
    }
  }
}







