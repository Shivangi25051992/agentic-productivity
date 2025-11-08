# 🌳 BRANCHING STRATEGY

**Goal**: Keep web and iOS development separate and organized  
**Status**: ✅ **IMPLEMENTED**

---

## 📋 **BRANCH STRUCTURE**

```
main (production-ready code)
├── develop-web (web development & testing)
└── develop-ios (iOS development & testing)
```

---

## 🎯 **BRANCH PURPOSES**

### **`main`** - Production Branch
- **Purpose**: Stable, production-ready code
- **Deploys to**: 
  - Backend: Cloud Run
  - Frontend: Firebase Hosting (web)
  - iOS: App Store (future)
- **Merge from**: `develop-web` or `develop-ios` after testing
- **Never**: Develop directly on main

### **`develop-web`** - Web Development
- **Purpose**: Web-specific features and testing
- **Platform**: Web browsers (Chrome, Safari, Firefox)
- **Testing**: Local web server (`flutter run -d chrome`)
- **Features**: PWA, web-specific optimizations
- **Merge to**: `main` when ready for production

### **`develop-ios`** - iOS Development
- **Purpose**: iOS-specific features and testing
- **Platform**: iOS Simulator & physical iPhone
- **Testing**: Xcode Simulator, TestFlight
- **Features**: Native iOS, App Store preparation
- **Merge to**: `main` when ready for App Store

---

## 🔄 **WORKFLOW**

### **Starting Web Development**:
```bash
# Switch to web branch
git checkout develop-web

# Start web development
cd flutter_app
flutter run -d chrome --web-port=9001

# Make changes, test, commit
git add .
git commit -m "feat: add web feature"
git push origin develop-web
```

### **Starting iOS Development**:
```bash
# Switch to iOS branch
git checkout develop-ios

# Start iOS development
cd flutter_app
flutter run  # Auto-selects iOS simulator

# Or run on physical iPhone
flutter run -d <iphone-id>

# Make changes, test, commit
git add .
git commit -m "feat: add iOS feature"
git push origin develop-ios
```

### **Merging to Production**:
```bash
# After testing on develop-web or develop-ios
git checkout main
git merge develop-web  # or develop-ios
git push origin main

# Deploy to production
./deploy_production.sh
```

---

## 📱 **PLATFORM-SPECIFIC FILES**

### **Web-Only** (in `develop-web`):
```
flutter_app/
├── web/
│   ├── index.html
│   ├── manifest.json
│   └── favicon.png
├── firebase.json (hosting config)
└── .firebaserc
```

### **iOS-Only** (in `develop-ios`):
```
flutter_app/
├── ios/
│   ├── Runner/
│   │   ├── Info.plist
│   │   └── AppDelegate.swift
│   ├── Podfile
│   └── Runner.xcworkspace
└── .ios-specific-config
```

### **Shared** (in both branches):
```
flutter_app/
├── lib/ (all Dart code)
├── pubspec.yaml
├── assets/
└── test/
```

---

## 🎯 **BEST PRACTICES**

### **1. Keep Branches Synced**:
```bash
# Regularly merge main into your development branch
git checkout develop-web
git merge main
git push origin develop-web

git checkout develop-ios
git merge main
git push origin develop-ios
```

### **2. Share Common Features**:
```bash
# If you add a feature that works on both platforms:
# 1. Implement on one branch (e.g., develop-web)
git checkout develop-web
# ... make changes ...
git commit -m "feat: add shared feature"

# 2. Cherry-pick to other branch
git checkout develop-ios
git cherry-pick <commit-hash>
git push origin develop-ios
```

### **3. Platform-Specific Features**:
```bash
# Use platform checks in code:
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;

if (kIsWeb) {
  // Web-specific code
} else if (Platform.isIOS) {
  // iOS-specific code
}
```

---

## 🚀 **QUICK REFERENCE**

### **Switch Branches**:
```bash
# To web development
git checkout develop-web

# To iOS development
git checkout develop-ios

# To production
git checkout main
```

### **Check Current Branch**:
```bash
git branch --show-current
```

### **List All Branches**:
```bash
git branch -a
```

### **Create New Feature Branch** (optional):
```bash
# From develop-web
git checkout develop-web
git checkout -b feature/new-web-feature

# From develop-ios
git checkout develop-ios
git checkout -b feature/new-ios-feature
```

---

## 📊 **CURRENT STATUS**

| Branch | Status | Purpose | Last Updated |
|--------|--------|---------|--------------|
| `main` | ✅ Active | Production | Nov 8, 2025 |
| `develop-web` | ✅ Active | Web dev | Nov 8, 2025 |
| `develop-ios` | ✅ Active | iOS dev | Nov 8, 2025 |

---

## 🎯 **DEPLOYMENT CHECKLIST**

### **Before Deploying to Production**:

**From `develop-web`**:
- [ ] Test on Chrome, Safari, Firefox
- [ ] Test on mobile browsers (iOS Safari, Android Chrome)
- [ ] Run `flutter build web --release`
- [ ] Test production build locally
- [ ] Merge to `main`
- [ ] Run `./deploy_production.sh`

**From `develop-ios`**:
- [ ] Test on iOS Simulator
- [ ] Test on physical iPhone
- [ ] Run `flutter build ios --release`
- [ ] Test with TestFlight (future)
- [ ] Merge to `main`
- [ ] Submit to App Store (future)

---

## 💡 **PRO TIPS**

1. **Always commit before switching branches**
2. **Use descriptive commit messages**
3. **Test thoroughly before merging to main**
4. **Keep branches up to date with main**
5. **Use `.gitignore` for platform-specific build files**

---

## 🔧 **TROUBLESHOOTING**

### **Uncommitted Changes When Switching**:
```bash
# Stash your changes
git stash

# Switch branch
git checkout develop-ios

# Apply stashed changes (if needed)
git stash pop
```

### **Merge Conflicts**:
```bash
# When merging main into develop branch
git checkout develop-web
git merge main

# If conflicts occur:
# 1. Resolve conflicts in files
# 2. Stage resolved files
git add .

# 3. Complete merge
git commit
```

### **Accidentally Committed to Wrong Branch**:
```bash
# Move last commit to correct branch
git log  # Note the commit hash

# Switch to correct branch
git checkout develop-ios

# Cherry-pick the commit
git cherry-pick <commit-hash>

# Go back and remove from wrong branch
git checkout develop-web
git reset --hard HEAD~1
```

---

**Current Branch**: `develop-ios` ✅  
**Ready for**: iOS development and testing  
**Next Step**: Configure iOS project and run on simulator


