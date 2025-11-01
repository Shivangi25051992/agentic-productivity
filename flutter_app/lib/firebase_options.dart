// Single definition of DefaultFirebaseOptions for web (manual minimal version).
// If you later run `flutterfire configure`, replace this file with the generated one.
import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart' show defaultTargetPlatform, kIsWeb, TargetPlatform;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      return web;
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
      case TargetPlatform.iOS:
      case TargetPlatform.macOS:
      case TargetPlatform.windows:
      case TargetPlatform.linux:
        return web; // fallback to web config for local web testing
      default:
        return web;
    }
  }

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyCWfkKNm9Q6nYBHnldlUtlFBS15NJmCBkg',
    appId: '1:51515298953:web:52f38fdff9581deca5e258',
    messagingSenderId: '51515298953',
    projectId: 'productivityai-mvp',
    authDomain: 'productivityai-mvp.firebaseapp.com',
    storageBucket: 'productivityai-mvp.appspot.com',
    measurementId: 'G-07VDDT860C',
  );
}
