# 📱 iOS APP SETUP GUIDE

**Goal**: Run your app as a native iOS app on simulator and iPhone  
**Time**: ~30-60 minutes (depending on download speeds)  
**Status**: 🔄 **IN PROGRESS**

---

## ✅ **CURRENT STATUS**

- ✅ Flutter installed and working
- ✅ Xcode Command Line Tools installed
- ❌ Full Xcode not installed (REQUIRED)
- ❌ CocoaPods not installed (REQUIRED)
- ❌ iOS Simulator not configured

---

## 🛠️ **STEP 1: INSTALL XCODE** (30-45 minutes)

### **Option A: App Store** (Recommended - Easier)

1. Open **App Store** on your Mac
2. Search for **"Xcode"**
3. Click **"Get"** or **"Install"**
4. Wait for download (~15 GB, takes 20-30 minutes)
5. Once installed, open Xcode
6. Accept license agreement
7. Wait for additional components to install

### **Option B: Apple Developer Website** (Faster if you have account)

1. Go to: https://developer.apple.com/xcode/
2. Click **"Download"**
3. Sign in with Apple ID
4. Download Xcode 16.x (latest)
5. Install the `.xip` file
6. Move Xcode to `/Applications`

### **After Installation**:

Run these commands in terminal:

```bash
# Set Xcode path
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer

# Accept license
sudo xcodebuild -license accept

# Run first launch setup
sudo xcodebuild -runFirstLaunch

# Verify installation
xcodebuild -version
```

**Expected Output**:
```
Xcode 16.x
Build version 16xxxxx
```

---

## 🛠️ **STEP 2: INSTALL COCOAPODS** (5 minutes)

CocoaPods is a dependency manager for iOS (like npm for Node.js).

### **Installation**:

```bash
# Install CocoaPods via Homebrew (recommended)
brew install cocoapods

# Or install via Ruby gem
sudo gem install cocoapods

# Verify installation
pod --version
```

**Expected Output**:
```
1.15.x
```

---

## 🛠️ **STEP 3: CONFIGURE FLUTTER FOR iOS** (5 minutes)

### **1. Run Flutter Doctor**:

```bash
flutter doctor
```

**Expected Output** (after Xcode + CocoaPods installed):
```
[✓] Flutter
[✓] Xcode - develop for iOS and macOS
[✓] Chrome - develop for the web
[✓] VS Code
[✓] Connected device
[✓] Network resources
```

### **2. Accept iOS Licenses**:

```bash
flutter doctor --android-licenses  # Skip if no Android
sudo xcodebuild -license accept    # iOS license
```

---

## 🛠️ **STEP 4: CONFIGURE YOUR FLUTTER APP FOR iOS** (10 minutes)

### **1. Navigate to Flutter App**:

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app
```

### **2. Install iOS Dependencies**:

```bash
cd ios
pod install
cd ..
```

**Expected Output**:
```
Analyzing dependencies
Downloading dependencies
Installing Firebase... (and other pods)
Generating Pods project
Pod installation complete!
```

### **3. Update iOS Configuration**:

Edit `ios/Runner/Info.plist` to add required permissions:

```xml
<!-- Add these inside <dict> tag -->

<!-- Camera permission (for future photo logging) -->
<key>NSCameraUsageDescription</key>
<string>We need camera access to log meals via photos</string>

<!-- Photo library permission -->
<key>NSPhotoLibraryUsageDescription</key>
<string>We need photo library access to select meal photos</string>

<!-- Location permission (for geo-aware meal suggestions) -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>We use your location to suggest local, seasonal meals</string>

<!-- Notifications permission -->
<key>UIBackgroundModes</key>
<array>
    <string>remote-notification</string>
</array>
```

### **4. Update Bundle Identifier** (Important):

Edit `ios/Runner.xcodeproj/project.pbxproj` or open in Xcode:

1. Open Xcode
2. File → Open → Navigate to `flutter_app/ios/Runner.xcworkspace`
3. Select **Runner** in left sidebar
4. Under **General** → **Identity**:
   - **Bundle Identifier**: `com.yourcompany.productivityai` (change to your domain)
   - **Display Name**: `AI Productivity`
   - **Version**: `1.1.0`
   - **Build**: `1`

---

## 📱 **STEP 5: RUN ON iOS SIMULATOR** (5 minutes)

### **1. List Available Simulators**:

```bash
flutter devices
```

**Expected Output**:
```
4 connected devices:

iPhone 16 Pro (mobile)        • <UUID> • ios • com.apple.CoreSimulator.SimRuntime.iOS-18-1 (simulator)
iPhone 16 (mobile)            • <UUID> • ios • com.apple.CoreSimulator.SimRuntime.iOS-18-1 (simulator)
macOS (desktop)               • macos • darwin-arm64 • macOS 15.7.1
Chrome (web)                  • chrome • web-javascript • Google Chrome
```

### **2. Open iOS Simulator**:

```bash
open -a Simulator
```

Or in Xcode:
- **Xcode** → **Open Developer Tool** → **Simulator**

### **3. Run Your App**:

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app

# Run on simulator (auto-selects available simulator)
flutter run

# Or specify a specific simulator
flutter run -d "iPhone 16 Pro"
```

**Expected Output**:
```
Launching lib/main.dart on iPhone 16 Pro in debug mode...
Running pod install...
Running Xcode build...
✓ Built build/ios/Debug-iphonesimulator/Runner.app
Installing and launching...
Flutter run key commands.
r Hot reload. 🔥
R Hot restart.
h List all available interactive commands.
d Detach (terminate "flutter run" but leave application running).
c Clear the screen
q Quit (terminate the application on the device).
```

---

## 📱 **STEP 6: RUN ON YOUR PHYSICAL iPhone** (10 minutes)

### **1. Enable Developer Mode on iPhone**:

On your iPhone:
1. **Settings** → **Privacy & Security**
2. Scroll down → **Developer Mode**
3. Toggle **ON**
4. Restart iPhone

### **2. Connect iPhone to Mac**:

1. Connect iPhone via USB cable
2. On iPhone: Tap **"Trust This Computer"**
3. Enter iPhone passcode

### **3. Verify Device Connection**:

```bash
flutter devices
```

**Expected Output**:
```
5 connected devices:

Your iPhone (mobile) • <UUID> • ios • iOS 18.1.1 (physical device)
iPhone 16 Pro (mobile) • <UUID> • ios • (simulator)
...
```

### **4. Configure Signing in Xcode**:

1. Open Xcode:
   ```bash
   open ios/Runner.xcworkspace
   ```

2. Select **Runner** in left sidebar

3. Go to **Signing & Capabilities** tab

4. Under **Team**:
   - If you have Apple Developer account: Select your team
   - If not: Select your personal Apple ID (free provisioning)

5. Check **"Automatically manage signing"**

6. Xcode will create a provisioning profile

### **5. Run on iPhone**:

```bash
# Run on connected iPhone
flutter run -d <your-iphone-id>

# Or just run and select device
flutter run
# Then select your iPhone from the list
```

**First Time**: You'll need to trust the developer certificate on iPhone:
1. On iPhone: **Settings** → **General** → **VPN & Device Management**
2. Tap your Apple ID
3. Tap **"Trust"**
4. Go back and run app again

---

## 🎨 **WHAT YOU'LL SEE**

Your app will launch as a **native iOS app** with:

✅ **Native iOS UI**:
- iOS navigation gestures (swipe back)
- Native keyboard
- iOS status bar
- iOS animations

✅ **All Features Working**:
- Yuvi AI chat
- Meal planning
- Dashboard with quick-add buttons
- Water tracking
- Supplements
- Profile with Free Tier badge

✅ **Better Performance**:
- Faster than web version
- Smoother animations
- Native scrolling
- Better touch response

---

## 🐛 **TROUBLESHOOTING**

### **Issue: "No iOS devices found"**

**Solution**:
```bash
# Restart Flutter daemon
flutter devices
killall -9 dart
flutter devices
```

### **Issue: "CocoaPods not installed"**

**Solution**:
```bash
brew install cocoapods
cd ios
pod install
```

### **Issue: "Code signing error"**

**Solution**:
1. Open Xcode
2. Runner → Signing & Capabilities
3. Select your Apple ID under Team
4. Change Bundle Identifier to something unique

### **Issue: "Build failed"**

**Solution**:
```bash
# Clean and rebuild
flutter clean
cd ios
pod deintegrate
pod install
cd ..
flutter run
```

### **Issue: "Simulator not showing"**

**Solution**:
```bash
# Open Simulator manually
open -a Simulator

# Or via Xcode
# Xcode → Open Developer Tool → Simulator
```

---

## 📊 **DEVELOPMENT WORKFLOW**

### **Hot Reload** (Instant Updates):

While app is running:
- Press **`r`** in terminal → Hot reload (updates UI instantly)
- Press **`R`** in terminal → Hot restart (full restart)
- Press **`q`** in terminal → Quit

### **Debug Mode**:

```bash
# Run in debug mode (default)
flutter run

# Run in profile mode (better performance)
flutter run --profile

# Run in release mode (production-like)
flutter run --release
```

### **View Logs**:

```bash
# View Flutter logs
flutter logs

# View iOS system logs
xcrun simctl spawn booted log stream --predicate 'processImagePath contains "Runner"'
```

---

## 🎯 **TESTING CHECKLIST**

Once your app is running on iOS, test:

- [ ] Login/Signup flow
- [ ] Home screen displays correctly
- [ ] "How You're Leveling Up 🆙" panel visible
- [ ] Quick-add water button works (+250ml)
- [ ] Quick-add supplements button opens chat
- [ ] Meal plan generation works
- [ ] Plan selector shows multiple plans
- [ ] Recipe details display correctly
- [ ] Profile shows Free Tier badge
- [ ] Chat with Yuvi works
- [ ] Animations are smooth
- [ ] Native iOS gestures work (swipe back)

---

## 🚀 **NEXT STEPS AFTER SETUP**

Once you have iOS working locally:

1. **Test on simulator** - Quick iteration
2. **Test on real iPhone** - Real user experience
3. **Optimize for iOS** - Native feel
4. **Prepare for App Store** - When ready to publish

---

## 📝 **QUICK REFERENCE**

### **Common Commands**:

```bash
# Check setup
flutter doctor

# List devices
flutter devices

# Run on simulator
flutter run

# Run on specific device
flutter run -d <device-id>

# Hot reload
r (while running)

# Clean build
flutter clean

# Update pods
cd ios && pod install && cd ..
```

---

## ⏱️ **ESTIMATED TIME**

- **Xcode Installation**: 30-45 minutes (one-time)
- **CocoaPods Installation**: 5 minutes (one-time)
- **Flutter iOS Setup**: 10 minutes (one-time)
- **First Run**: 5-10 minutes (build time)
- **Subsequent Runs**: 30 seconds (hot reload)

---

## 💡 **PRO TIPS**

1. **Keep Simulator Open**: Faster subsequent runs
2. **Use Hot Reload**: Press `r` for instant updates
3. **Test on Real Device**: Better performance testing
4. **Enable Developer Mode**: On both Mac and iPhone
5. **Use Xcode for Debugging**: Better iOS-specific debugging

---

**Ready to start? Let me know when you've installed Xcode and I'll help you with the next steps!** 🚀


