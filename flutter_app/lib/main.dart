import 'dart:async';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart' as fb_auth;
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

import 'providers/auth_provider.dart';
import 'providers/task_provider.dart';
import 'providers/fitness_provider.dart';
import 'providers/notification_provider.dart';
import 'providers/chat_provider.dart';
import 'providers/profile_provider.dart';
import 'providers/onboarding_provider.dart';
import 'providers/dashboard_provider.dart';
import 'services/notification_service.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/signup_screen.dart';
import 'screens/home/home_screen.dart';
import 'screens/home/enhanced_home_screen.dart';
import 'screens/home/mobile_first_home_screen.dart';
import 'screens/main_navigation.dart';
import 'screens/chat/chat_screen.dart';
import 'screens/tasks/task_list_screen.dart';
import 'screens/fitness/fitness_dashboard_screen.dart';
import 'screens/settings/settings_screen.dart';
import 'screens/onboarding/welcome_screen.dart';
import 'screens/onboarding/welcome_screen_enhanced.dart';
import 'screens/onboarding/basic_info_screen.dart';
import 'screens/onboarding/basic_info_screen_enhanced.dart';
import 'screens/onboarding/bmi_result_screen.dart';
import 'screens/onboarding/activity_level_screen.dart';
import 'screens/onboarding/fitness_goal_screen.dart';
import 'screens/onboarding/goal_review_screen.dart';
import 'screens/onboarding/preferences_screen.dart';
import 'screens/onboarding/review_complete_screen.dart';
import 'screens/onboarding/setup_loading_screen.dart';
import 'screens/onboarding/success_screen.dart';
import 'screens/onboarding/success_screen_enhanced.dart';
import 'utils/theme.dart';
import 'firebase_options.dart';
import 'widgets/common/auth_guard.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  try {
    await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
    if (!kIsWeb) {
      await NotificationService.instance.initialize();
    }
  } catch (e) {
    debugPrint('Firebase initialization error: $e');
  }
  
  runApp(const AppRoot());
}

class AppRoot extends StatelessWidget {
  const AppRoot({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ProfileProvider()),
        ChangeNotifierProvider(create: (_) => OnboardingProvider()),
        ChangeNotifierProvider(create: (_) => DashboardProvider()),
        ChangeNotifierProvider(create: (_) => NotificationProvider()),
        ChangeNotifierProvider(create: (_) => TaskProvider()),
        ChangeNotifierProvider(create: (_) => FitnessProvider()),
        ChangeNotifierProvider(create: (_) => ChatProvider()),
      ],
      child: const _App(),
    );
  }
}

class _App extends StatelessWidget {
  const _App();

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    return MaterialApp(
      title: 'AI Productivity',
      debugShowCheckedModeBanner: false, // Remove debug banner
      themeMode: ThemeMode.system,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      routes: {
        // Public routes (no authentication required)
        '/login': (_) => const LoginScreen(),
        '/signup': (_) => const SignupScreen(),
        
        // Protected routes (authentication required)
        '/home': (_) => const AuthGuard(child: MainNavigation()),
        '/home-dashboard': (_) => const AuthGuard(child: MobileFirstHomeScreen()), // New mobile-first design
        '/home-enhanced': (_) => const AuthGuard(child: EnhancedHomeScreen()), // Previous version
        '/home-old': (_) => const AuthGuard(child: HomeScreen()), // Original version
        '/chat': (_) => const AuthGuard(child: ChatScreen()),
        '/tasks': (_) => const AuthGuard(child: TaskListScreen()),
        '/fitness': (_) => const AuthGuard(child: FitnessDashboardScreen()),
        '/settings': (_) => const AuthGuard(child: SettingsScreen()),
        
        // Onboarding routes (require authentication)
        '/onboarding/welcome': (_) => const AuthGuard(child: WelcomeScreenEnhanced()),
        '/onboarding/welcome-old': (_) => const AuthGuard(child: WelcomeScreen()),
        '/onboarding/basic-info': (_) => const AuthGuard(child: BasicInfoScreenEnhanced()),
        '/onboarding/basic-info-old': (_) => const AuthGuard(child: BasicInfoScreen()),
        '/onboarding/bmi-result': (_) => const AuthGuard(child: BMIResultScreen()),
        '/onboarding/activity-level': (_) => const AuthGuard(child: ActivityLevelScreen()),
        '/onboarding/fitness-goal': (_) => const AuthGuard(child: FitnessGoalScreen()),
        '/onboarding/goal-review': (_) => const AuthGuard(child: GoalReviewScreen()),
        '/onboarding/preferences': (_) => const AuthGuard(child: PreferencesScreen()),
        '/onboarding/review': (_) => const AuthGuard(child: ReviewCompleteScreen()),
        '/onboarding/setup': (_) => const AuthGuard(child: SetupLoadingScreen()),
        '/onboarding/success': (_) => const AuthGuard(child: SuccessScreenEnhanced()),
        '/onboarding/success-old': (_) => const AuthGuard(child: SuccessScreen()),
      },
      home: auth.isAuthenticated ? const _HomeOrOnboarding() : const LoginScreen(),
      builder: (context, child) {
        // Error handling wrapper
        ErrorWidget.builder = (FlutterErrorDetails details) {
          return Scaffold(
            body: Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text('Something went wrong:\n${details.exceptionAsString()}', textAlign: TextAlign.center),
              ),
            ),
          );
        };
        return child!;
      },
    );
  }
}

/// Smart wrapper that checks if user has completed onboarding
/// If not, redirect to welcome screen. Otherwise, show home.
class _HomeOrOnboarding extends StatefulWidget {
  const _HomeOrOnboarding();

  @override
  State<_HomeOrOnboarding> createState() => _HomeOrOnboardingState();
}

class _HomeOrOnboardingState extends State<_HomeOrOnboarding> {
  bool _isChecking = true;

  @override
  void initState() {
    super.initState();
    _checkProfile();
  }

  Future<void> _checkProfile() async {
    final auth = context.read<AuthProvider>();
    final profile = context.read<ProfileProvider>();

    try {
      await profile.fetchProfile(auth);
    } catch (e) {
      // Profile fetch failed, but continue
      debugPrint('Profile fetch error: $e');
    }

    if (mounted) {
      setState(() {
        _isChecking = false;
      });

      // If no profile or onboarding not completed, redirect to welcome
      if (!profile.hasProfile) {
        Navigator.of(context).pushReplacementNamed('/onboarding/welcome');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isChecking) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return const MainNavigation();
  }
}
