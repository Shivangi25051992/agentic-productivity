import 'package:firebase_auth/firebase_auth.dart' as fb_auth;
import 'package:flutter/material.dart';

import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _auth = AuthService();

  fb_auth.User? _user;
  fb_auth.User? get currentUser => _user;
  bool get isAuthenticated => _user != null;

  bool isLoading = false;
  String? errorMessage;

  AuthProvider() {
    _auth.authStateChanges.listen((u) {
      _user = u;
      notifyListeners();
    });
  }

  Future<void> signInWithEmail(String email, String password) async {
    _setLoading(true);
    try {
      errorMessage = null;
      _user = await _auth.signInWithEmail(email, password);
    } catch (e) {
      errorMessage = e.toString();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> signUpWithEmail(String email, String password) async {
    _setLoading(true);
    try {
      errorMessage = null;
      _user = await _auth.signUpWithEmail(email, password);
    } catch (e) {
      errorMessage = e.toString();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> signInWithGoogle() async {
    _setLoading(true);
    try {
      errorMessage = null;
      _user = await _auth.signInWithGoogle();
    } catch (e) {
      errorMessage = e.toString();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> signOut() async {
    await _auth.signOut();
    _user = null;
    notifyListeners();
  }

  Future<String?> getIdToken() => _auth.getIdToken();

  void _setLoading(bool v) { isLoading = v; notifyListeners(); }
}


