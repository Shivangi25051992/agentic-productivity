import 'dart:async';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart' as fb_auth;
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter/foundation.dart' show kIsWeb, kDebugMode;

import 'config/environment_config.dart';

import 'providers/auth_provider.dart';
import 'providers/task_provider.dart';
import 'providers/fitness_provider.dart';
import 'providers/notification_provider.dart';
import 'providers/chat_provider.dart';
import 'providers/profile_provider.dart';
import 'providers/onboarding_provider.dart';
import 'providers/dashboard_provider.dart';
import 'providers/timeline_provider.dart';
import 'services/notification_service.dart';
import 'screens/landing/landing_page.dart';
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
import 'screens/meals/timeline_view_screen.dart';
import 'screens/timeline/timeline_screen.dart';
import 'screens/profile/edit_profile_screen.dart';
import 'utils/theme.dart';
import 'services/api_service.dart';
import 'firebase_options.dart';
import 'widgets/common/auth_guard.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Validate configuration before starting app
  try {
    EnvironmentConfig.validate();
  } catch (e) {
    // Configuration validation failed - show error and exit
    runApp(MaterialApp(
      home: Scaffold(
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error_outline, size: 64, color: Colors.red),
                const SizedBox(height: 24),
                const Text(
                  'Configuration Error',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                Text(
                  e.toString(),
                  style: const TextStyle(fontSize: 14, color: Colors.red),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    ));
    return;
  }
  
  try {
    await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
    debugPrint('✅ Firebase initialized for ${DefaultFirebaseOptions.currentPlatform.projectId}');
    
    if (!kIsWeb) {
      await NotificationService.instance.initialize();
    }
  } catch (e) {
    debugPrint('❌ Firebase initialization error: $e');
    // Don't rethrow - allow app to continue
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
        // ✅ FIX: Provide ApiService globally so widgets can access it via Provider.of<ApiService>
        ProxyProvider<AuthProvider, ApiService>(
          update: (context, auth, previous) => ApiService(auth),
        ),
        // TimelineProvider needs ApiService, so we use ChangeNotifierProxyProvider
        ChangeNotifierProxyProvider<AuthProvider, TimelineProvider>(
          create: (context) {
            final auth = context.read<AuthProvider>();
            return TimelineProvider(ApiService(auth));
          },
          update: (context, auth, previous) {
            if (previous == null) {
              return TimelineProvider(ApiService(auth));
            }
            // Reuse existing provider
            return previous;
          },
        ),
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
        '/meals/timeline': (_) => const AuthGuard(child: TimelineViewScreen()),
        '/profile/edit': (_) => const AuthGuard(child: EditProfileScreen()),
        
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
      home: auth.isAuthenticated ? const _HomeOrOnboarding() : const LoginScreen(), // Temporarily bypass landing page
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
  String? _debugError;

  @override
  void initState() {
    super.initState();
    _checkProfile();
  }

  Future<void> _checkProfile() async {
    debugPrint('🔍 [MOBILE DEBUG] Starting profile check...');
    
    final auth = context.read<AuthProvider>();
    final profile = context.read<ProfileProvider>();

    // Check if user is authenticated
    if (!auth.isAuthenticated || auth.currentUser == null) {
      debugPrint('❌ [MOBILE DEBUG] User not authenticated!');
      if (mounted) {
        setState(() {
          _isChecking = false;
          _debugError = 'Not authenticated';
        });
      }
      return;
    }

    debugPrint('✅ [MOBILE DEBUG] User authenticated: ${auth.currentUser?.email}');

    // Try to get ID token
    String? token;
    try {
      token = await auth.getIdToken();
      debugPrint('✅ [MOBILE DEBUG] Got ID token: ${token?.substring(0, 20)}...');
    } catch (e) {
      debugPrint('❌ [MOBILE DEBUG] Failed to get ID token: $e');
      if (mounted) {
        setState(() {
          _isChecking = false;
          _debugError = 'Token error: $e';
        });
      }
      return;
    }

    if (token == null) {
      debugPrint('❌ [MOBILE DEBUG] ID token is null!');
      if (mounted) {
        setState(() {
          _isChecking = false;
          _debugError = 'Token is null';
        });
      }
      return;
    }

    // Try to fetch profile
    debugPrint('🔍 [MOBILE DEBUG] Fetching profile...');
    try {
      await profile.fetchProfile(auth);
      debugPrint('✅ [MOBILE DEBUG] Profile fetch completed');
      debugPrint('🔍 [MOBILE DEBUG] Profile data: ${profile.profile?.toJson()}');
      debugPrint('🔍 [MOBILE DEBUG] Has profile: ${profile.hasProfile}');
      debugPrint('🔍 [MOBILE DEBUG] Onboarding completed: ${profile.profile?.onboardingCompleted}');
    } catch (e, stackTrace) {
      debugPrint('❌ [MOBILE DEBUG] Profile fetch error: $e');
      debugPrint('❌ [MOBILE DEBUG] Stack trace: $stackTrace');
      if (mounted) {
        setState(() {
          _isChecking = false;
          _debugError = 'Profile fetch error: $e';
        });
      }
      // Don't return - continue to check profile state
    }

    if (mounted) {
      setState(() {
        _isChecking = false;
      });

      // If no profile or onboarding not completed, redirect to welcome
      // SKIP IN DEBUG MODE for local testing
      if (!profile.hasProfile && !kDebugMode) {
        debugPrint('⚠️  [MOBILE DEBUG] No profile found or onboarding not completed - redirecting to onboarding');
        debugPrint('🔍 [MOBILE DEBUG] Profile object: ${profile.profile}');
        debugPrint('🔍 [MOBILE DEBUG] Profile error: ${profile.errorMessage}');
        Navigator.of(context).pushReplacementNamed('/onboarding/welcome');
      } else if (!profile.hasProfile && kDebugMode) {
        debugPrint('🔧 [DEV MODE] Skipping onboarding check for local development');
      } else {
        debugPrint('✅ [MOBILE DEBUG] Profile found - showing home screen');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isChecking) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(),
              const SizedBox(height: 16),
              const Text('Loading your profile...'),
              if (_debugError != null) ...[
                const SizedBox(height: 16),
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Text(
                    'Debug: $_debugError',
                    style: const TextStyle(fontSize: 12, color: Colors.red),
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
            ],
          ),
        ),
      );
    }

    return const MainNavigation();
  }
}
