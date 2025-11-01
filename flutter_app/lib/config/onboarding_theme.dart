import 'package:flutter/material.dart';

/// 🎨 Onboarding Design System
/// Modern, GenZ-friendly design inspired by Apple, Notion, and Linear
class OnboardingTheme {
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 🎨 COLOR PALETTE
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  // Primary Colors
  static const primaryTeal = Color(0xFF20B2AA);
  static const primaryTealLight = Color(0xFF4FD1C5);
  static const primaryTealDark = Color(0xFF0F8A82);
  
  // Background Colors
  static const bgCream = Color(0xFFFDFCF9);
  static const bgWhite = Color(0xFFFFFFFF);
  static const bgGray = Color(0xFFF7F8FA);
  
  // Text Colors
  static const textPrimary = Color(0xFF1A202C);
  static const textSecondary = Color(0xFF718096);
  static const textTertiary = Color(0xFFA0AEC0);
  
  // Accent Colors
  static const accentBlue = Color(0xFF4299E1);
  static const accentPurple = Color(0xFF9F7AEA);
  static const accentPink = Color(0xFFED64A6);
  static const accentOrange = Color(0xFFED8936);
  static const accentGreen = Color(0xFF48BB78);
  
  // Status Colors
  static const success = Color(0xFF48BB78);
  static const warning = Color(0xFFED8936);
  static const error = Color(0xFFF56565);
  static const info = Color(0xFF4299E1);
  
  // Gradient Colors
  static const gradientStart = Color(0xFF20B2AA);
  static const gradientEnd = Color(0xFF4299E1);
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 📐 SPACING & SIZING
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  static const double spacingXS = 4.0;
  static const double spacingS = 8.0;
  static const double spacingM = 16.0;
  static const double spacingL = 24.0;
  static const double spacingXL = 32.0;
  static const double spacingXXL = 48.0;
  
  static const double radiusS = 8.0;
  static const double radiusM = 12.0;
  static const double radiusL = 16.0;
  static const double radiusXL = 24.0;
  static const double radiusFull = 999.0;
  
  static const double iconSizeS = 20.0;
  static const double iconSizeM = 24.0;
  static const double iconSizeL = 32.0;
  static const double iconSizeXL = 48.0;
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 🔤 TYPOGRAPHY
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  static const String fontFamily = 'SF Pro Display'; // System default
  
  static const TextStyle headingXL = TextStyle(
    fontSize: 32,
    fontWeight: FontWeight.w700,
    height: 1.2,
    letterSpacing: -0.5,
    color: textPrimary,
  );
  
  static const TextStyle headingL = TextStyle(
    fontSize: 28,
    fontWeight: FontWeight.w700,
    height: 1.3,
    letterSpacing: -0.3,
    color: textPrimary,
  );
  
  static const TextStyle headingM = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.w600,
    height: 1.3,
    color: textPrimary,
  );
  
  static const TextStyle headingS = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w600,
    height: 1.4,
    color: textPrimary,
  );
  
  static const TextStyle bodyL = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w400,
    height: 1.5,
    color: textSecondary,
  );
  
  static const TextStyle bodyM = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 1.5,
    color: textSecondary,
  );
  
  static const TextStyle bodyS = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w400,
    height: 1.5,
    color: textSecondary,
  );
  
  static const TextStyle caption = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w400,
    height: 1.4,
    color: textTertiary,
  );
  
  static const TextStyle buttonL = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    height: 1.2,
    letterSpacing: 0.2,
  );
  
  static const TextStyle buttonM = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w600,
    height: 1.2,
    letterSpacing: 0.2,
  );
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 🎭 SHADOWS & EFFECTS
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  static List<BoxShadow> shadowS = [
    BoxShadow(
      color: Colors.black.withOpacity(0.05),
      blurRadius: 4,
      offset: const Offset(0, 2),
    ),
  ];
  
  static List<BoxShadow> shadowM = [
    BoxShadow(
      color: Colors.black.withOpacity(0.08),
      blurRadius: 8,
      offset: const Offset(0, 4),
    ),
  ];
  
  static List<BoxShadow> shadowL = [
    BoxShadow(
      color: Colors.black.withOpacity(0.12),
      blurRadius: 16,
      offset: const Offset(0, 8),
    ),
  ];
  
  static List<BoxShadow> shadowGlow = [
    BoxShadow(
      color: primaryTeal.withOpacity(0.3),
      blurRadius: 20,
      offset: const Offset(0, 4),
    ),
  ];
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 🎨 GRADIENTS
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [gradientStart, gradientEnd],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient accentGradient = LinearGradient(
    colors: [accentPurple, accentPink],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static LinearGradient shimmerGradient = LinearGradient(
    colors: [
      Colors.grey.shade200,
      Colors.grey.shade100,
      Colors.grey.shade200,
    ],
    stops: const [0.0, 0.5, 1.0],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 🎯 BUTTON STYLES
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  static ButtonStyle primaryButton = ElevatedButton.styleFrom(
    backgroundColor: primaryTeal,
    foregroundColor: Colors.white,
    minimumSize: const Size.fromHeight(56),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(radiusM),
    ),
    elevation: 0,
    shadowColor: Colors.transparent,
    textStyle: buttonL,
  );
  
  static ButtonStyle secondaryButton = ElevatedButton.styleFrom(
    backgroundColor: bgGray,
    foregroundColor: textPrimary,
    minimumSize: const Size.fromHeight(56),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(radiusM),
    ),
    elevation: 0,
    shadowColor: Colors.transparent,
    textStyle: buttonL,
  );
  
  static ButtonStyle outlineButton = OutlinedButton.styleFrom(
    foregroundColor: primaryTeal,
    minimumSize: const Size.fromHeight(56),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(radiusM),
    ),
    side: const BorderSide(color: primaryTeal, width: 2),
    textStyle: buttonL,
  );
  
  static ButtonStyle textButton = TextButton.styleFrom(
    foregroundColor: primaryTeal,
    minimumSize: const Size.fromHeight(48),
    textStyle: buttonM,
  );
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 📝 INPUT DECORATION
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  static InputDecoration inputDecoration({
    String? label,
    String? hint,
    String? prefix,
    Widget? prefixIcon,
    Widget? suffixIcon,
  }) {
    return InputDecoration(
      labelText: label,
      hintText: hint,
      prefixText: prefix,
      prefixIcon: prefixIcon,
      suffixIcon: suffixIcon,
      filled: true,
      fillColor: bgWhite,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: spacingM,
        vertical: spacingM,
      ),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(radiusM),
        borderSide: BorderSide(color: Colors.grey.shade300),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(radiusM),
        borderSide: BorderSide(color: Colors.grey.shade300),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(radiusM),
        borderSide: const BorderSide(color: primaryTeal, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(radiusM),
        borderSide: const BorderSide(color: error, width: 2),
      ),
      labelStyle: bodyM.copyWith(color: textSecondary),
      hintStyle: bodyM.copyWith(color: textTertiary),
    );
  }
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 🎴 CARD STYLES
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  static BoxDecoration cardDecoration({
    Color? color,
    List<BoxShadow>? shadow,
    Gradient? gradient,
  }) {
    return BoxDecoration(
      color: color ?? bgWhite,
      gradient: gradient,
      borderRadius: BorderRadius.circular(radiusL),
      boxShadow: shadow ?? shadowM,
    );
  }
  
  static BoxDecoration selectableCard({
    required bool isSelected,
  }) {
    return BoxDecoration(
      color: isSelected ? primaryTeal.withOpacity(0.1) : bgWhite,
      borderRadius: BorderRadius.circular(radiusM),
      border: Border.all(
        color: isSelected ? primaryTeal : Colors.grey.shade300,
        width: isSelected ? 2 : 1,
      ),
      boxShadow: isSelected ? shadowGlow : shadowS,
    );
  }
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 🎬 ANIMATIONS
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  static const Duration animationFast = Duration(milliseconds: 200);
  static const Duration animationNormal = Duration(milliseconds: 300);
  static const Duration animationSlow = Duration(milliseconds: 500);
  
  static const Curve animationCurve = Curves.easeInOutCubic;
  static const Curve animationBounceCurve = Curves.elasticOut;
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 🎯 PROGRESS INDICATOR
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  static Widget progressIndicator({
    required int currentStep,
    required int totalSteps,
  }) {
    return Row(
      children: List.generate(totalSteps, (index) {
        final isActive = index <= currentStep;
        final isCurrent = index == currentStep;
        
        return Expanded(
          child: Container(
            margin: EdgeInsets.only(
              right: index < totalSteps - 1 ? spacingXS : 0,
            ),
            height: 4,
            decoration: BoxDecoration(
              color: isActive ? primaryTeal : Colors.grey.shade300,
              borderRadius: BorderRadius.circular(radiusFull),
              boxShadow: isCurrent ? shadowGlow : null,
            ),
          ),
        );
      }),
    );
  }
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 🎨 EMOJI & ICONS
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  static const Map<String, String> onboardingEmojis = {
    'welcome': '👋',
    'profile': '👤',
    'fitness': '💪',
    'nutrition': '🍎',
    'goals': '🎯',
    'activity': '🏃',
    'medical': '🏥',
    'preferences': '⚙️',
    'sync': '🔄',
    'success': '🎉',
    'fire': '🔥',
    'trophy': '🏆',
    'heart': '❤️',
    'brain': '🧠',
  };
}




