# 🚀 Deploy NOW - Step by Step Guide

**Goal**: Deploy to web + test on iOS device  
**Time**: 30-45 minutes  
**Cost**: $0 (Free tier)

---

## ⚡ Quick Setup (5 minutes)

### **Step 1: Install Google Cloud SDK**

Open Terminal and run:

```bash
# Install gcloud
curl https://sdk.cloud.google.com | bash

# Restart terminal or run:
exec -l $SHELL

# Verify installation
gcloud --version
```

### **Step 2: Install Firebase CLI**

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Verify installation
firebase --version
```

### **Step 3: Login**

```bash
# Login to Google Cloud
gcloud auth login

# Login to Firebase
firebase login

# Set your project (use existing: productivityai-mvp)
gcloud config set project productivityai-mvp
```

---

## 🚀 Deploy Backend + Frontend (20 minutes)

### **Option A: Automated Deployment** (Recommended)

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity

# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The script will:
1. ✅ Build backend Docker image
2. ✅ Deploy to Cloud Run
3. ✅ Build Flutter web
4. ✅ Deploy to Firebase Hosting
5. ✅ Deploy Firestore rules
6. ✅ Give you the URLs

---

### **Option B: Manual Deployment** (If script fails)

#### **1. Deploy Backend**:

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity

# Build and deploy to Cloud Run
gcloud run deploy aiproductivity-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=productivityai-mvp" \
  --set-env-vars="OPENAI_MODEL=gpt-4o-mini" \
  --max-instances=1 \
  --memory=512Mi

# Get backend URL
gcloud run services describe aiproductivity-backend \
  --region us-central1 \
  --format='value(status.url)'
```

Copy the backend URL (e.g., `https://aiproductivity-backend-xxxxx-uc.a.run.app`)

#### **2. Update Flutter Config**:

```bash
# Edit constants file
nano flutter_app/lib/utils/constants.dart

# Change apiBaseUrl to your backend URL:
# static const String apiBaseUrl = 'https://your-backend-url';

# Save: Ctrl+O, Enter, Ctrl+X
```

#### **3. Deploy Frontend**:

```bash
cd flutter_app

# Build Flutter web
flutter build web --release

# Initialize Firebase (if not done)
firebase init hosting
# Select: productivityai-mvp
# Public directory: build/web
# Single-page app: Yes

# Deploy
firebase deploy --only hosting

# Get frontend URL
firebase hosting:channel:list
```

#### **4. Deploy Firestore Rules**:

```bash
cd ..
firebase deploy --only firestore:rules,firestore:indexes
```

---

## 🌐 Test on Web Browser (5 minutes)

### **1. Open Your App**:

Your app will be at:
```
https://productivityai-mvp.web.app
```

Or check with:
```bash
firebase hosting:channel:list
```

### **2. Test Scenarios**:

```
✅ Open app in browser
✅ Signup with new email (or use alice.test@aiproductivity.app / Test@123)
✅ Send: "I had oatmeal with banana for breakfast"
✅ Refresh page (Cmd+R) - chat should persist!
✅ Send: "For lunch I ate chicken, rice, and broccoli"
✅ Check timeline - should show 1 lunch log (not 3)
✅ Test on mobile browser (Safari/Chrome)
```

---

## 📱 Test on iOS Device (15 minutes)

### **Method 1: Web App (Fastest - 2 minutes)**

1. **Open Safari on iPhone**
2. **Go to**: `https://productivityai-mvp.web.app`
3. **Add to Home Screen**:
   - Tap Share button
   - Tap "Add to Home Screen"
   - Tap "Add"
4. **Test**: Opens like a native app!

---

### **Method 2: Native iOS App (20 minutes)**

#### **Build iOS App**:

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app

# Build iOS (debug mode for testing)
flutter build ios --debug --no-codesign

# Or build for device
flutter build ios --release
```

#### **Install on Device**:

**Option A: Via Xcode** (Recommended):

1. Open Xcode:
   ```bash
   open ios/Runner.xcworkspace
   ```

2. In Xcode:
   - Select your iPhone from device list
   - Click Run (▶️) button
   - App installs and launches on your iPhone

**Option B: Via TestFlight** (For sharing with others):

1. **Archive the app**:
   ```bash
   flutter build ipa
   ```

2. **Upload to App Store Connect**:
   - Open Xcode
   - Window > Organizer
   - Select archive
   - Click "Distribute App"
   - Choose "TestFlight"
   - Upload

3. **Invite testers**:
   - Go to App Store Connect
   - TestFlight tab
   - Add testers via email
   - They get link to install via TestFlight app

---

## 🐛 Troubleshooting

### **Issue: gcloud not found**

```bash
# Install gcloud
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### **Issue: Firebase not found**

```bash
npm install -g firebase-tools
```

### **Issue: Backend deployment fails**

```bash
# Check logs
gcloud builds log --stream

# Try with more memory
gcloud run deploy --memory=1Gi
```

### **Issue: Frontend not updating**

```bash
# Clear cache and rebuild
cd flutter_app
flutter clean
flutter build web --release
firebase deploy --only hosting --force
```

### **Issue: iOS build fails**

```bash
# Clean and rebuild
cd flutter_app
flutter clean
rm -rf ios/Pods ios/Podfile.lock
cd ios && pod install && cd ..
flutter build ios
```

### **Issue: "No provisioning profile"**

```bash
# Open Xcode
open ios/Runner.xcworkspace

# In Xcode:
# 1. Select Runner in left panel
# 2. Select "Signing & Capabilities" tab
# 3. Check "Automatically manage signing"
# 4. Select your Apple ID team
```

---

## ✅ Success Checklist

After deployment, verify:

- [ ] Backend URL is accessible: `curl https://your-backend-url/health`
- [ ] Frontend URL is accessible: Open in browser
- [ ] Login works
- [ ] Chat messages persist after refresh
- [ ] Meals log correctly (no duplicates)
- [ ] Timeline displays properly
- [ ] Web app works on iPhone Safari
- [ ] iOS app installs and runs (if built)

---

## 📊 Monitor Your Deployment

### **View Logs**:

```bash
# Backend logs
gcloud run services logs read aiproductivity-backend \
  --region us-central1 \
  --limit 50

# Follow logs in real-time
gcloud run services logs tail aiproductivity-backend \
  --region us-central1
```

### **Check Costs**:

```bash
# View billing
gcloud billing accounts list

# Check usage
gcloud run services describe aiproductivity-backend \
  --region us-central1
```

### **Monitor Performance**:

- Cloud Console: https://console.cloud.google.com/run
- Firebase Console: https://console.firebase.google.com
- Logs: Real-time in terminal

---

## 🎯 Quick Commands Reference

```bash
# Deploy everything
./deploy.sh

# Deploy backend only
gcloud run deploy aiproductivity-backend --source .

# Deploy frontend only
cd flutter_app && flutter build web && firebase deploy --only hosting

# View logs
gcloud run services logs read aiproductivity-backend --region us-central1

# Build iOS
cd flutter_app && flutter build ios

# Open in Xcode
open ios/Runner.xcworkspace
```

---

## 🎉 You're Live!

Once deployed, share with testers:

**Web App**: `https://productivityai-mvp.web.app`

**Test Credentials**:
- Email: `alice.test@aiproductivity.app`
- Password: `Test@123`

**Or create new account**: Any email + password

---

## 📱 iOS Testing Tips

### **Test on Physical Device**:
1. Connect iPhone via USB
2. Trust computer on iPhone
3. In Xcode, select your iPhone
4. Click Run

### **Test on Simulator**:
```bash
# List simulators
xcrun simctl list devices

# Run on simulator
flutter run -d "iPhone 15 Pro"
```

### **Share with Testers**:
- TestFlight (best for multiple testers)
- Direct install via Xcode (for you)
- Web app (works on all devices)

---

## 🚀 Next Steps

After successful deployment:

1. **Test thoroughly** on web + iOS
2. **Collect feedback** from testers
3. **Monitor costs** (should be $0)
4. **Check performance** (logs, metrics)
5. **Iterate** based on feedback

---

**Ready to deploy?** Run these commands in order:

```bash
# 1. Install tools (if needed)
curl https://sdk.cloud.google.com | bash
npm install -g firebase-tools

# 2. Login
gcloud auth login
firebase login

# 3. Deploy
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
chmod +x deploy.sh
./deploy.sh

# 4. Build iOS
cd flutter_app
flutter build ios
open ios/Runner.xcworkspace
```

**Let's go! 🚀**

