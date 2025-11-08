import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:provider/provider.dart';
import 'dart:io' show Platform;

import 'home/mobile_first_home_screen.dart';
import 'home/ios_home_screen.dart';
import 'home/ios_home_screen_v2_hybrid.dart';
import 'home/ios_home_screen_v3_apple.dart';
import 'home/ios_home_screen_v4_compact.dart';
import 'chat/chat_screen.dart';
import 'timeline/timeline_screen.dart';
import 'plan/plan_screen.dart';
import 'profile/profile_screen.dart';
import '../widgets/common/app_sidebar.dart';
import '../providers/home_variant_provider.dart';

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
        default:
          return const IosHomeScreenV2Hybrid(); // Default to v2
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
          ChatScreen(),
          TimelineScreen(),
          PlanScreen(),
          ProfileScreen(),
        ],
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 10,
              offset: const Offset(0, -5),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: _onTabTapped,
          type: BottomNavigationBarType.fixed,
          selectedItemColor: Theme.of(context).colorScheme.primary,
          unselectedItemColor: Theme.of(context).textTheme.bodySmall?.color,
          selectedFontSize: 12,
          unselectedFontSize: 12,
          elevation: 0,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home_outlined),
              activeIcon: Icon(Icons.home),
              label: 'Home',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.chat_bubble_outline),
              activeIcon: Icon(Icons.chat_bubble),
              label: 'Assistant',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.timeline_outlined),
              activeIcon: Icon(Icons.timeline),
              label: 'Timeline',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.calendar_today_outlined),
              activeIcon: Icon(Icons.calendar_today),
              label: 'Plan',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_outline),
              activeIcon: Icon(Icons.person),
              label: 'Profile',
            ),
          ],
        ),
      ),
    );
  }
}

