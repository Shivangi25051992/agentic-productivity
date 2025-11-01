import 'package:flutter/material.dart';

/// Wrapper widget for onboarding steps with progress indicator and navigation
class OnboardingStep extends StatelessWidget {
  final String title;
  final String stepDisplay; // e.g., "1/7"
  final double progress; // 0.0 to 1.0
  final Widget child;
  final VoidCallback? onNext;
  final VoidCallback? onBack;
  final bool isNextEnabled;
  final String nextButtonText;
  final bool showSkip;

  const OnboardingStep({
    super.key,
    required this.title,
    required this.stepDisplay,
    required this.progress,
    required this.child,
    this.onNext,
    this.onBack,
    this.isNextEnabled = true,
    this.nextButtonText = 'Continue',
    this.showSkip = false,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: onBack != null
            ? IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: onBack,
              )
            : null,
        title: Text(stepDisplay),
        centerTitle: true,
        actions: [
          if (showSkip)
            TextButton(
              onPressed: () {
                Navigator.of(context).pushReplacementNamed('/home');
              },
              child: const Text('Skip'),
            ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(4),
          child: LinearProgressIndicator(
            value: progress,
            backgroundColor: Theme.of(context).dividerColor.withOpacity(0.1),
          ),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 24),
                    child,
                  ],
                ),
              ),
            ),
            // Bottom button
            if (onNext != null)
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Theme.of(context).scaffoldBackgroundColor,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, -5),
                    ),
                  ],
                ),
                child: SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: isNextEnabled ? onNext : null,
                    style: ElevatedButton.styleFrom(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: Text(
                      nextButtonText,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}





