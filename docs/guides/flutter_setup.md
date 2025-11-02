## Flutter App – Setup

### Prerequisites
- Flutter SDK (3.3+)
- Dart SDK (bundled)
- Xcode (iOS), Android Studio/SDK (Android), Chrome (Web)

### 1) Install dependencies
```bash
cd flutter_app
flutter pub get
```

### 2) Firebase setup
- Add a Firebase project, enable Authentication and Firestore.
- Add platform apps (iOS/Android/Web) and download configs.
- Initialize Firebase in `main.dart` (already wired).

### 3) Run
```bash
flutter run -d chrome   # Web
flutter run -d ios      # iOS
flutter run -d android  # Android
```

### 4) Configure API base URL
Pass compile-time env:
```bash
flutter run --dart-define=API_BASE_URL=http://localhost:8000
```







