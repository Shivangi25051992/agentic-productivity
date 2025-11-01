import 'dart:async';

import 'package:firebase_auth/firebase_auth.dart' as fb_auth;
import 'package:flutter/foundation.dart' show kIsWeb;

/// Custom auth exceptions to surface friendly messages upstream.
class AuthException implements Exception {
  final String code;
  final String message;
  AuthException(this.code, this.message);
  @override
  String toString() => 'AuthException($code): $message';
}

/// Wraps FirebaseAuth with email/password, Google Sign-In, and ID token access.
class AuthService {
  final fb_auth.FirebaseAuth _auth = fb_auth.FirebaseAuth.instance;

  Stream<fb_auth.User?> get authStateChanges => _auth.authStateChanges();

  Future<fb_auth.User?> signUpWithEmail(String email, String password) async {
    try {
      final creds = await _auth.createUserWithEmailAndPassword(email: email, password: password);
      return creds.user;
    } on fb_auth.FirebaseAuthException catch (e) {
      throw _mapFirebaseError(e);
    } catch (e) {
      throw AuthException('unknown', 'Failed to sign up');
    }
  }

  Future<fb_auth.User?> signInWithEmail(String email, String password) async {
    try {
      final creds = await _auth.signInWithEmailAndPassword(email: email, password: password);
      return creds.user;
    } on fb_auth.FirebaseAuthException catch (e) {
      throw _mapFirebaseError(e);
    } catch (e) {
      throw AuthException('unknown', 'Failed to sign in');
    }
  }

  /// Google Sign-In (temporarily disabled on all platforms).
  /// For production, re-enable:
  /// - Web: `await FirebaseAuth.instance.signInWithPopup(GoogleAuthProvider())`
  /// - Mobile: GoogleSignIn + Firebase credential.
  Future<fb_auth.User?> signInWithGoogle() async {
    throw AuthException('unsupported', 'Google Sign-In is temporarily disabled');
  }

  Future<void> signOut() async {
    await _auth.signOut();
  }

  Future<String?> getIdToken() async {
    final u = _auth.currentUser;
    if (u == null) return null;
    return u.getIdToken();
  }

  AuthException _mapFirebaseError(fb_auth.FirebaseAuthException e) {
    switch (e.code) {
      case 'invalid-email':
        return AuthException(e.code, 'Invalid email address');
      case 'user-not-found':
      case 'wrong-password':
        return AuthException(e.code, 'Incorrect email or password');
      case 'email-already-in-use':
        return AuthException(e.code, 'Email already in use');
      case 'weak-password':
        return AuthException(e.code, 'Password is too weak');
      default:
        return AuthException(e.code, e.message ?? 'Authentication error');
    }
  }
}


