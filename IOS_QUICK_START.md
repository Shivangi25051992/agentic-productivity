# 🚀 iOS QUICK START GUIDE

**Status**: ⏳ **Waiting for Xcode Installation**  
**Current Branch**: `develop-ios` ✅

---

## 📋 **WHEN XCODE FINISHES INSTALLING**

### **OPTION 1: Automated Setup** (Recommended)

Just run this one command:

```bash
./setup_ios_after_xcode.sh
```

This will automatically:
1. ✅ Configure Xcode
2. ✅ Install iOS dependencies (CocoaPods)
3. ✅ Launch iOS Simulator
4. ✅ Prepare everything for your app

### **OPTION 2: Manual Setup**

If you prefer step-by-step:

```bash
# 1. Configure Xcode
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license accept
sudo xcodebuild -runFirstLaunch

# 2. Verify installation
xcodebuild -version

# 3. Install iOS dependencies
cd flutter_app/ios
export LANG=en_US.UTF-8
pod install
cd ../..

# 4. Check Flutter setup
flutter doctor

# 5. List available devices
flutter devices

# 6. Open iOS Simulator
open -a Simulator
```

---

## 🎯 **RUNNING YOUR APP ON iOS**

### **Once Simulator is Open**:

```bash
cd flutter_app

# Run on iOS (auto-selects simulator)
flutter run

# Or specify device
flutter run -d "iPhone 16 Pro"
```

### **First Build** (takes 3-5 minutes):
- Flutter compiles your Dart code
- Xcode builds the iOS app
- Dependencies are linked
- App launches in simulator

### **Subsequent Runs** (30 seconds):
- Much faster!
- Use hot reload (`r`) for instant updates

---

## ⌨️ **FLUTTER COMMANDS WHILE RUNNING**

Once your app is running, press:

- **`r`** - Hot reload (instant UI updates)
- **`R`** - Hot restart (full app restart)
- **`h`** - Help (show all commands)
- **`d`** - Detach (keep app running, exit flutter)
- **`c`** - Clear console
- **`q`** - Quit (stop app)

---

## 📱 **WHAT YOU'LL SEE**

Your app will launch in the iOS Simulator showing:

✅ **Native iOS Experience**:
- iOS status bar (time, battery, signal)
- Native iOS navigation (swipe back)
- iOS keyboard
- iOS animations and transitions
- Native scrolling physics

✅ **All Your Features**:
- Login/Signup
- Home screen with "How You're Leveling Up 🆙"
- Quick-add water button (+250ml)
- Quick-add supplements button
- Meal planning with Yuvi
- Plan selector
- Profile with Free Tier badge
- Chat with Yuvi

---

## 🐛 **TROUBLESHOOTING**

### **"No devices found"**

```bash
# Restart Flutter
killall -9 dart
flutter devices

# Or manually open Simulator
open -a Simulator
```

### **"CocoaPods error"**

```bash
cd flutter_app/ios
pod deintegrate
pod install
cd ../..
```

### **"Build failed"**

```bash
# Clean and rebuild
flutter clean
cd flutter_app
flutter run
```

### **"Xcode license not accepted"**

```bash
sudo xcodebuild -license accept
```

---

## 📊 **DEVELOPMENT WORKFLOW**

### **Daily iOS Development**:

```bash
# 1. Switch to iOS branch
git checkout develop-ios

# 2. Open Simulator
open -a Simulator

# 3. Run app
cd flutter_app
flutter run

# 4. Make changes in your code editor

# 5. Press 'r' for hot reload (instant updates!)

# 6. Test your changes

# 7. Commit when ready
git add .
git commit -m "feat: add iOS feature"
```

---

## 🔄 **SWITCHING BETWEEN WEB & iOS**

### **To Web Development**:
```bash
git checkout develop-web
cd flutter_app
flutter run -d chrome --web-port=9001
```

### **Back to iOS Development**:
```bash
git checkout develop-ios
open -a Simulator
cd flutter_app
flutter run
```

---

## 🎯 **TESTING ON PHYSICAL iPhone** (Later)

### **Requirements**:
1. iPhone connected via USB
2. Developer Mode enabled on iPhone
3. Trust computer on iPhone

### **Steps**:
```bash
# 1. Connect iPhone
# 2. Trust computer on iPhone
# 3. List devices
flutter devices

# 4. Run on iPhone
flutter run -d <your-iphone-id>

# 5. First time: Trust developer certificate
#    iPhone → Settings → General → VPN & Device Management
#    → Tap your Apple ID → Trust
```

---

## 📱 **SIMULATOR TIPS**

### **Useful Simulator Shortcuts**:
- **⌘ + K** - Toggle keyboard
- **⌘ + Shift + H** - Home button
- **⌘ + Shift + H** (twice) - App switcher
- **⌘ + →** - Rotate right
- **⌘ + ←** - Rotate left
- **⌘ + 1/2/3** - Scale (100%, 75%, 50%)

### **Simulate Actions**:
- **Features → Location** - Test location features
- **Features → Shake** - Test shake gestures
- **Device → Restart** - Restart simulator

---

## 🚀 **PERFORMANCE TIPS**

### **Faster Builds**:
```bash
# Use profile mode for better performance testing
flutter run --profile

# Use release mode for production-like performance
flutter run --release
```

### **Debug Performance**:
```bash
# Enable performance overlay
flutter run --profile
# Then press 'P' while running
```

---

## 📋 **CHECKLIST FOR FIRST RUN**

After Xcode installs:

- [ ] Run `./setup_ios_after_xcode.sh`
- [ ] Wait for iOS Simulator to open
- [ ] Run `cd flutter_app && flutter run`
- [ ] Wait for first build (3-5 min)
- [ ] See your app launch! 🎉
- [ ] Test login/signup
- [ ] Test home screen
- [ ] Test quick-add water button
- [ ] Test meal planning
- [ ] Test chat with Yuvi
- [ ] Try hot reload (press `r`)

---

## 🎉 **YOU'RE READY!**

Once Xcode finishes installing, just run:

```bash
./setup_ios_after_xcode.sh
```

Then:

```bash
cd flutter_app
flutter run
```

**That's it!** Your app will launch on iOS! 🚀

---

**Current Status**: ⏳ Waiting for Xcode installation to complete  
**Next Step**: Run `./setup_ios_after_xcode.sh` when Xcode is ready  
**ETA**: ~5 minutes after Xcode installs


