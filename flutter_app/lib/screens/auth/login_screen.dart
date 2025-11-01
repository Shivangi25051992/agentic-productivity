import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

import '../../providers/auth_provider.dart';
import '../../utils/constants.dart';
import '../../widgets/common/custom_button.dart';
import '../../widgets/common/custom_input.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _obscure = true;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final auth = context.read<AuthProvider>();
    await auth.signInWithEmail(_emailCtrl.text.trim(), _passwordCtrl.text);
    if (!mounted) return;
    if (auth.errorMessage != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(auth.errorMessage!)));
    } else {
      Navigator.of(context).pushReplacementNamed('/home');
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 520),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 250),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface.withOpacity(0.9),
                borderRadius: BorderRadius.circular(24),
                boxShadow: const [BoxShadow(blurRadius: 30, color: Colors.black12)],
              ),
              padding: const EdgeInsets.all(24),
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: 4),
                    Text(Strings.loginTitle, style: Theme.of(context).textTheme.headlineMedium, textAlign: TextAlign.center),
                    const SizedBox(height: 4),
                    Text('Secure access to your productivity hub', textAlign: TextAlign.center, style: Theme.of(context).textTheme.bodyMedium),
                    const SizedBox(height: 20),
                    CustomInput(
                      controller: _emailCtrl,
                      labelText: 'Email',
                      keyboardType: TextInputType.emailAddress,
                      validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                      autofocus: true,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _passwordCtrl,
                      obscureText: _obscure,
                      validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                      decoration: InputDecoration(
                        labelText: 'Password',
                        suffixIcon: IconButton(
                          onPressed: () => setState(() => _obscure = !_obscure),
                          icon: Icon(_obscure ? Icons.visibility : Icons.visibility_off),
                        ),
                      ),
                    ),
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton(onPressed: () {}, child: const Text('Forgot Password?')),
                    ),
                    const SizedBox(height: 8),
                    CustomButton(text: auth.isLoading ? 'Signing in…' : 'Sign In', onPressed: auth.isLoading ? null : _submit),
                    const SizedBox(height: 8),
                    if (!kIsWeb) // show Google only on mobile for now
                      OutlinedButton.icon(
                        onPressed: auth.isLoading ? null : () async {
                          await context.read<AuthProvider>().signInWithGoogle();
                          if (!mounted) return;
                          final a = context.read<AuthProvider>();
                          if (a.errorMessage != null) {
                            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(a.errorMessage!)));
                          } else {
                            Navigator.of(context).pushReplacementNamed('/home');
                          }
                        },
                        icon: const Icon(Icons.g_mobiledata),
                        label: const Text('Sign in with Google'),
                      ),
                    if (auth.errorMessage != null) ...[
                      const SizedBox(height: 8),
                      Text(auth.errorMessage!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                    ],
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text("Don't have an account?"),
                        TextButton(onPressed: () => Navigator.of(context).pushNamed('/signup'), child: const Text('Sign Up')),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}


