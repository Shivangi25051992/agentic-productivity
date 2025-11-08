// Firebase configuration for all platforms
// Web config is used for web builds
// iOS/Android use the same Firebase project with platform-specific configs
import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart' show defaultTargetPlatform, kIsWeb, TargetPlatform;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      return web;
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        return ios;
      case TargetPlatform.macOS:
        return macos;
      case TargetPlatform.windows:
      case TargetPlatform.linux:
        return web; // fallback to web config for desktop
      default:
        return web;
    }
  }

  // Web configuration (existing, unchanged)
  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyCWfkKNm9Q6nYBHnldlUtlFBS15NJmCBkg',
    appId: '1:51515298953:web:52f38fdff9581deca5e258',
    messagingSenderId: '51515298953',
    projectId: 'productivityai-mvp',
    authDomain: 'productivityai-mvp.firebaseapp.com',
    storageBucket: 'productivityai-mvp.appspot.com',
    measurementId: 'G-07VDDT860C',
  );

  // iOS configuration (same project, iOS-specific app ID)
  static const FirebaseOptions ios = FirebaseOptions(
    apiKey: 'AIzaSyCWfkKNm9Q6nYBHnldlUtlFBS15NJmCBkg',
    appId: '1:51515298953:ios:52f38fdff9581deca5e258',
    messagingSenderId: '51515298953',
    projectId: 'productivityai-mvp',
    authDomain: 'productivityai-mvp.firebaseapp.com',
    storageBucket: 'productivityai-mvp.appspot.com',
    iosBundleId: 'com.example.aiProductivityApp',
  );

  // Android configuration (for future use)
  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'AIzaSyCWfkKNm9Q6nYBHnldlUtlFBS15NJmCBkg',
    appId: '1:51515298953:android:52f38fdff9581deca5e258',
    messagingSenderId: '51515298953',
    projectId: 'productivityai-mvp',
    authDomain: 'productivityai-mvp.firebaseapp.com',
    storageBucket: 'productivityai-mvp.appspot.com',
  );

  // macOS configuration (for future use)
  static const FirebaseOptions macos = FirebaseOptions(
    apiKey: 'AIzaSyCWfkKNm9Q6nYBHnldlUtlFBS15NJmCBkg',
    appId: '1:51515298953:ios:52f38fdff9581deca5e258',
    messagingSenderId: '51515298953',
    projectId: 'productivityai-mvp',
    authDomain: 'productivityai-mvp.firebaseapp.com',
    storageBucket: 'productivityai-mvp.appspot.com',
    iosBundleId: 'com.example.aiProductivityApp',
  );
}
