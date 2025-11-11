import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:provider/provider.dart';
import 'dart:io' show Platform;
import 'dart:ui' show ImageFilter;

import 'home/mobile_first_home_screen.dart';
import 'home/ios_home_screen.dart';
import 'home/ios_home_screen_v2_hybrid.dart';
import 'home/ios_home_screen_v3_apple.dart';
import 'home/ios_home_screen_v4_compact.dart';
import 'home/ios_home_screen_v5_yuvi_ai_first.dart';
import 'home/ios_home_screen_v6_enhanced.dart';
import 'home/ios_home_screen_v7_mobile_first.dart';
import 'chat/chat_screen.dart';
import 'timeline/timeline_screen.dart';
import 'plan/plan_screen.dart';
import 'profile/profile_screen.dart';
import '../widgets/common/app_sidebar.dart';
import '../widgets/radial_quick_actions.dart';
import '../providers/home_variant_provider.dart';
import '../providers/timeline_provider.dart'; // 🔄 For auto-refresh
import '../providers/dashboard_provider.dart'; // For V7
import '../providers/auth_provider.dart'; // For V7

class MainNavigation extends StatefulWidget {
  final int initialIndex;

  const MainNavigation({
    super.key,
    this.initialIndex = 0,
  });

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  late int _currentIndex;
  late PageController _pageController;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
    _pageController = PageController(initialPage: _currentIndex);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _onPageChanged(int index) {
    setState(() {
      _currentIndex = index;
    });
    
    // 🔄 SIMPLE REFRESH: Force fresh data when switching to Timeline tab
    if (index == 2) { // Timeline tab
      print('🔄 [NAVIGATION] Switched to Timeline tab, forcing refresh...');
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          final timeline = context.read<TimelineProvider>();
          final dashboard = context.read<DashboardProvider>();
          final auth = context.read<AuthProvider>();
          
          // Clear ALL caches
          timeline.invalidateCache();
          dashboard.invalidateCache();
          
          // Force refresh (bypasses cache completely)
          timeline.fetchTimeline(forceRefresh: true);
          dashboard.fetchDailyStats(auth, forceRefresh: true);
          
          print('🔄 [NAVIGATION] Force refresh triggered');
        }
      });
    }
  }

  void _onTabTapped(int index) {
    _pageController.animateToPage(
      index,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  /// Get the appropriate home screen based on platform
  Widget _getHomeScreen(BuildContext context) {
    // Use iOS-optimized screen on iOS, web version elsewhere
    if (!kIsWeb && Platform.isIOS) {
      // Watch the variant provider for changes
      final variant = context.watch<HomeVariantProvider>().variant;
      
      // Return the selected iOS variant
      switch (variant) {
        case 'v1':
          return const IosHomeScreen(); // Original design
        case 'v2':
          return const IosHomeScreenV2Hybrid(); // Hybrid recommended
        case 'v3':
          return const IosHomeScreenV3Apple(); // Apple-inspired premium
        case 'v4':
          return const IosHomeScreenV4Compact(); // Compact rings + inline chat
        case 'v5':
          return const IosHomeScreenV5YuviAiFirst(); // Yuvi AI-First (Chat-centric)
        case 'v6':
          return const IosHomeScreenV6Enhanced(); // Enhanced (Production Ready)
        case 'v7':
          return const IosHomeScreenV7MobileFirst(); // Mobile-First Feed
        default:
          return const IosHomeScreenV6Enhanced(); // Default to v6 (production)
      }
    }
    return MobileFirstHomeScreen();
  }

  void _handleSidebarNavigation(String route) {
    Navigator.pop(context); // Close drawer
    
    switch (route) {
      case 'home':
        _onTabTapped(0);
        break;
      case 'discover':
        // TODO: Navigate to discover page
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Discover - Coming Soon!')),
        );
        break;
      case 'spaces':
        // TODO: Navigate to spaces page
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Spaces - Coming Soon!')),
        );
        break;
      case 'finance':
        // TODO: Navigate to finance page
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Finance - Coming Soon!')),
        );
        break;
      case 'notifications':
        // TODO: Navigate to notifications page
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Notifications - Coming Soon!')),
        );
        break;
      case 'account':
        _onTabTapped(3); // Navigate to Profile
        break;
      case 'upgrade':
        // TODO: Navigate to upgrade/pricing page
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Upgrade to Pro - Coming Soon!')),
        );
        break;
    }
  }

  /// 🎯 Show Radial Quick Actions Menu
  void _showQuickActions() {
    showDialog(
      context: context,
      barrierColor: Colors.transparent,
      builder: (_) => RadialQuickActions(
        onClose: () => Navigator.pop(context),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: AppSidebar(
        onMenuSelected: _handleSidebarNavigation,
      ),
      body: PageView(
        controller: _pageController,
        onPageChanged: _onPageChanged,
        physics: const NeverScrollableScrollPhysics(), // Disable swipe
        children: [
          // Use iOS-optimized home screen on iOS, web version on web
          _getHomeScreen(context),
          PlanScreen(), // Replaced Chat with Plan
          TimelineScreen(),
          ProfileScreen(),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showQuickActions,
        backgroundColor: const Color(0xFF6366F1),
        child: const Icon(Icons.add, size: 24),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      bottomNavigationBar: ClipRRect(
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: BottomAppBar(
            shape: const CircularNotchedRectangle(),
            notchMargin: 8,
            height: 70,
            padding: EdgeInsets.zero,
            color: Colors.black.withOpacity(0.7), // 70% opacity for glassmorphism
            elevation: 0,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  _buildNavItem(Icons.home_outlined, Icons.home, 'Home', 0),
                  _buildNavItem(Icons.calendar_today_outlined, Icons.calendar_today, 'Plan', 1),
                  const SizedBox(width: 56), // Space for FAB
                  _buildNavItem(Icons.timeline_outlined, Icons.timeline, 'Timeline', 2),
                  _buildNavItem(Icons.person_outline, Icons.person, 'Profile', 3),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(IconData icon, IconData activeIcon, String label, int index) {
    final isSelected = _currentIndex == index;
    return Expanded(
      child: GestureDetector(
        onTap: () => _onTabTapped(index),
        child: SizedBox(
          height: 50,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                isSelected ? activeIcon : icon,
                color: isSelected 
                  ? const Color(0xFF6366F1)
                  : Colors.white.withOpacity(0.6), // Better contrast on dark blur
                size: 24,
              ),
              const SizedBox(height: 2),
              Text(
                label,
                style: TextStyle(
                  fontSize: 10,
                  color: isSelected 
                    ? const Color(0xFF6366F1)
                    : Colors.white.withOpacity(0.6), // Better contrast on dark blur
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                ),
                overflow: TextOverflow.clip,
                maxLines: 1,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

