# 🔧 Environment Configuration

## Automatic Environment Detection

The app now **automatically detects** which environment it's running in!

---

## 🎯 How It Works

### **Debug Mode (Development)**
```dart
flutter run -d chrome
// Uses: http://localhost:8000
```

### **Release Mode (Production)**
```dart
flutter build web --release
// Uses: https://aiproductivity-backend-51515298953.us-central1.run.app
```

---

## 🛠️ Manual Override (Optional)

You can override the API URL using environment variables:

### **Local Testing with Custom URL**
```bash
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:3000
```

### **Staging Environment**
```bash
flutter build web --release --dart-define=API_BASE_URL=https://staging-backend.run.app
```

### **Production Build**
```bash
flutter build web --release
# Automatically uses production URL
```

---

## 📋 Environment Priority

The app checks in this order:

1. **Environment Variable** (`--dart-define=API_BASE_URL`)
2. **Debug Mode** → `http://localhost:8000`
3. **Release Mode** → `https://aiproductivity-backend-51515298953.us-central1.run.app`

---

## ✅ Benefits

### **No More Manual Changes!**
- ✅ Developers run `flutter run` → Uses localhost automatically
- ✅ Production builds use production URL automatically
- ✅ No need to edit `constants.dart` file
- ✅ No risk of committing wrong URL

### **Flexible Testing**
- ✅ Can test against staging
- ✅ Can test against different local ports
- ✅ Can test against remote dev server

---

## 🧪 Testing Different Environments

### **Local Backend (Default)**
```bash
flutter run -d chrome
# Uses: http://localhost:8000
```

### **Local Backend on Different Port**
```bash
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:3000
```

### **Remote Dev Server**
```bash
flutter run -d chrome --dart-define=API_BASE_URL=https://dev-backend.run.app
```

### **Production Backend (for testing)**
```bash
flutter run -d chrome --dart-define=API_BASE_URL=https://aiproductivity-backend-51515298953.us-central1.run.app
```

---

## 🚀 Deployment

### **Firebase Hosting (Production)**
```bash
# Build with production URL (automatic)
flutter build web --release

# Deploy
firebase deploy --only hosting
```

### **Staging Deployment**
```bash
# Build with staging URL
flutter build web --release --dart-define=API_BASE_URL=https://staging-backend.run.app

# Deploy to staging
firebase deploy --only hosting:staging
```

---

## 🔍 Debugging

To check which URL is being used:

```dart
import 'package:flutter/foundation.dart';

print('API Base URL: ${AppConstants.apiBaseUrl}');
print('Debug Mode: $kDebugMode');
```

---

## 📝 Code Implementation

```dart
// flutter_app/lib/utils/constants.dart

static String get apiBaseUrl {
  // 1. Check environment variable
  const envUrl = String.fromEnvironment('API_BASE_URL', defaultValue: '');
  if (envUrl.isNotEmpty) {
    return envUrl;
  }
  
  // 2. Auto-detect based on debug mode
  if (kDebugMode) {
    return 'http://localhost:8000';  // Development
  } else {
    return 'https://aiproductivity-backend-51515298953.us-central1.run.app';  // Production
  }
}
```

---

## ⚠️ Important Notes

1. **Never hardcode URLs** in the app code
2. **Always use** `AppConstants.apiBaseUrl`
3. **Debug builds** automatically use localhost
4. **Release builds** automatically use production
5. **Environment variables** override everything

---

## 🎉 Result

**No more accidentally breaking production!** 🎊

- Developers can work locally without touching config
- Production builds work automatically
- Flexible for testing different environments
- Clear and maintainable

---

**Last Updated**: November 4, 2025








