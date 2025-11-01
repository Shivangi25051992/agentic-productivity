class Validators {
  static String? required(String? v) => (v == null || v.trim().isEmpty) ? 'Required' : null;
  static String? email(String? v) {
    if (v == null || v.isEmpty) return 'Required';
    final re = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');
    return re.hasMatch(v) ? null : 'Invalid email';
  }
  static String? passwordStrength(String? v) {
    if (v == null || v.length < 8) return 'Min 8 chars';
    final hasLetter = RegExp(r'[A-Za-z]').hasMatch(v);
    final hasDigit = RegExp(r'\d').hasMatch(v);
    if (!hasLetter || !hasDigit) return 'Use letters and numbers';
    return null;
  }
  static String? confirm(String? v, String against) {
    if (v == null || v.isEmpty) return 'Required';
    return v == against ? null : 'Passwords do not match';
  }
}


