import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/auth_provider.dart';
import '../../screens/auth/login_screen.dart';

/// Authentication guard wrapper
/// Redirects to login if user is not authenticated
class AuthGuard extends StatelessWidget {
  final Widget child;
  
  const AuthGuard({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, auth, _) {
        // Show loading while checking auth state
        if (auth.isLoading) {
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }

        // Redirect to login if not authenticated
        if (!auth.isAuthenticated) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            Navigator.of(context).pushReplacementNamed('/login');
          });
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }

        // User is authenticated, show the protected content
        return child;
      },
    );
  }
}

/// Wrapper for authenticated routes
class AuthenticatedRoute extends StatelessWidget {
  final Widget child;
  
  const AuthenticatedRoute({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return AuthGuard(child: child);
  }
}





